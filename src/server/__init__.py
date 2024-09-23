import http.server as hs
import urllib.parse
import os
import uuid
class RequestHandler(hs.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200) # Here is an implementation of get request (cant continue due to no files)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Hello, World!')
        return

    def do_POST(self):
        # Check if the request contains an image (Content-Type header should indicate this)
        content_type = self.headers.get('Content-Type')
        print("Request headers:", dict(self.headers))

        if (content_type and 'images/' in content_type):  # This includes images, thus we proceed
            # Get image data from request body
            length = int(self.headers['Content-Length'])
            body = self.rfile.read(length)
            image_name = uuid.uuid4()
            image_type = content_type.split('/')[-1]
            # Save the received image to disk
            with open(f'{image_name}.' + image_type, 'wb') as image_file:
                image_file.write(body)

            print(f"Image saved to {os.getcwd()}/{image_name}.{image_type}")
            print(image_name)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str(image_name).encode('utf-8'))
        else:
            self.send_response(400)  # Bad Request, we can't handle it
            self.end_headers()

        return


    def do_PUT(self):
        print("Request headers:", dict(self.headers))
        self.send_response(200)
        return
