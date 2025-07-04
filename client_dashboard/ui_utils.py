from nicegui import ui
from nicegui.element import Element
from nicegui.elements.chat_message import ChatMessage
from nicegui.elements.dialog import Dialog
from nicegui.elements.notification import Notification
import utils
import asyncio

"""
Package that contains all the UI utilities for the application.
Can in principle be swapped with another UI library while keeping the function signatures.
"""

###
# Stateful UI components
###

_generation_progress_notification : Notification = None
_server_connection_notification : Notification = None
_furhat_connection_notification : Notification = None
_messages_container : Element = None
_messages_scroll_container : Element = None
_last_form_values = {
    "disease_difficulty": 6,
    "neuroticism": 1,
    "extraversion": 4,
    "openness": 4,
    "agreeableness": 4,
    "conscientiousness": 4
}
_open_debug_dialog_button_shown = False
_open_patient_information_button_shown = False
_message_skeleton : ChatMessage = None

# The conversation ID is used to identify the conversation in the server.
# Used in the UI but for clarity kept in main.
conversation_id : str = None

# The feedback dialog gets initialized in main.py using the fresh_feedback_dialog function.
_dialog_dialog : Dialog = ui.dialog().props("position=top")
_dialog_conversation_feedback_content = None
_dialog_clinical_feedback_content = None
_debug_dialog : Dialog = ui.dialog()
_debug_dialog_content = None
_patientinfo_dialog : Dialog = ui.dialog()
_patientinfo_content = None

###
# Direct UI Components and Refreshables
###

@ui.refreshable
def form(disabled: bool = True):
    ui.markdown(f'### Disease parameters')
    with ui.element('div').classes('flex gap-20 w-full no-wrap'):
        with ui.element("div").classes("w-1/2"):
            ui.label("Disease difficulty")
            disease_difficulty = ui.slider(min=1, max=10, value=_last_form_values["disease_difficulty"]).props('label-always switch-label-side snap markers :markers="1,10" marker-labels')
    ui.markdown(f'### Patient personality parameters')
    with ui.element('div').classes('flex gap-20 w-full no-wrap pr-5'):
        with ui.element("div").classes("w-1/2"):
            ui.label("Neuroticism")
            neuroticism = ui.slider(min=0, max=5, value=_last_form_values["neuroticism"]).props('label-always switch-label-side snap markers :markers="0,5" marker-labels')
            ui.label("Extraversion").classes("mt-5")
            extraversion = ui.slider(min=0, max=5, value=_last_form_values["extraversion"]).props(
                'label-always switch-label-side snap markers :markers="0,5" marker-labels')
            ui.label("Openness").classes("mt-5")
            openness = ui.slider(min=0, max=5, value=_last_form_values["openness"]).props(
                'label-always switch-label-side snap markers :markers="0,5" marker-labels')
        with ui.element("div").classes("w-1/2"):
            ui.label("Agreeableness")
            agreeableness = ui.slider(min=0, max=5, value=_last_form_values["agreeableness"]).props('label-always switch-label-side snap markers :markers="0,5" marker-labels')
            ui.label("Conscientiousness").classes("mt-5")
            conscientiousness = ui.slider(min=0, max=5, value=_last_form_values["conscientiousness"]).props(
                'label-always switch-label-side snap markers :markers="0,5" marker-labels')
    with ui.element('div').classes('flex flex-row gap-4 w-full'):
        with ui.element("div"):
            submit_button = ui.button('Generate patient', on_click=lambda: [
                update_last_form_values(disease_difficulty.value, neuroticism.value, extraversion.value,
                                        openness.value, agreeableness.value, conscientiousness.value),
                _start_patient_generation_ui(),
                utils.generate_patient(disease_difficulty.value, neuroticism.value, extraversion.value,
                                       openness.value, agreeableness.value, conscientiousness.value)]).classes(
                'mt-5')
        with ui.element("div"):
            open_debug_dialog_button(override=False, shown=False)

        with ui.element("div"):
            prefablaunchbutton = ui.dropdown_button('Launch predef. patient', auto_close=True, color='accent').classes('mt-5')
            with prefablaunchbutton:
                ui.item('Eleanor Vance, 68', on_click=lambda: [
                 _start_patient_launching_ui(),
                 utils.launch_predefined_patient(1)])
                ui.item('Cassian Bellwether, 48', on_click=lambda: [
                    _start_patient_launching_ui(),
                    utils.launch_predefined_patient(2)])
                ui.item('Marcus Williams, 34', on_click=lambda: [
                    _start_patient_launching_ui(),
                    utils.launch_predefined_patient(3)])

    if disabled:
        disease_difficulty.disable()
        neuroticism.disable()
        extraversion.disable()
        openness.disable()
        agreeableness.disable()
        conscientiousness.disable()
        submit_button.disable()
        prefablaunchbutton.disable()

