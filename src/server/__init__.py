import http.server as hs
import urllib.parse
import uuid
import os
from tools import find_file_by_name


class RequestHandler(hs.BaseHTTPRequestHandler):
    tmp = False

    def ready(self, id: uuid.UUID):
        if (self.tmp):
            return 1
        return 0

    def do_GET(self):

        if 'uuid' in self.path:
            self.curr_uuid = uuid.UUID(self.path[7:])
            if (self.ready(self.curr_uuid)):
                image_type = 'image/'
                if a := find_file_by_name(os.getcwd(), self.curr_uuid):
                    image_type += a.splti('.')[-1]
                    self.send_header('Content-type', image_type)
                    self.end_headers()
                    with open(a, "rb") as f:
                        self.wfile.write(f.read())
                self.send_response(200)
            else:
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.send_response(201)
            self.wfile.write(b"Cunt!")
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

    def do_DELETE(self):
        self.tmp = True
        self.send_response(200)
        return
