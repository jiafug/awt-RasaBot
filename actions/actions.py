# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

# This is a simple example for a custom action which utters "Hello World!"

import csv
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

script_dir = os.path.dirname(__file__)  # <--- absolute dir the script is in


class ActionSetTopic(Action):
    def name(self) -> Text:
        return "action_set_topic"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # [short-name]: [long-name] mapping
        # dictionary of topics with their short and full name
        dict_topics = {
            "wohnung_anmelden": "Anmeldung einer Wohnung",
            "wohnung_abmelden": "Abmeldung einer Wohnung",
        }
        topic = None
        for event in tracker.events:
            if event["event"] == "user":
                usr_intent = event["parse_data"]["intent"]["name"]
                if "topic" in usr_intent:
                    topic = usr_intent.replace("topic_", "")
        topic = dict_topics[topic]
        date_time = datetime.now().strftime("%d/%b/%Y %H:%M:%S")
        print("[" + date_time + "]", " set topic slot to: ", topic)
        return [SlotSet("topic", topic)]


class ActionDefaultAskAffirmation(Action):
    """Asks for an affirmation of the intent if NLU threshold is not met."""

    def name(self) -> Text:
        return "action_default_ask_affirmation"

    def __init__(self) -> None:
        path = script_dir + "/intent_description_mapping.csv"
        reader = csv.reader(open(path, "r"))
        intent_mappings = {}
        for row in reader:
            k, v = row
            intent_mappings[k] = v
        self.intent_mappings = intent_mappings

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        intent_ranking = tracker.latest_message.get("intent_ranking", [])
        if len(intent_ranking) > 1:
            nlu_fallback_score = intent_ranking[0].get("confidence")
            next_best_score = intent_ranking[1].get("confidence")
            diff_intent_confidence = nlu_fallback_score - next_best_score
            # if the difference between the NLU threshold and the next best intent is less than 0.2
            # offer only the best intent as an option else offer the next 3 best intents as options
            if diff_intent_confidence < 0.2:
                intent_ranking = intent_ranking[:1]
            else:
                intent_ranking = intent_ranking[:3]
        # save intent names
        first_intent_names = [intent.get("name", "") for intent in intent_ranking]
        if "nlu_fallback" in first_intent_names:
            first_intent_names.remove("nlu_fallback")
        if "out_of_scope" in first_intent_names:
            first_intent_names.remove("out_of_scope")
        # buttons to show to the user
        buttons = []
        if len(first_intent_names) > 0:
            message_title = "Ich habe es nicht ganz verstanden. Meinten Sie..."
            entities = tracker.latest_message.get("entities", [])
            entities = {e["entity"]: e["value"] for e in entities}
            entities_json = json.dumps(entities)
            for intent in first_intent_names:
                try:
                    button_title = self.intent_mappings[intent]
                    buttons.append(
                        {"title": button_title, "payload": f"/{intent}{entities_json}"}
                    )
                except KeyError:
                    pass                
        # if there are buttons from the intent_description_mapping.csv file append a new button
        if len(buttons) >= 1:
            buttons.append({"title": "Etwas anders", "payload": "/anything_else"})
            dispatcher.utter_message(text=message_title, buttons=buttons)
        else:
            message_title = "Tut mir leid, ich habe es nicht verstanden. Können Sie es bitte umformulieren?"
            dispatcher.utter_message(text=message_title)
        return []