@ui.refreshable
def open_debug_dialog_button(override = False, shown = False):
    global _open_debug_dialog_button_shown

    print(f"override: {override}, shown: {shown}")
    print(f"_open_debug_dialog_button_shown: {_open_debug_dialog_button_shown}")

    if (override and shown) or _open_debug_dialog_button_shown:
        ui.button('Generation log', on_click=_debug_dialog.open).classes(
            'mt-5').props("color=secondary")
    if override:
        _open_debug_dialog_button_shown = shown

@ui.refreshable
def feedback(message = None):
    if message is None:
        ui.markdown(f"*Awaiting connection...*")
    else:
        ui.markdown(message)

@ui.refreshable
def open_patient_information_button(override = False, shown = False):
    global _open_patient_information_button_shown

    print(f"override: {override}, shown: {shown}")
    print(f"_open_debug_dialog_button_shown: {_open_patient_information_button_shown}")

    if (override and shown) or _open_patient_information_button_shown:
        ui.button('Patient information', on_click=_patientinfo_dialog.open).classes(
            'mt-5').props("color=standard")
    if override:
        _open_patient_information_button_shown = shown

@ui.refreshable
def patient_control_buttons(disable_connection_buttons = False):
    """
    Render the patient control buttons.

    Args:
        disable_connection_buttons (bool): Whether the connection buttons should be disabled. These are
            the terminate and resume buttons. They are buttons that need a connection. Defaults to False.

    Returns:
        None
    """
    print(f"is_patient_running: {utils.is_patient_running}")
    print(f"is_patient_in_system: {utils.is_patient_in_system}")
    print(f"furhat_is_connected: {utils.furhat_is_connected}")
    print(f"disable_connection_buttons: {disable_connection_buttons}")

    with ui.row():
        open_patient_information_button(override=False, shown=False)
        terminate_button = ui.button('Pause', on_click=lambda: [utils.stop_and_get_final_feedback(), patient_control_buttons.refresh(disable_connection_buttons=True)]).classes('mt-5')
        if disable_connection_buttons:
            terminate_button.disable()
        if not utils.is_patient_running and utils.is_patient_in_system:
            ui.button('Feedback', on_click=_dialog_dialog.open).classes('mt-5')
        if not utils.is_patient_running and utils.is_patient_in_system and utils.furhat_is_connected:
            resume_button = ui.button('Resume', on_click=lambda: [utils.resume_patient(), patient_control_buttons.refresh(disable_connection_buttons=True)]).classes('mt-5')
            if disable_connection_buttons:
                resume_button.disable()
    if not utils.is_patient_running:
        terminate_button.disable()

