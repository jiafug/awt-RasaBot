import json
import os
import random
from http.server import BaseHTTPRequestHandler, HTTPServer

import yaml

from doc_store import DocumentStore

script_dir = os.path.dirname(__file__)  # <--- absolute dir the script is in
domain = os.path.join(script_dir, "../domain.yml")  # <--- rasa domain file
hostName = "localhost"
serverPort = 5054


class NLGServer(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self.send_error(405, "Method Not Allowed",
                        "Only HTTP POST is supported")

    def do_POST(self):
        if self.path == '/nlg':
            self._set_response()
            # length of request
            content_length = int(self.headers['Content-Length'])
            # body of request
            post_data = self.rfile.read(content_length).decode("utf-8")
            # get current topic
            topic, action = NLGServer.parse_rasa_request(post_data)
            if "qa" in action:
                # q&a response from document store
                pass
            else:
                # get static response
                response_txt = NLGServer.get_static_bot_response(action)
            # create rasa response
            response = NLGServer.create_rasa_response(response_txt)
            # write response
            self.wfile.write(bytes(json.dumps(response), 'utf-8'))
        else:
            self.send_error(404, "Not Found", "Please use the '/nlg' endpoint")

    @staticmethod
    def parse_rasa_request(data):
        request = json.loads(data)
        action = request['response']
        events = request['tracker']['events']
        return "", action

    @staticmethod
    def get_static_bot_response(action):
        with open(domain, 'r') as stream:
            data_loaded = yaml.safe_load(stream)
            # get a list of all responses for a specific action
            text_list = data_loaded['responses'][action]
            # pick a random respone
            rand_res = random.choice(text_list)
            return rand_res['text']

    @staticmethod
    def create_rasa_response(response_txt):
        json_response = {
            "text": response_txt,
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
