import asyncio
import aiohttp
import config
import ui_utils
import json

"""
Package that contains all the business logic for the application.
Also communicates with UI utils (ui_utils.py) to update the UI.
"""

_websocket : aiohttp.ClientWebSocketResponse = None
# Stateful variable that keeps track of whether Furhat is connected or not. Is always up to date if the server is connected.
furhat_is_connected = False
# Stateful variable that keeps track of whether the patient is running or not. Is always up to date if the server is connected.
is_patient_running: bool = False
# Stateful variable that keeps track of whether there is a patient, running or not, in the system. Is always up to date if the server is connected.
is_patient_in_system: bool = False

###
# Functions to send messages to the server
###
def generate_patient(disease_difficulty, neuroticism, extraversion, openness, agreeableness, conscientiousness):
    ui_utils.fresh_debug_dialog()
    ui_utils.fresh_patient_dialog()
    ui_utils.open_debug_dialog_button.refresh(override=True,shown=True)
    ui_utils.open_patient_information_button.refresh(override=True,shown=True)
    send_message(json.dumps({"action": "generatePatient",
                             "diseaseDifficulty": disease_difficulty,
                             "neuroticism": neuroticism,
                             "extraversion": extraversion,
                             "openness": openness,
                             "agreeableness": agreeableness,
                             "conscientiousness": conscientiousness}))

def launch_predefined_patient(patient_nr):
    ui_utils.fresh_debug_dialog()
    ui_utils.fresh_patient_dialog()
    ui_utils.open_debug_dialog_button.refresh(override=True, shown=True)
    ui_utils.open_patient_information_button.refresh(override=True, shown=True)
    send_message(json.dumps({"action": "launchPredefinedPatient",
                             "patient_nr": patient_nr}))

###
# Server connection
###
def send_message(message):
    # print("Sending message...")
    if _websocket is not None:
        asyncio.create_task(_websocket.send_str(message))
        # print("Message sent.")
    # else:
        # print("No connection to the server. Message not sent.")

def set_patient_running(is_running):
    global is_patient_running
    is_patient_running = is_running

def set_patient_in_system(in_system):
    global is_patient_in_system
    is_patient_in_system = in_system

def stop_and_get_final_feedback():
    print("Stopping and getting final feedback...")
    send_message(json.dumps({"action": "stopAndGetFinalFeedback"}))

def resume_patient():
    ui_utils.fresh_feedback_dialog()
    send_message(json.dumps({"action": "resumePatient"}))

