# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ActionExecuted, EventType, SessionStarted, SlotSet
from rasa_sdk.executor import CollectingDispatcher
import time


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


class ActionHumanFallback(Action):
    def name(self) -> Text:
        return "action_trigger_human_fallback"

    @staticmethod
    def fetch_slots(tracker: Tracker) -> List[EventType]:
        """Collect slots that contain the user's name and phone number."""

        slots = []
        for key in ("name", "phone_number"):
            value = tracker.get_slot(key)
            if value is not None:
                slots.append(SlotSet(key=key, value=value))
        return slots

    async def run(self, dispatcher, tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # the session should begin with a `session_started` event
        #events = [SessionStarted()]

        # any slots that should be carried over should come after the
        # `session_started` event
        #events.extend(self.fetch_slots(tracker))

        # an `action_listen` should be added at the end as a user message follows
        #events.append(ActionExecuted("action_listen"))

        dispatcher.utter_message(text="Hello World!" + str(tracker.slots))

        return []
