import pandas as pd
import json
import os
from g4f.client import Client
from g4f import Provider, ChatCompletion

import flet as ft
from flet import FilePicker, FilePickerUploadFile

os.environ["FLET_SECRET_KEY"] = "0"


def complete_message(messages: list, client) -> ChatCompletion:
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        provider=Provider.Bing
    )
    messages.append({"role": response.choices[0].message.role, "content": response.choices[0].message.content})
    return response


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.ALWAYS
    chat = ft.Column(scroll=ft.ScrollMode.ALWAYS)
    new_message = ft.TextField()
    client = Client()
    message_conv = [{"role": "system", "content": "Hallo, ich bin ein Bot. Ich kann Ihnen bei Ihrer Finanzanalyse helfen, ich werde keine Emojis benutzen und verwende markdown in utf-8."}]

    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    page.update()

    def on_dialog_result(e: ft.FilePickerResultEvent):
        global xlsx_file
        print("Selected files:", e.files)
        xlsx_file = e.files[0].name
        upload_list = []
        if file_picker.result != None and file_picker.result.files != None:
            for f in file_picker.result.files:
                upload_list.append(
                    FilePickerUploadFile(
                        f.name,
                        upload_url=page.get_upload_url(f.name, 600),
                    )
                )
            file_picker.upload(upload_list)

    def upload_files(e):
        file_picker.pick_files(allow_multiple=False, allowed_extensions=["xlsx", "xls"])

    def add_table(table_file, area: tuple[str, str, str, str]) -> None:
        print(table_file, area)
        df = pd.read_excel(".\\uploads\\" + table_file)
        table_dict = df.iloc[int(area[0]):int(area[1]), int(area[2]):int(area[3])].to_dict()
        message_conv.append({"role": "user", "content": json.dumps(table_dict)})

        chat.controls.append(ft.Column([ft.Row(
            [ft.Icon(name=ft.icons.PERSON),
             ft.Text(value="Du")]),
            ft.Container(
                content=ft.Text(f"Tabelle {table_file} eingefügt."), width=900
            )], wrap=True))
        table_response = get_response(message_conv)
        send.disabled = False
        chat.controls.append(ft.Column([ft.Row(
            [ft.Icon(name=ft.icons.ANALYTICS),
             ft.Text(value="Finanz Bot")]),
            ft.Container(
                content=ft.Markdown(
                    table_response,
                    selectable=True,
                    extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                    on_tap_link=lambda e: page.launch_url(e.data),
                ), width=900
            )
            ], wrap=True))
        page.update()

    def add_table_e(e):
        add_table(xlsx_file, (area_0.value,area_1.value, area_2.value, area_3.value))

    def get_response(conv) -> str:
        up.disabled = True
        paste.disabled = True
        page.update()
        try:
            api_response = complete_message(conv, client)
        except Exception as e:
            print(e)
            up.disabled = False
            paste.disabled = False
            page.update()
            return f"Entschuldigung, ich konnte Ihre Anfrage nicht verarbeiten.\nFehler: {e}"

        up.disabled = False
        paste.disabled = False
        page.update()
        return api_response.choices[0].message.content

    def send_click(e):
        chat.controls.append(ft.Column([ft.Row(
            [ft.Icon(name=ft.icons.PERSON),
             ft.Text(value="Du")]),
            ft.Container(content=ft.Markdown(
                        new_message.value,
                        selectable=True,
                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                        on_tap_link=lambda e: page.launch_url(e.data),
                    ), width=900)]))
        message_conv.append({"role": "user", "content": new_message.value})
        new_message.value = ""
        send.disabled = True
        page.update()
        bot_response = get_response(message_conv)
        chat.controls.append(ft.Column([ft.Row(
            [ft.Icon(name=ft.icons.ANALYTICS),
             ft.Text(value="Finanz Bot")]),
            ft.Container(
                content=ft.Markdown(
                        bot_response,
                        selectable=True,
                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                        on_tap_link=lambda e: page.launch_url(e.data),
                    ), width=900
            )], wrap=True))
        send.disabled = False
        page.update()


    page.add(
        chat, ft.Row(controls=[new_message, (send := ft.ElevatedButton("Senden", on_click=send_click)),
                               (up := ft.ElevatedButton("Upload", on_click=upload_files)),
                               (file_picker := ft.FilePicker(on_result=on_dialog_result)),
                               (area_0 := ft.TextField("4",keyboard_type=ft.KeyboardType.NUMBER)),
                               (area_1 := ft.TextField("14", keyboard_type=ft.KeyboardType.NUMBER)),
                               (area_2 := ft.TextField("1", keyboard_type=ft.KeyboardType.NUMBER)),
                               (area_3 := ft.TextField("15", keyboard_type=ft.KeyboardType.NUMBER)),
                               (paste := ft.ElevatedButton("Einfügen", on_click=add_table_e))])
    )
    send.disabled = True
    chat.controls.append(ft.Column([ft.Row(
        [ft.Icon(name=ft.icons.ANALYTICS),
         ft.Text(value="Finanz Bot")]),
        ft.Text("Bitte laden Sie eine Tabelle hoch und geben Sie den Bereich an, den Sie analysieren möchten.")]))
    page.update()



ft.app(target=main, view=ft.AppView.WEB_BROWSER, name="Finanzanalyse", upload_dir="uploads")

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