@ui.refreshable
def furhat_status(status : str = None):
    global _messages_container

    if status == "listening":
        ui.icon('hearing').classes('mb-[0.9rem] ml-[-0.5rem]')
    elif status == "speaking":
        ui.icon('record_voice_over').classes('mb-[0.9rem] ml-[-0.5rem]')
    elif status == "started_idle":
        ui.icon('play_circle').classes('mb-[0.9rem] ml-[-0.5rem]')
    elif status == "ready":
        ui.icon('not_started').classes('mb-[0.9rem] ml-[-0.5rem]')
    elif status == "terminated":
        ui.icon('pause_circle').classes('mb-[0.9rem] ml-[-0.5rem]')
    elif status == "thinking":
        ui.icon('psychology').classes('mb-[0.9rem] ml-[-0.5rem]')
    elif status == "disconnected":
        ui.icon('wifi_off').classes('text-red-500 mb-[0.9rem] ml-[-0.5rem]')
    else:
        ui.spinner().classes('mb-[0.9rem] ml-[-0.5rem]')

def messages():
    global _messages_scroll_container, _messages_container
    scroll_area = ui.scroll_area().classes('w-full border rounded')
    _messages_scroll_container = scroll_area
    with scroll_area:
        _messages_container = ui.element('div').classes('flow-root w-full')
        with _messages_container:
            ui.markdown(f'*Awaiting connection...*')

def fresh_feedback_dialog():
    global _dialog_dialog, _dialog_conversation_feedback_content, _dialog_clinical_feedback_content

    _dialog_dialog.clear()

    with _dialog_dialog:
        card = ui.card().classes('w-[1000px] h-[700px] !max-w-full')
        with card:
            with ui.row().classes('w-full'):
                ui.markdown("## Feedback")
                ui.space()
                ui.button('Close', on_click=_dialog_dialog.close).classes('mt-5')
            with ui.tabs().classes('w-full') as tabs:
                conversation_feedback = ui.tab('Feedback on conversation')
                clinical_feedback = ui.tab('Feedback on clinical ability')
            with ui.tab_panels(tabs, value=conversation_feedback):#.classes('w-full'):
                with ui.tab_panel(conversation_feedback):
                    ui.markdown("This feedback uses the [MIRS](https://health.uconn.edu/principles-clinical-medicine-clinical-skills-assessment/master-interview-rating-scale-mirs/) (master interview rating scale).")
                    _dialog_conversation_feedback_content = ui.list().props('bordered separator')
                    with _dialog_conversation_feedback_content:
                        with ui.item().classes('bg-slate-600'):
                            with ui.element('div').classes('flex flex-row w-full gap-5 flex-nowrap'):
                                with ui.element('div').classes('basis-2/4'):
                                    ui.item_label('Score out of 5 and criterium').props('header').classes('text-bold pl-0')
                                with ui.element('div').classes('basis-2/4'):
                                    ui.item_label('Feedback and evidence').props('header').classes('text-bold pl-0')
                with ui.tab_panel(clinical_feedback):
                    _dialog_clinical_feedback_content = ui.list().props('bordered separator')
                    with _dialog_clinical_feedback_content:
                        with ui.item().classes('bg-slate-600'):
                            with ui.element('div').classes('flex flex-row w-full gap-5 flex-nowrap'):
                                with ui.element('div').classes('basis-1/4'):
                                    ui.item_label('Criterium').props('header').classes('text-bold pl-0')
                                with ui.element('div').classes('basis-3/4'):
                                    ui.item_label('Feedback').props('header').classes('text-bold pl-0')


def fresh_debug_dialog():
    global _debug_dialog, _debug_dialog_content

    _debug_dialog.clear()

    with _debug_dialog:
        card = ui.card().classes('w-[1000px] h-[700px] !max-w-full')
        with card:
            with ui.row().classes('w-full'):
                ui.markdown("## Generation log")
                ui.space()
                ui.button('Close', on_click=_debug_dialog.close).classes('mt-5')
            scroll_area = ui.scroll_area().classes('w-full h-full')
            with scroll_area:
                _debug_dialog_content = ui.list().props('separator')

