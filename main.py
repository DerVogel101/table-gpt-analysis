import pandas as pd
import json
import os
from g4f.client import Client
from g4f import Provider, ChatCompletion

import flet as ft
from flet import FilePicker, FilePickerUploadFile

os.environ["FLET_SECRET_KEY"] = "0"  # Required for FilePicker to work


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
    page_width = page.width
    new_message = ft.TextField(multiline=True, label="Nachricht")
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
        paste.disabled = False
        page.update()

    def add_table(table_file, area: tuple[str, str, str, str]) -> None:
        print(table_file, area)
        df = pd.read_excel(".\\uploads\\" + table_file)
        table_dict = df.iloc[int(area[0]):int(area[1]), int(area[2]):int(area[3])].to_dict()
        message_conv.append({"role": "user", "content": json.dumps(table_dict)})

        chat.controls.append(ft.Column([ft.Row(
            [ft.Icon(name=ft.icons.PERSON),
             ft.Text(value="Du")]),
            ft.Container(
                content=ft.Text(f"Tabelle {table_file} eingefügt."), width=page_width // 2
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
                ), width=page_width // 2
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
                    ), width=page_width // 2)]))
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
                    ), width=page_width // 2
            )], wrap=True))
        send.disabled = False
        page.update()


    page.add(
        ft.Row(controls=[ft.Column(controls=[ft.Container(content=chat, width=page_width // 2 + 50, border=ft.border.all(1), padding=15),
            ft.Row(controls=[new_message, (send := ft.ElevatedButton("Senden", on_click=send_click)),
                             (paste := ft.ElevatedButton("Einfügen", on_click=add_table_e)),
                             (up := ft.ElevatedButton("Upload", on_click=upload_files)),
                             (file_picker := ft.FilePicker(on_result=on_dialog_result)),
                             ]),
            ft.Column(controls=[
                ft.Row(controls=[ft.Text("Zeilenbereich:"), (area_0 := ft.TextField("4", keyboard_type=ft.KeyboardType.NUMBER, dense=True, label="von Zeile")),
                                 (area_1 := ft.TextField("14", keyboard_type=ft.KeyboardType.NUMBER, dense=True, label="bis Zeile"))]),
                ft.Row(controls=[ft.Text("Spaltenbereich:"), (area_2 := ft.TextField("1", keyboard_type=ft.KeyboardType.NUMBER, dense=True, label="von Spalte")),
                                 (area_3 := ft.TextField("15", keyboard_type=ft.KeyboardType.NUMBER, dense=True, label="bis Spalte"))]),
            ]),
        ])], alignment=ft.MainAxisAlignment.CENTER),
    )
    send.disabled = True
    paste.disabled = True
    chat.controls.append(ft.Column([ft.Row(
        [ft.Icon(name=ft.icons.ANALYTICS),
         ft.Text(value="Finanz Bot")]),
        ft.Text("Bitte laden Sie eine Tabelle hoch und geben Sie den Bereich an, den Sie analysieren möchten.\n"
                "Dann können Sie Einfügen drücken")]))
    page.update()


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, name="Finanzanalyse", upload_dir="uploads")
