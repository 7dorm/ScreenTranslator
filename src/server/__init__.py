import http.server as hs
import urllib.parse


class RequestHandler(hs.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Hello, World!')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        params = urllib.parse.parse_qs(body.decode('utf-8'))
        print(params)
        self.send_response(200)
        self.end_headers()
        return