async def consumer():
    global _websocket, furhat_is_connected

    while True:
        try:
            async with aiohttp.ClientSession(trust_env=True) as session:
                # print(f"Connecting to {WS_CONN}")
                async with session.ws_connect(config.WS_CONN) as websocket:
                    print(f"Connected to: {config.WS_CONN}")
                    await websocket.send_str('{"action": "setRole","role":"dashboard"}')

                    #asyncio.create_task(remove_spinner())

                    _websocket = websocket
                    ui_utils.server_connection_restored_ui()

                    await websocket.send_str('{"action": "checkPatient"}')
                    await websocket.send_str('{"action": "getHistory"}')
                    await websocket.send_str('{"action": "getQuickFeedback"}')
                    await websocket.send_str('{"action": "recallFinalFeedback"}')
                    await websocket.send_str('{"action": "checkFurhatConnected"}')
                    await websocket.send_str('{"action": "getDebugLog"}')
                    await websocket.send_str('{"action": "getPatientInformation"}')
                    await websocket.send_str('{"action": "getConversationId"}')

                    async for message in websocket:
                        data = message.json()
                        print(f"Websocket received message: {data}")

                        if "action" not in data:
                            continue

                        if data["action"] == "doctorResponse" and "response" in data and "time" in data:
                            ui_utils.add_doctor_message(data["response"], data["time"])

                        if (data["action"] == "patientResponse" or data["action"] == "patientGeneratedResponse" ) and "response" in data and "time" in data:
                            ui_utils.add_patient_message(data["response"], data["time"])

                        if data["action"] == "quickFeedbackResponse" and "response" in data:
                            ui_utils.feedback.refresh(data["response"])

                        if data["action"] == "updateDebugLog" and "debugLog" in data:
                            ui_utils.add_generation_log_item(data["debugLog"])

                        if data["action"] == "patientInformation" and "information" in data:
                            ui_utils.set_patient_info(data["information"])

                        if data["action"] == "generationStart":
                            ui_utils.progress_message("Generating patient...")

                        if data["action"] == "startPatient" and "new" in data:
                            set_patient_running(True)
                            set_patient_in_system(True)
                            if data["new"]:
                                ui_utils.clear_messages()
                                ui_utils.fresh_feedback_dialog()
                            ui_utils.update_form_fields_running_patient()

                        if data["action"] == "stopPatient":
                            set_patient_running(False)
                            print("Patient stopped. Updating UI...")
                            ui_utils.update_form_fields_running_patient()

                        if data["action"] == "checkPatientResponse" and "inSystem" in data and "isRunning" in data:
                            set_patient_running(data["isRunning"])
                            set_patient_in_system(data["inSystem"])

                            print(f"Updated patient running: {is_patient_running}")
                            print(f"Updated patient in system: {is_patient_in_system}")
                            ui_utils.update_form_fields_running_patient()

                        if data["action"] == "generationUpdate" and "text" in data and "step" in data and "totalSteps" in data:
                            ui_utils.progress_step(data["text"], data["step"], data["totalSteps"])

                        if data["action"] == "generationStop" and "state" in data and "text" in data:
                            ui_utils.progress_end(data["state"], data["text"])

                        if data["action"] == "furhatStatusUpdate" and "status" in data:
                            ui_utils.furhat_status.refresh(data["status"])

                        if (data["action"] == "checkFurhatConnectedResponse" and "furhatConnected" in data) or data["action"] == "furhatDisconnected":
                            if data["action"] != "furhatDisconnected" and data["furhatConnected"]:
                                furhat_is_connected = True
                                send_message(json.dumps({"action": "getFurhatStatusUpdate"}))
                                ui_utils.furhat_connection_restored_ui()
                            else:
                                async def check_furhat_connected():
                                    await asyncio.sleep(5)
                                    send_message(json.dumps({"action": "checkFurhatConnected"}))

                                ui_utils.furhat_connection_lost_ui()
                                furhat_is_connected = False
                                await check_furhat_connected()

                        if data["action"] == "feedbackResponse" and "explanation" in data and "mark" in data and "criterium" in data and "i" in data and "evidence" in data:
                            ui_utils.add_conversation_feedback_item(data["criterium"],data["mark"],data["i"],data["explanation"],data["evidence"])

                        if data["action"] == "clinicalFeedbackResponse" and "feedback":
                            ui_utils.add_clinical_feedback_item(data["feedback"])

                        if data["action"] == "conversationId" and "conversationId" in data:
                            ui_utils.conversation_id = data["conversationId"]

        except aiohttp.ClientConnectorError as e:
            print(f"Connection failed: {e}. Retrying in {config.RETRY_DELAY} seconds...")
        except aiohttp.WSServerHandshakeError as e:
            print(f"WebSocket handshake failed: {e}. Retrying in {config.RETRY_DELAY} seconds...")
        except aiohttp.ClientError as e:
            print(f"WebSocket connection error: {e}. Retrying in {config.RETRY_DELAY} seconds...")
        except ConnectionResetError as e:
            print(f"Connection reset error: {e}. Retrying in {config.RETRY_DELAY} seconds...")
        except Exception as e:
            # raise e
            print(f"Unexpected error: {e}. Retrying in {config.RETRY_DELAY} seconds...")
        finally:
            _websocket = None
            ui_utils.server_connection_lost_ui()
            print("Reconnecting...")
            await asyncio.sleep(config.RETRY_DELAY)