def fresh_patient_dialog():
    global _patientinfo_dialog, _patientinfo_content

    _patientinfo_dialog.clear()

    with _patientinfo_dialog:
        card = ui.card().classes('w-[1000px] h-[700px] !max-w-full')
        with card:
            with ui.row().classes('w-full'):
                ui.markdown("## Patient information")
                ui.space()
                ui.button('Close', on_click=_patientinfo_dialog.close).classes('mt-5')
            scroll_area = ui.scroll_area().classes('w-full h-full')
            with scroll_area:
                _patientinfo_content = ui.element('div')


"""
UI logic
"""
def _start_patient_generation_ui():
    """
    Change UI elements to reflect the start of patient generation.
    """
    _start_notification(message="Launching patient generation...")
    form.refresh(disabled=True)

def _start_patient_launching_ui():
    """
    Change UI elements to reflect the start of patient launching.
    """
    _start_notification(message="Launching patient...")
    form.refresh(disabled=True)

def _start_notification(message = "Loading..."):
    global _generation_progress_notification
    _generation_progress_notification = ui.notification(message, spinner=True, position="top-right", type="ongoing", timeout=0)

def update_form_fields_running_patient():
    """
    Update the disabledness "terminate patient" button and the form fields.
    """
    patient_control_buttons.refresh(disable_connection_buttons=False)
    form.refresh(disabled=utils.is_patient_running)
    # TODO: Assumption: if patient is in system, the patient was generated. This is usually true, but consider a separate field in the server for that, and a separate WS call to check.
    open_debug_dialog_button.refresh(override=True, shown=utils.is_patient_in_system)
    open_patient_information_button.refresh(override=True, shown=utils.is_patient_in_system)

def update_last_form_values(disease_difficulty, neuroticism, extraversion, openness, agreeableness, conscientiousness):
    global _last_form_values
    _last_form_values = {
        "disease_difficulty": disease_difficulty,
        "neuroticism": neuroticism,
        "extraversion": extraversion,
        "openness": openness,
        "agreeableness": agreeableness,
        "conscientiousness": conscientiousness
    }

def add_patient_message(message,time):
    global _messages_container, _message_skeleton
    if _message_skeleton is not None:
        _message_skeleton.delete()
        _message_skeleton = None

    with _messages_container:
        ui.chat_message(message,
                        name='Patient',
                        stamp=time,
                        avatar='https://robohash.org/ui').props("sent")
    messages_scroll_to_bottom()

def add_doctor_message(message,time):
    global _messages_container, _message_skeleton
    with (_messages_container):
        ui.chat_message(message,
                        name='Doctor',
                        stamp=time,
                        avatar='https://static.vecteezy.com/ti/gratis-vector/p3/8957222-mannelijke-dokter-avatar-beroep-clipart-pictogram-in-flat-design-vector.jpg')
        _message_skeleton = ui.skeleton().classes('w-96 float-right mr-4 mb-2').props("type=QInput")
    messages_scroll_to_bottom()

def messages_scroll_to_bottom():
    global _messages_scroll_container
    _messages_scroll_container.scroll_to(percent=100)

def progress_message(message):
    global _generation_progress_notification
    if _generation_progress_notification is None:
        _start_notification()
    _generation_progress_notification.message = f"{message}"

def progress_step(message, step, total_steps):
    global _generation_progress_notification
    if _generation_progress_notification is None:
        _start_notification()
    _generation_progress_notification.message = f"{message} ({step}/{total_steps})"

def progress_end(state,message):
    async def wait_and_close():
        global _generation_progress_notification
        temp_notification = _generation_progress_notification
        _generation_progress_notification = None
        await asyncio.sleep(5)
        temp_notification.dismiss()

    if _generation_progress_notification is None:
        _start_notification()
    if state == "success":
        _generation_progress_notification.type = "positive"
    if state == "error":
        _generation_progress_notification.type = "negative"
        update_form_fields_running_patient()
    if state == "warning":
        _generation_progress_notification.type = "warning"
        update_form_fields_running_patient()

    _generation_progress_notification.message = message
    _generation_progress_notification.close_button = True
    _generation_progress_notification.spinner = False

    asyncio.create_task(wait_and_close())

