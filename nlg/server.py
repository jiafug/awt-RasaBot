import json
import os
import random
import re
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

import yaml

from doc_store import DocumentStore

script_dir = os.path.dirname(__file__)  # <--- absolute dir the script is in
domain = os.path.join(script_dir, "../domain.yml")  # <--- rasa domain file
hostName = "localhost"
serverPort = 5054
doc_store = None


class NLGServer(BaseHTTPRequestHandler):
    def _set_response(self):
        """Sets the responds header."""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_GET(self):
        """Sends info that only POST is supported."""
        self.send_error(405, "Method Not Allowed", "Only HTTP POST is supported")

    def do_POST(self):
        """Main handler where requests are received and responses are created."""
        if self.path == "/nlg":
            self._set_response()
            # length of request
            content_length = int(self.headers["Content-Length"])
            # body of request
            post_data = self.rfile.read(content_length).decode("utf-8")
            # get current topic
            topic, question, action, slots = NLGServer.parse_rasa_request(post_data)
            if "qa" in action and topic != None:
                # q&a response from document store
                response_txt = doc_store.get_answer(question, topic)
            else:
                # get static response
                response_txt = NLGServer.get_static_bot_response(action, slots)
            # create rasa response
            response = NLGServer.create_rasa_response(response_txt)
            # write response
            self.wfile.write(bytes(json.dumps(response), "utf-8"))
        else:
            self.send_error(404, "Not Found", "Please use the '/nlg' endpoint")

    @staticmethod
    def parse_rasa_request(data):
        """Parses the request body provied by Rasa core.

        Args:
            data (str): rasa request body

        Returns:
            str: identifier of action to be taken
        """
        request = json.loads(data)
        # extract the next action
        action = request["response"]
        # extract last user message
        last_message = request["tracker"]["latest_message"]["text"]
        # extract last topic
        events = request["tracker"]["events"]
        topic = None
        for event in events:
            if event["event"] == "user":
                usr_intent = event["parse_data"]["intent"]["name"]
                if "topic" in usr_intent:
                    topic = usr_intent.replace("topic_", "")
        # extract all slots and last intent
        slots = request["tracker"]["slots"]
        intent = request["tracker"]["latest_message"]["intent"]["name"]
        intent_confi = request["tracker"]["latest_message"]["intent"]["confidence"]
        # logging
        date_time = datetime.now().strftime("%d/%b/%Y %H:%M:%S")
        print(
            "[" + date_time + "]",
            " topic: ",
            topic,
            " action: ",
            action,
            " last_message: ",
            last_message,
            " intent: ",
            intent,
            "(" + str(intent_confi) + ")",
        )
        return topic, last_message, action, slots

    @staticmethod
    def get_static_bot_response(action, slot):
        """Resturns a randomized static response which was defined in the Rasa domain.

        Args:
            action (str): action identifier

        Returns:
            str: static response
        """
        with open(domain, "r") as stream:
            data_loaded = yaml.safe_load(stream)
            # get a list of all responses for a specific action
            text_list = data_loaded["responses"][action]
            # pick a random respone
            rand_res = random.choice(text_list)["text"]
        # get all slot placeholders from response string
        placeholders = re.findall("{(.*?)}", rand_res)
        # replace all placeholders with their slot values
        for placeholder in placeholders:
            slot_val = slot[placeholder]
            pattern = "{" + placeholder + "}"
            rand_res = rand_res.replace(pattern, slot_val)
        return rand_res

    @staticmethod
    def create_rasa_response(response_txt):
        """Builds a JSON object to be returned to Rasa core.

        Args:
            response_txt (str): response

        Returns:
            dict: dict object
        """
        json_response = {
            "text": response_txt,
            "buttons": [],
            "image": None,
            "elements": [],
            "attachments": [],
            "custom": {},
        }
        return json_response


if __name__ == "__main__":
    """Starts the NLG server."""
    print("Initialize Q&A transformer model...")
    doc_store = DocumentStore()
    webServer = HTTPServer((hostName, serverPort), NLGServer)
    print("Server started http://%s:%s" % (hostName, serverPort))
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()
    print("Server stopped.")
