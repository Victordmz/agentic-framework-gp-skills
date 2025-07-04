#!/usr/bin/env python

# ⚠️ WARNING: RESEARCH DEMO ONLY – NOT FOR PRODUCTION USE ⚠️
#
# This code is a research prototype and should NOT be deployed in any
# production environment. It lacks critical features required for safe and
# scalable operation, including:
#
# - No transport security (no HTTPS, no authentication)
# - Global shared state with no isolation between clients
# - Blocking I/O inside async handlers (can freeze the event loop)
# - No error recovery, retry logic, or request timeouts
# - Uses `print()` instead of structured logging
#
# Use at your own risk. This repository is intended for experimentation only.

import json
import asyncio
from datetime import datetime

from websockets import ConnectionClosed
from websockets.asyncio.server import serve
import globals_conversation_logic
import utils
import globals_server

async def handler(websocket):
    globals_server.add_client(websocket)

    print("Client connected")
    try:
        async for message in websocket:
            print("Received message:", message)

            # Parse the message as JSON
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                print("Invalid JSON")
                continue

            # Check if the message contains an action
            if "action" not in data:
                print("No action specified")
                continue

            # Set the role of the client
            if not globals_server.has_a_client_role(websocket) and data.get("action") == "setRole" and "role" in data:
                role = data.get("role")
                globals_server.set_client_role(websocket, role)

                # If the furhat gets connected to an already running patient, start the patient on the furhat
                if role == "furhat" and globals_conversation_logic.has_patient():
                    await globals_conversation_logic.start_patient(globals_conversation_logic.get_patient(), new = False)
                continue

            # Deny messages from clients without a role
            if not globals_server.has_a_client_role(websocket):
                await websocket.send('{"error": "Role not set"}')
                continue

            # Add a message to the conversation history. Only used when not expecting a patient response generation.
            if data.get("action") == "addPatientResponse" and "patientResponse" in data:
                if globals_conversation_logic.is_patient_running() and globals_conversation_logic.has_patient():
                    patient_response = data.get("patientResponse")
                    time_now = datetime.now().strftime("%H:%M")
                    globals_conversation_logic.add_to_history("patient", patient_response, time_now)
                    await globals_server.broadcast_message({"action": "patientResponse", "response": patient_response, "time": time_now})

            # Add a message to the conversation history. Only used when not expecting a patient response generation.
            if data.get("action") == "addDoctorResponse" and "doctorResponse" in data:
                if globals_conversation_logic.is_patient_running() and globals_conversation_logic.has_patient():
                    doctor_response = data.get("doctorResponse")
                    time_now = datetime.now().strftime("%H:%M")
                    globals_conversation_logic.add_to_history("doctor", doctor_response, time_now)
                    await globals_server.broadcast_message({"action": "doctorResponse", "response": doctor_response, "time": time_now})

            # Generate a response.
            elif data.get("action") == "getPatientResponse" and "doctorResponse" not in data:
                if globals_conversation_logic.is_patient_running() and globals_conversation_logic.has_patient():
                    if globals_conversation_logic.last_message_is_from_patient():
                        await websocket.send('{"action": "listenResponse"}')
                    else:
                        await utils.generate_patient_response()


            # Add a message to the conversation history and generate a response.
            elif data.get("action") == "getPatientResponse" and "doctorResponse" in data:
                if globals_conversation_logic.is_patient_running() and globals_conversation_logic.has_patient():
                    doctor_response = data.get("doctorResponse")
                    current_time = datetime.now().strftime("%H:%M")
                    globals_conversation_logic.add_to_history("doctor", doctor_response, current_time)

                    # Send the doctor response
                    await globals_server.broadcast_message({"action": "doctorResponse", "response": doctor_response, "time": current_time})

                    # Get the patient response
                    await utils.generate_patient_response()

                    # Ask feedback on the doctor response
                    await utils.ask_quick_feedback()

            # Check if Furhat is connected
            elif data.get("action") == "checkFurhatConnected":
                furhat_connected = globals_server.is_furhat_connected()
                await websocket.send(json.dumps({"action":"checkFurhatConnectedResponse","furhatConnected": furhat_connected}))

            # Give Furhat status
            elif data.get("action") == "getFurhatStatusUpdate":
                furhat_status = globals_conversation_logic.get_furhat_status()
                await websocket.send(json.dumps({"action":"furhatStatusUpdate","status": furhat_status}))

            # Update Furhat status (given by Furhat)
            elif data.get("action") == "furhatStatusUpdate" and "status" in data:
                furhat_status = data.get("status")
                await globals_conversation_logic.update_furhat_status(furhat_status)

            # Check if a patient is running
            elif data.get("action") == "checkPatient":
                has_patient = globals_conversation_logic.has_patient()
                is_running = globals_conversation_logic.is_patient_running()
                await websocket.send(json.dumps({"action":"checkPatientResponse","inSystem": has_patient, "isRunning": is_running}))

            # Send the conversation history
            elif data.get("action") == "getHistory":
                for history_item in globals_conversation_logic.get_conversation_history():
                    if history_item["origin"] == "doctor":
                        await websocket.send(json.dumps({"action": "doctorResponse", "response": history_item["message"], "time": history_item["time"]}))
                    elif history_item["origin"] == "patient":
                        await websocket.send(json.dumps({"action": "patientResponse", "response": history_item["message"], "time": history_item["time"]}))

            elif data.get("action") == "getDebugLog":
                for log_item in globals_conversation_logic.get_debug_log():
                    await websocket.send(json.dumps({"action": "updateDebugLog", "debugLog": log_item}))

            elif data.get("action") == "getPatientInformation":
                await globals_conversation_logic.send_basic_patient_information()

            # Send the quick feedback
            elif data.get("action") == "getQuickFeedback":
                await websocket.send(json.dumps({"action": "quickFeedbackResponse", "response": globals_conversation_logic.get_quick_feedback()}))

            elif data.get("action") == "generatePatient" and "diseaseDifficulty" in data and "neuroticism" in data and "extraversion" in data and "openness" in data and "agreeableness" in data and "conscientiousness" in data:
                disease_difficulty = data.get("diseaseDifficulty")
                neuroticism = data.get("neuroticism")
                extraversion = data.get("extraversion")
                openness = data.get("openness")
                agreeableness = data.get("agreeableness")
                conscientiousness = data.get("conscientiousness")
                try:
                    await globals_conversation_logic.reset_patient()
                    await utils.generate_patient(disease_difficulty, neuroticism, extraversion, openness, agreeableness, conscientiousness)
                except Exception as e:
                    print("Error generating patient:", e)
                    await websocket.send(json.dumps({"action": "generationStop", "state": "error",
                                       "text": "Something went wrong. Please try again."}))


            elif data.get("action") == "launchPredefinedPatient" and "patient_nr" in data:
                try:
                    await globals_conversation_logic.reset_patient()
                    await utils.launch_predefined_patient(data.get("patient_nr"))
                except Exception as e:
                    print("Error generating patient:", e)
                    await websocket.send(json.dumps({"action": "generationStop", "state": "error",
                                       "text": "Something went wrong. Please try again."}))

            elif data.get("action") == "stopAndGetFinalFeedback":
                await utils.stop_patient()

                if globals_conversation_logic.has_final_feedback():
                    print("Feedback already generated. Sending...")
                    final_feedback = globals_conversation_logic.get_final_feedback()
                    for feedback in final_feedback:
                        await websocket.send(json.dumps(feedback))
                else:
                    print("Stopping patient and getting final feedback...")
                    await utils.final_feedback()

            elif data.get("action") == "recallFinalFeedback":
                final_feedback = globals_conversation_logic.get_final_feedback()
                for feedback in final_feedback:
                    await websocket.send(json.dumps(feedback))

            elif data.get("action") == "resumePatient":
                print("Resuming patient...")
                globals_conversation_logic.clear_final_feedback()
                await globals_conversation_logic.start_patient(globals_conversation_logic.get_patient(), new = False)

            elif data.get("action") == "getConversationId":
                await globals_conversation_logic.send_conversation_id()

    except ConnectionClosed:
        pass
    finally:
        globals_server.remove_client(websocket)
        # Remove the client from the connected clients set
        if globals_server.get_client_role(websocket) == "furhat":
            await globals_server.broadcast_message({"action": "furhatDisconnected"})
            await globals_conversation_logic.update_furhat_status("disconnected")
        globals_server.remove_client_role(websocket)
        print("Client disconnected")

async def main():
    print("Booting up websockets server...")
    server = await serve(handler, "localhost", 8085)
    try:
        await server.serve_forever()
    except asyncio.CancelledError:
        # stop taking new clients
        server.close()
        # wait for all clients to close
        await server.wait_closed()
        # re-raise cancellation
        raise

# To run the server
if __name__ == "__main__":
    asyncio.run(main())