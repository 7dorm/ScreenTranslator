import http.server as hs
import urllib.parse
import threading
import json
import uuid
import os

from tools import find_file_by_name, detect

class RequestHandler(hs.BaseHTTPRequestHandler):
    def do_GET(self):
        if 'uuid' in self.path:

            self.curr_uuid = uuid.UUID(self.path[7:].split('%20%22')[-1].split('.')[0])
            print(self.curr_uuid)


            if a := find_file_by_name(os.getcwd() + '/runs', self.curr_uuid):
                with open(a, "rb") as f:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/octet-stream")
                    self.send_header("Content-Length", os.path.getsize(a))
                    self.end_headers()
                    while chunk := f.read(8192):  # Read and send the file in chunks
                        self.wfile.write(chunk)
                        self.wfile.flush()  # Force flush after each chunk
                    os.system(f'rm -rf {self.curr_uuid}.{a.split(".")[-1]}')
            else:
                self.send_response(201)
        return

    def do_POST(self):
        # Check if the request contains an image (Content-Type header should indicate this)
        content_type = self.headers.get('Content-Type')
        print("Request headers:", dict(self.headers))

        if content_type and 'image/' in content_type:  # Check for an image
            try:
                # Get image data from request body
                length = int(self.headers['Content-Length'])
                body = self.rfile.read(length)
                image_uuid = uuid.uuid4()
                image_type = content_type.split('/')[-1]

                # Save the received image to disk
                image_filename = f"{image_uuid}.{image_type}"
                with open(image_filename, 'wb') as image_file:
                    image_file.write(body)

                print(f"Image saved to {os.getcwd()}/{image_filename}")

                # Send JSON response with uuid and name
                response_data = {
                    "uuid": str(image_uuid),
                    "name": image_filename
                }

                self.send_response(200)  # Success
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

                self.wfile.write(json.dumps(response_data).encode('utf-8'))

                # Optional: Call the detect function here
                threading.Thread(target=detect, args=[os.path.join(os.getcwd(), image_filename)]).start()

            except Exception as e:
                # Handle errors (e.g., invalid Content-Length or file writing failure)
                print(f"Error handling POST request: {e}")
                self.send_response(500)  # Internal Server Error
                self.end_headers()
                self.wfile.write(b"Internal Server Error")
        else:
            # Bad request: Content-Type not an image
            self.send_response(400)  # Bad Request
            self.end_headers()
            self.wfile.write(b"Unsupported Content-Type")

        return

import yaml

# Load the YAML file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
    
# Accessing data
print(">", config['data'])