def clear_messages():
    global _messages_container
    _messages_container.clear()

def server_connection_lost_ui():
    global _server_connection_notification, _generation_progress_notification, _furhat_connection_notification, _messages_container
    if _server_connection_notification is None:
        _server_connection_notification = ui.notification("Connecting to the intermediate server...", spinner=True, position="bottom-left", type="ongoing", timeout=0)
        form.refresh(disabled=True)
        patient_control_buttons.refresh(disable_connection_buttons=True)
        clear_messages()
        fresh_feedback_dialog()
        fresh_debug_dialog()
        fresh_patient_dialog()
        with _messages_container:
            ui.markdown(f'*Awaiting connection...*')
        feedback.refresh(f'*Awaiting connection...*')
    if _furhat_connection_notification is not None:
        _furhat_connection_notification.dismiss()
        _furhat_connection_notification = None
    # If the server was disconnected, the generation process failed.
    if _generation_progress_notification is not None:
        _generation_progress_notification.dismiss()
        _generation_progress_notification = None

def server_connection_restored_ui():
    global _server_connection_notification, _messages_container
    if _server_connection_notification is not None:
        _server_connection_notification.dismiss()
        _server_connection_notification = None
    clear_messages()

def furhat_connection_lost_ui():
    global _furhat_connection_notification
    if _furhat_connection_notification is None:
        _furhat_connection_notification = ui.notification("Connecting to the avatar...", spinner=True, position="bottom-left", type="ongoing", timeout=0)
        form.refresh(disabled=True)
        patient_control_buttons.refresh(disable_connection_buttons=True)
    furhat_status.refresh(None)

def furhat_connection_restored_ui():
    global _furhat_connection_notification
    if _furhat_connection_notification is not None:
        _furhat_connection_notification.dismiss()
        _furhat_connection_notification = None
    update_form_fields_running_patient()

def add_conversation_feedback_item(criterium, mark, i, feedback_message, evidence):
    def convert_score_to_color(score):
        if score == 1:
            return "bg-red-700 text-white"
        elif score == 2:
            return "bg-red-500 text-white"
        elif score == 3:
            return "bg-yellow-500 text-white"
        elif score == 4:
            return "bg-green-500 text-white"
        elif score == 5:
            return "bg-green-700 text-white"
        else:
            return "bg-gray-300 text-white"  # fallback for invalid scores

    with _dialog_conversation_feedback_content:
        with ui.item().props("dense"):
            with ui.element('div').classes('flex flex-row gap-4 no-wrap'):
                with ui.element('div').classes('basis-2/4 flex justify-center content-start gap-3 pt-2 pb-2'):
                    with ui.element('div').classes(f'w-10 h-10 rounded-full inline-flex items-center justify-center {convert_score_to_color(mark)}'):
                        ui.label(f"{mark}")
                    ui.markdown(f"{i+1} -- **{criterium}**")
                with ui.element('div').classes('basis-2/4 pt-2 pb-2'):
                    ui.label(feedback_message).classes("text-justify")
                    if len(evidence) > 0:
                        for e in evidence:
                            ui.markdown(f"> {e}")

def add_clinical_feedback_item(fb):
    for feedback in fb:
        with _dialog_clinical_feedback_content:
            with ui.item().props("dense"):
                with ui.element('div').classes('flex flex-row gap-4 no-wrap'):
                    with ui.element('div').classes('basis-1/4 pt-2 pb-2'):
                        ui.markdown(f"**{feedback['criterium']}**")
                    with ui.element('div').classes('basis-3/4 pt-2 pb-2'):
                        ui.label(feedback['feedback']).classes("text-justify")

def add_generation_log_item(log):
    global _debug_dialog_content
    with _debug_dialog_content:
        with ui.item().classes('w-[900px]'):
            ui.markdown(log)

def set_patient_info(info):
    global _patientinfo_content
    with _patientinfo_content:
            ui.markdown(info)