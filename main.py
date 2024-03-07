import pandas as pd
import json
from pprint import pprint, pformat
from g4f.client import Client
from g4f import Provider, ChatCompletion

import flet as ft


def complete_message(messages: list) -> ChatCompletion:
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        provider=Provider.Bing
    )
    messages.append({"role": response.choices[0].message.role, "content": response.choices[0].message.content})
    return response

def main(page: ft.Page):
    chat = ft.Column()
    new_message = ft.TextField()
    user = "userx"
    def send_click(e):
        chat.controls.append(ft.Column([ft.Row([ft.Icon(name=ft.icons.PERSON if user == "user" else ft.icons.ANALYTICS)]),
            ft.Text(new_message.value)]))

        new_message.value = ""
        page.update()

    page.add(
        chat, ft.Row(controls=[new_message, ft.ElevatedButton("Send", on_click=send_click)])
    )


ft.app(target=main, view=ft.AppView.WEB_BROWSER, name="Finanzanalyse")

if __name__ == "__main__":

    exit()
    message = []
    client = Client()
    df = pd.read_excel("Gewinn_und_Verlust.xlsx")
    pprint((table := df.iloc[4:14, 1:15].to_dict()))
    try:
        message.append({"role": "system", "content": "Hallo, ich bin ein Bot. Ich kann Ihnen bei Ihrer Finanzanalyse helfen und werde keine Emojis benutzen."})
        message.append({"role": "user", "content": json.dumps(table)})
        while True:
            response = complete_message(message)
            print(response.choices[0].message.content)
            message.append({"role": "user", "content": input("You: ")})
    except KeyboardInterrupt:
        print("Goodbye")

