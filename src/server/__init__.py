from src.tools.MPCustom import CustomImage
from src.tools.Medipy import Medipy
from http.server import SimpleHTTPRequestHandler, HTTPServer
import os

model = Medipy(show=True)
model.addModel('../tools/best.pt', 'en')


class MyServer(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def do_GET(self):
        # Handle GET request
        self.send_response(200)
        self.end_headers()
        model.process(self.path)
        self.wfile.write("Done!".encode())

    def do_POST(self):
        # Handle POST request
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print("Received POST data:", post_data.decode('utf-8'))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"This is a POST response")

if __name__=="__main__":
    print(f"Started at http://localhost:8000")
    HTTPServer(('localhost', 8000), MyServer).serve_forever()