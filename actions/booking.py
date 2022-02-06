import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

script_dir = os.path.dirname(__file__)  # <--- absolute dir the script is in
db = sqlite3.connect(script_dir + "/db.sqlite3")


class ActionResetSlotTime(Action):
    """Sets slotvalue of time to None"""

    def name(self):
        return "action_reset_slot_time"

    def run(self, dispatcher, tracker, domain):
        return [SlotSet("time", None)]


class ActionBookAppointment(Action):
    """Action to book an appointment."""

    def name(self) -> Text:
        return "action_book_appointment"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        appointment_id = tracker.slots["appointment_id"]
        name = tracker.slots["name"]
        phone = tracker.slots["phone-number"]
        mail = tracker.slots["email"]
        book_appointment(appointment_id, name, phone, mail)
        return []


class ActionFindAppointments(Action):
    """Finds available appointments for a given service topic, place and time combination."""

    def name(self) -> Text:
        # initializes database with its relations
        init_db()
        return "action_find_appointments"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        service_slot = tracker.slots["topic"]
        district_slot = tracker.slots["place"]
        date_slot = tracker.slots["time"]
        if isinstance(date_slot, dict):
            date_slot = date_slot["from"]
        requested_day = datetime.fromisoformat(date_slot).strftime("%d.%m.%Y")
        today, other = get_available_appointments(
            service_slot, district_slot, date_slot
        )
        buttons = []
        loop = None
        # show appointments of the requested day if there is at least one
        if len(today) >= 1:
            loop = today
        else:
            loop = other
        for entry in loop:
            date = datetime.fromisoformat(entry[1])
            full_date = date.strftime("%d.%m.%Y %H:%M") + " Uhr"
            # set entities directly through payload
            payload = str(
                {
                    "appointment_id": str(entry[0]),
                    "appointment_time": full_date,
                    "appointment_office": entry[2],
                    "appointment_street": entry[4],
                    "appointment_city": str(entry[5]) + " " + str(entry[6]),
                }
            ).replace("'", '"')
            button = {
                "title": full_date,
                "payload": "/booking_set_appointment" + payload,
            }
            buttons.append(button)
        new_search_button = {
            "title": "Ein anderer Zeitpunkt",
            "payload": "/booking_reject_appointment",
        }
        buttons.append(new_search_button)
        if len(today) >= 1:
            dispatcher.utter_button_message(
                "Für den " + requested_day + " konnte diese Termine finden:", buttons
            )
        else:
            dispatcher.utter_button_message(
                "Am "
                + requested_day
                + " sind leider keine Termine mehr verfügbar. Die nächsten Termine sind:",
                buttons,
            )
        date_time = datetime.now().strftime("%d/%b/%Y %H:%M:%S")
        print(
            "[" + date_time + "]",
            " found appointments: ",
            len(other),
            " for requested date: ",
            requested_day,
        )
        return []


