from nicegui import app, ui
from fastapi import Response
from fastapi.responses import PlainTextResponse
import utils
import ui_utils


@app.get('/conversation_id', response_class=PlainTextResponse)
def conversation_id(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return ui_utils.conversation_id

ui.dark_mode().enable()
ui.query('.nicegui-content').classes('pt-5 pb-5 pr-10 pl-10')

with ui.row().classes('w-full'):
    tailwind = f'mb-2 h-auto break-inside-avoid'
    with ui.element("div").classes(tailwind).classes("w-7/12"):
        with ui.row().classes('w-full items-end'):
            ui.markdown(f'## Conversation log')
            ui.space()
            ui.label(f'Avatar status: ').classes('pb-3')
            ui_utils.furhat_status()
        ui_utils.messages()
        ui_utils.patient_control_buttons()
        ui.markdown(f"## Immediate feedback")
        with ui.card():
            ui_utils.feedback()
    ui.space()
    with ui.element("div").classes(tailwind).classes("w-2/6"):
        ui_utils.form()

app.on_startup(utils.consumer)
app.on_startup(ui_utils.fresh_feedback_dialog)
app.on_startup(ui_utils.fresh_debug_dialog)
app.on_startup(ui_utils.fresh_patient_dialog)
app.on_connect(ui_utils.messages_scroll_to_bottom)
ui.add_css('''
pre {
    white-space: pre-wrap;       /* Since CSS 2.1 */
    white-space: -moz-pre-wrap;  /* Mozilla, since 1999 */
    white-space: -pre-wrap;      /* Opera 4-6 */
    white-space: -o-pre-wrap;    /* Opera 7 */
    word-wrap: break-word;       /* Internet Explorer 5.5+ */
}
''')
ui.run(port=8501, show=False)