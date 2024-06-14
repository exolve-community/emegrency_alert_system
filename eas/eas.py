"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
import requests

from dotenv import dotenv_values

config = dotenv_values(".env")

EXOLVE_APP_API_KEY = config["EXOLVE_APP_API_KEY"]
EXOLVE_SENDER_NUMBER = config["EXOLVE_SENDER_NUMBER"]


class State(rx.State):
    """The app state."""

    phone_number_list_raw: str = ""
    important_information: str = ""
    emergency_type: str = ""
    degree_of_danger: str = ""

    response_message: str = ""

    def on_phone_numbers_list_change(self, list_raw: str):
        self.phone_number_list_raw = list_raw

    def on_important_information_text_change(self, important_information: str):
        self.important_information = important_information

    def on_type_of_emergency_change(self, emergency_type: str):
        self.emergency_type = emergency_type

    def on_degree_of_danger_change(self, degree_of_danger: str):
        self.degree_of_danger = degree_of_danger

    def send_sms(self):
        if not self.emergency_type:
            self.response_message = "Please select the type of emergency"
            return

        if not self.degree_of_danger:
            self.response_message = "Please select the degree of danger"
            return

        if not self.phone_number_list_raw:
            self.response_message = "Please enter phone numbers"
            return

        phone_numbers = self.phone_number_list_raw.strip().split()

        for number in phone_numbers:
            print(number)
            r = requests.post(
                "https://api.exolve.ru/messaging/v1/SendSMS",
                json={
                    "number": "79884857254",
                    "destination": number,
                    "text": f"🚨 {self.emergency_type} Alert 🚨\n\n"
                    f"Degree of danger: {self.degree_of_danger}\n\n"
                    f"{self.important_information}",
                },
                headers={"Authorization": f"Bearer {EXOLVE_APP_API_KEY}"},
            )
            if "message_id" not in r.json():
                self.response_message = f"Error sending SMS: {r.json()}"
                return

        self.response_message = "SMS sent!"


def index() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("🛟 Emergency Alert System", size="9"),
            rx.heading("Emergency SMS Sender"),
            rx.flex(
                rx.select(
                    ["Flood", "Landslide", "Tornado", "Storm", "Hurricane"],
                    placeholder="Type of emergency",
                    on_change=State.on_type_of_emergency_change,
                ),
                rx.select(
                    ["High", "Medium", "Low"],
                    placeholder="Degree of danger",
                    on_change=State.on_degree_of_danger_change,
                ),
                spacing="2",
                width="100%",
            ),
            rx.text_area(
                placeholder="Enter phone numbers line by line in format like 79524567893",
                width="100%",
                auto_height=True,
                on_change=State.on_phone_numbers_list_change,
            ),
            rx.text_area(
                placeholder="Enter important information (optional)",
                width="100%",
                on_change=State.on_important_information_text_change,
            ),
            rx.button("Send", on_click=State.send_sms),
            rx.text(State.response_message),
            spacing="5",
            justify="center",
            min_height="85vh",
        ),
    )


app = rx.App(
    telemetry_enabled=False,
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="large",
        accent_color="red",
    ),
)
app.add_page(index)
