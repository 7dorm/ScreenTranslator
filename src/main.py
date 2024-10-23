from server import RequestHandler
import http.server as hs

server = hs.HTTPServer(("localhost", 8080), RequestHandler)
server.serve_forever()
