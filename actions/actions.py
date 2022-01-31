# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

# This is a simple example for a custom action which utters "Hello World!"

from datetime import datetime
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher


class ActionHelloWorld(Action):
    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        buttons = [{
            "title": "Button 1",
            "payload": "/goodbye"
        }, {
            "title": "Button 2",
            "payload": "/goodbye"
        }]
        dispatcher.utter_button_message("Here are two buttons:", buttons)

        return []


class ActionSetTopic(Action):
    def name(self) -> Text:
        return "action_set_topic"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # [short-name]: [long-name] mapping
        # dictionary of topics with their short and full name
        dict_topics = {
            "wohnung_anmelden": "Anmeldung einer Wohnung",
            "wohnung_abmelden": "Abmeldung einer Wohnung"
        }
        topic = None
        for event in tracker.events:
            if event['event'] == 'user':
                usr_intent = event['parse_data']['intent']['name']
                if 'topic' in usr_intent:
                    topic = usr_intent.replace('topic_', '')
        topic = dict_topics[topic]
        date_time = datetime.now().strftime("%d/%b/%Y %H:%M:%S")
        print('[' + date_time + ']', ' set topic slot to: ', topic)
        return [SlotSet("topic", topic)]