def book_appointment(id, name, phone, mail):
    """Function for appointment booking.

    Args:
        id (str): id of appointment
        name (str): full name of user
        phone (str): phone number of user
        mail (str): e-mail of user
    """
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO bookings(appointment,name, phone, mail)
                  VALUES(?,?,?,?)""",
        (int(id), name, phone, mail),
    )
    db.commit()


def get_available_appointments(service_slot, district_slot, date_slot):
    """Function that finds appointments for given parameters.

    Args:
        service_slot (str): type of requested service
        district_slot (str): requested location
        date_slot ([type]): requested date of appointment

    Returns:
        tuple of available appointments for the requested day and next available appointments
    """
    cursor = db.cursor()
    sql = """
        SELECT appointments.id, appointments.date, offices.name, offices.district, 
            offices.street, offices.postcode, offices.ort, services.name , bookings.id
        FROM 'appointments' 
        LEFT JOIN 'bookings' 
            ON appointments.id = bookings.appointment
        LEFT JOIN 'offices' 
            ON appointments.office = offices.id 
        LEFT JOIN 'services' 
            ON appointments.service = services.id 
        WHERE offices.district=? 
            AND services.name=? 
            AND bookings.id IS NULL
            AND datetime(appointments.date)>=datetime(?)
        ORDER BY appointments.date
    """
    cursor.execute(sql, (district_slot, service_slot, date_slot))
    all_available = cursor.fetchall()
    # stores distinct time slots per day
    time_slots = []
    # stores available appointments
    available = []
    for entry in all_available:
        dt = datetime.fromisoformat(entry[1])
        # get hour and minute of available appointment
        t = [dt.year, dt.month, dt.day, dt.hour, dt.minute]
        if t not in time_slots:
            time_slots.append(t)
            available.append(entry)
            # limit to 3 appointment suggestions
            if len(available) == 3:
                break
    # get available time slots for today
    slot_date = datetime.fromisoformat(date_slot).date()
    today = [x for x in available if datetime.fromisoformat(x[1]).date() == slot_date]
    return today, available


def init_db():
    """Create empty tables."""
    cursor = db.cursor()
    # create relation for offices
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS offices(
            id INTEGER PRIMARY KEY,
            district TEXT,
            name TEXT,
            street TEXT,
            postcode INTEGER,
            ort TEXT
        )
    """
    )
    # create relation for services
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS services(
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    """
    )
    # create relation for appointments
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments(
            id INTEGER PRIMARY KEY,
            date TEXT,
            office INTEGER,
            service INTEGER,
            FOREIGN KEY(office) REFERENCES offices(id),
            FOREIGN KEY(service) REFERENCES services(id)
        )
    """
    )
    # create relation for bookings
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bookings(
            id INTEGER PRIMARY KEY,
            appointment INTEGER UNIQUE,
            name TEXT,
            phone TEXT,
            mail TEXT,
            FOREIGN KEY(appointment) REFERENCES appointments(id)
        )
    """
    )
    db.commit()


def create_toy_data():
    """Function which creates some toy data and commits those to the database."""
    cursor = db.cursor()
    # create data for offices
    offices = [
        (
            122210,
            "Charlottenburg-Wilmersdorf",
            "Bürgeramt Halemweg (Außenstelle)",
            "Halemweg 18",
            13627,
            "Berlin",
        ),
        (
            122217,
            "Charlottenburg-Wilmersdorf",
            "Bürgeramt Heerstraße",
            "Heerstr. 12",
            14052,
            "Berlin",
        ),
        (
            122219,
            "Charlottenburg-Wilmersdorf",
            "Bürgeramt Hohenzollerndamm",
            "Hohenzollerndamm 177",
            10713,
            "Berlin",
        ),
        (
            122227,
            "Charlottenburg-Wilmersdorf",
            "Bürgeramt Wilmersdorfer Straße",
            "Wilmersdorfer Straße 46",
            10627,
            "Berlin",
        ),
    ]
    cursor.executemany(
        """INSERT INTO offices(id, district, name, street, postcode, ort) VALUES(?,?,?,?,?,?)""",
        offices,
    )
    db.commit()
    # create data for services
    services = [
        (120335, "Abmeldung einer Wohnung"),
        (120686, "Anmeldung einer Wohnung"),
    ]
    cursor.executemany("""INSERT INTO services(id, name) VALUES(?,?)""", services)
    db.commit()
    # create data for appointments
    appointments = [
        ("2022-03-01 10:30:00", 122210, 120335),
        ("2022-03-01 11:30:00", 122210, 120335),
        ("2022-03-01 12:30:00", 122210, 120335),
        ("2022-03-01 13:30:00", 122210, 120686),
        ("2022-03-01 14:30:00", 122210, 120686),
        ("2022-03-01 15:30:00", 122210, 120686),
        ("2022-03-01 16:30:00", 122210, 120686),
        ("2022-03-01 17:30:00", 122217, 120335),
        ("2022-03-01 10:30:00", 122217, 120335),
        ("2022-03-01 11:30:00", 122217, 120335),
        ("2022-03-01 12:30:00", 122217, 120686),
        ("2022-03-01 13:30:00", 122217, 120686),
        ("2022-03-01 14:30:00", 122217, 120686),
        ("2022-03-01 15:30:00", 122219, 120686),
        ("2022-03-01 16:30:00", 122219, 120335),
        ("2022-03-01 17:30:00", 122219, 120335),
        ("2022-03-01 18:30:00", 122219, 120335),
        ("2022-03-01 10:30:00", 122219, 120686),
        ("2022-03-01 10:30:00", 122219, 120686),
        ("2022-03-01 12:30:00", 122227, 120686),
        ("2022-03-01 13:30:00", 122227, 120686),
        ("2022-03-01 14:30:00", 122227, 120335),
        ("2022-03-01 15:30:00", 122227, 120335),
    ]
    cursor.executemany(
        """INSERT INTO appointments(date, office, service) VALUES(?,?,?)""",
        appointments,
    )
    db.commit()


# create_toy_data()
