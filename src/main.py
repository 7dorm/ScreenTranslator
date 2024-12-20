from server import RequestHandler
import http.server as hs

server = hs.HTTPServer(("localhost", 8080), RequestHandler)
server.serve_forever()

# fprintf(command, "curl -X POST -v http://localhost:8080/ -H 'Content-Type: images/%s' -T %s", type, path_to_file) // Send image. Returns uuid
# fprintf(command, "curl -X PUT -v http://localhost:8080/ -H 'Content-Type: application/json' -T {\"uuid\":%s, \"text\":%s}", uuid, text) // Send feedback. Retuns status_code
# fprintf(command, "curl -X GET -v http://localhost:8080/ -H 'Content-Type: application/text' -t Hello!") // WTF?

