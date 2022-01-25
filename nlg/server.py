import json
from http.server import BaseHTTPRequestHandler, HTTPServer

hostName = "localhost"
serverPort = 5054


class NLGServer(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        if self.path == '/nlg':
            self._set_response()
            self.wfile.write(
                bytes(
                    "<html><head><title>https://pythonbasics.org</title></head>",
                    "utf-8"))
        else:
            self.send_error(404, "not found",
                            "please use the './nlg' endpoint")

    def do_POST(self):
        if self.path == '/nlg':
            self._set_response()
            content_length = int(
                self.headers['Content-Length'])  # <--- Gets the size of data
            post_data = self.rfile.read(content_length).decode(
                "utf-8")  # <--- Gets the data itself
            topic = NLGServer.parse_rasa_request(post_data)
            response = NLGServer.get_rasa_response(topic)
            self.wfile.write(bytes(json.dumps(response), 'utf-8'))
        else:
            self.send_error(404, "not found",
                            "please use the './nlg' endpoint")

    @staticmethod
    def parse_rasa_request(data):
        request = json.loads(data)
        response = request['response']
        events = request['tracker']['events']
        print(events)
        return ""

    @staticmethod
    def get_rasa_response(topic):
        json_response = {
            "text": "Some text",
            "buttons": [],
            "image": None,
            "elements": [],
            "attachments": [],
            "custom": {}
        }
        return json_response


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), NLGServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
