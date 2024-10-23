import http.server as hs
import urllib.parse
import os

class RequestHandler(hs.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
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

            # Save the received image to disk
            with open('received_image.' + content_type.split('/')[-1], 'wb') as image_file:
                image_file.write(body)

            print(f"Image saved to {os.getcwd()}/received_image.{content_type.split('/')[-1]}")
            self.send_response(200)
        else:
            self.send_response(400)  # Bad Request, we can't handle it
            self.end_headers()

        return


    def do_PUT(self):
        print("Request headers:", dict(self.headers))
        self.send_response(200)
        return
