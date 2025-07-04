# This file contains the global state of the application's logic.
# This is global state because it is shared across multiple files in the project.
# They can therefore be used in any file in the project.
import globals_server
from globals_server import broadcast_message

class Patient:
    def __init__(self, disease, vignette, face, voice, neuroticism, extraversion, openness, agreeableness, conscientiousness):
        self.disease = disease
        self.vignette = vignette
        self.face = face
        self.voice = voice
        self.neuroticism = neuroticism
        self.extraversion = extraversion
        self.openness = openness
        self.agreeableness = agreeableness
        self.conscientiousness = conscientiousness

# Unique conversation id
_conversation_id = None
# The conversation history
_conversation_history = []
# The debug log string for generation
_debug_log = []
# The latest quick feedback
_quick_feedback = ""
# The latest final feedback. Contains broadcastable feedback elements.
_final_feedback = []
# The current patient
_patient : Patient = None
# If patient is running
_is_patient_running = False
# Current status
_status = "disconnected"

def generate_conversation_id():
    """
    Generate a random conversation ID consisting of 16 hexadecimal characters.
    This ID is used to uniquely identify a conversation session.
    Returns:
        str: A 16-character hexadecimal string representing the conversation ID.
    """
    import random
    global _conversation_id
    _conversation_id = ''.join(random.choices('0123456789abcdef', k=16))
    return _conversation_id

async def send_conversation_id():
    """
    Sends the current conversation ID to the UI.
    This function is called when the conversation ID is generated or reset.
    Returns:
        None
    """
    global _conversation_id
    # Broadcast the conversation ID to the UI and Furhat
    await broadcast_message({"action": "conversationId", "conversationId": _conversation_id})

def get_conversation_id():
    """
    Retrieve the current conversation ID.

    Returns:
        str: The current conversation ID.
    """
    global _conversation_id
    if _conversation_id is None:
        generate_conversation_id()
    return _conversation_id

def add_to_history(origin, message, time):
    """
    Add a message to the conversation history.

    Args:
        origin (str): The origin of the message (e.g., 'doctor', 'patient').
        message (str): The message content to be added to the history.
        time (str): The time the message was sent.

    Returns:
    None
    """
    global _conversation_history
    _conversation_history.append({"origin": origin, "message": message, "time": time})

async def update_furhat_status(status):
    """
    Updates the current Furhat status and broadcasts the updated status.
    Should be the result of a message from the Furhat itself as much as possible, except for
    statuses that are out of the Furhat's control, such as "disconnected".

    Args:
        status (str): The status to be set.

    Returns:
    None
    """
    global _status
    _status = status
    await broadcast_message({"action": "furhatStatusUpdate", "status": status})

def get_furhat_status():
    """
    Retrieve the current Furhat status.

    Returns:
    str: The current status.
    """
    global _status
    return _status

def add_final_feedback(feedback: dict):
    """
    Add feedback to the final feedback.

    Args:
        feedback (dict): The feedback to be added.

    Returns:
    None
    """
    global _final_feedback
    _final_feedback.append(feedback)

def has_final_feedback():
    """
    Check if there is final feedback.

    Returns:
    bool: True if there is final feedback, False otherwise.
    """
    global _final_feedback
    return len(_final_feedback) > 0

def get_final_feedback():
    """
    Retrieve the final feedback.

    Returns:
    list: The final feedback as a list of dictionaries.
    """
    global _final_feedback
    return _final_feedback

def clear_final_feedback():
    """
    Clear the final feedback.
    Use this function anytime the conversation is started, resumed or reset.

    Returns:
    None
    """
    global _final_feedback
    _final_feedback = []

def get_conversation_history():
    """
    Retrieve the conversation history.

    Returns:
    list: The conversation history as a list of dictionaries.
    """
    global _conversation_history
    return _conversation_history

def last_message_is_from_patient():
    """
    Check if the last message in the conversation history is from the patient.

    Returns:
    bool: True if the last message is from the patient, False otherwise.
    """
    global _conversation_history
    return len(_conversation_history) > 0 and _conversation_history[-1]["origin"] == "patient"

async def add_debug_log(message):
    """
    Append a message to the debug log and broadcast the updated log.

    Args:
        message (str): The debug message to be added.

    Returns:
    None
    """
    global _debug_log
    _debug_log.append(message)
    await broadcast_message({"action": "updateDebugLog", "debugLog": message})

def get_debug_log():
    """
    Retrieve the debug log.

    Returns:
    list: The debug log as a list of strings.
    """
    global _debug_log
    return _debug_log

def get_patient() -> Patient:
    """
    Retrieve the current patient.

    Returns:
    Patient: The current patient.
    """
    global _patient
    return _patient

def has_patient():
    """
    Check if there is a current patient.

    Returns:
    bool: True if there is a current patient, False otherwise.
    """
    global _patient
    return _patient is not None

def is_patient_running():
    """
    Check if the patient is currently running.

    Returns:
    bool: True if the patient is running, False otherwise.
    """
    global _is_patient_running
    return _is_patient_running

def _set_patient(patient):
    """
    Set the current patient.

    Args:
        patient (Patient): The patient object to be set as the current patient.

    Returns:
    None
    """
    global _patient
    _patient = patient

def _set_patient_running(is_running):
    """
    Set if the patient is running.

    Args:
        is_running (bool): True if the patient is running, False otherwise.

    Returns:
    None
    """
    global _is_patient_running
    _is_patient_running = is_running

def get_quick_feedback():
    """
    Retrieve the latest quick feedback.

    Returns:
    str: The latest quick feedback.
    """
    global _quick_feedback
    return _quick_feedback

async def set_quick_feedback(feedback):
    """
    Set the latest quick feedback.

    Args:
        feedback (str): The quick feedback to be set.

    Returns:
    None
    """
    global _quick_feedback
    await broadcast_message({"action": "quickFeedbackResponse", "response": feedback})
    _quick_feedback = feedback

async def send_basic_patient_information():
    """
    Sends the basic patient information to the UI.

    Returns:
        None
    """
    global _patient
    if _patient is None:
        return
    basic_information = "\n".join(_patient.vignette.split("\n")[1:4])
    await broadcast_message({"action": "patientInformation", "information": basic_information})

async def start_patient(patient, new: bool = True):
    """
    Sends a broadcast message to start the patient interaction.

    Args:
        patient (Patient): The patient to be started.
        new (bool): True if the patient is new, False if the patient is resumed.

    Returns:
        None
    """
    _set_patient(patient)
    _set_patient_running(True)

    message = {
        "action": "startPatient",
        "face": patient.face,
        "voice": patient.voice,
        "new": new
    }
    if globals_server.is_furhat_connected():
        await broadcast_message(message)

        await send_basic_patient_information()

        if new:
            await broadcast_message({"action": "generationStop",
                                     "state": "success",
                                     "text": "Generation successful. The patient is ready."})
    else:
        if new:
            await broadcast_message({"action": "generationStop",
                                     "state": "warning",
                                     "text": "Generation successful, but there is no connection with the avatar."})
    generate_conversation_id()
    await send_conversation_id()
    await add_debug_log("Conversation id: " + get_conversation_id())


async def stop_patient():
    """
    Set the patient as not running.

    Returns:
        None
    """
    _set_patient_running(False)


async def reset_patient():
    """
    Wipes the existence of the current patient, if any.

    Returns:
        None
    """
    global _conversation_history, _debug_log, _quick_feedback
    _set_patient_running(False)
    _set_patient(None)
    _conversation_history = []
    _debug_log = []
    _quick_feedback = ""
    clear_final_feedback()