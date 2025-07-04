# Furhat Application README

*Accompanies the paper **“An Agentic AI Framework for Training General‑Practitioner Student Skills”** and the top‑level project README.*

---

## 1. What the Furhat Application Does 🤖

The **Furhat Application** is the embodied agent component of the framework. It runs as a Kotlin "skill" on a physical Furhat robot or, more commonly for development, on the Furhat SDK's virtual robot.

Its primary responsibilities are to act as the sensory "front-end" for the Virtual Simulated Patient (VSP):
-   **Connects** to the `central_backend_server` via a persistent WebSocket.
-   **Listens** to the user's speech (the student doctor) and uses Furhat's engine for **Speech-to-Text (STT)**.
-   **Sends** the transcribed text to the backend for processing by the VSP agent.
-   **Receives** text responses from the backend.
-   **Speaks** the responses using a **Text-to-Speech (TTS)** engine (e.g., ElevenLabs or AWS Polly).
-   **Changes** its visual appearance (face) and voice based on commands from the server to embody different patient personas.

Crucially, this application contains **no conversational AI or LLM logic**. It is an I/O and state management layer, with all cognitive processing handled by the Python backend.

---

## 2. Configuration & Setup 🛠

Follow these instructions to configure and run the Furhat application.

### Prerequisites
- **Java**: A Java 11 JRE is recommended (e.g., OpenJDK 11).
- **Furhat SDK**: You must download and install the [Furhat SDK](https://www.furhatrobotics.com/requestsdk).

### Configuration
1.  **WebSocket Server Address**:
    -   If your `central_backend_server` is not running on `localhost:8085`, you must update the connection details.
    -   Open `src/main/kotlin/furhatos/app/askascientist/flow/askAScientist/client.kt`.
    -   Modify the `host` and `port` parameters in the `client.webSocket(...)` call.

2.  **Text-to-Speech (TTS) Engine**:
    -   The application defaults to using `ElevenlabsVoice`. To use this, you must add your **ElevenLabs API key** in the Furhat SDK's web configuration interface (typically at `http://localhost:8080`).
    -   Alternatively, you can switch to Furhat's built-in AWS Polly voices. In `src/main/kotlin/furhatos/app/askascientist/flow/askAScientist/client.kt`, replace the line:
        ```kotlin
        voice = listOf(ElevenlabsVoice(startPatientMessage.voice))
        ```
        with:
        ```kotlin
        voice = listOf(PollyNeuralVoice(startPatientMessage.voice))
        ```
    > **Note:** If you switch to Polly, ensure the voice names sent by the backend server in `central_backend_server/conversion_tables.py` and `predefined_patients.py` are valid Polly voice names. Also don't forget to import PollyNeuralVoice in Kotlin.

### Running the Application
1.  Launch the **Furhat SDK** and start the virtual robot from its launcher window.
2.  Open the `furhat_application` directory as a project in your IDE (e.g., IntelliJ IDEA).
3.  Allow the IDE to sync and build the Gradle project.
4.  Run the main function in `src/main/kotlin/furhatos/app/askascientist/Main.kt`.
5.  The skill will launch and attempt to connect to the backend server. The robot's LED strip will turn red if the connection fails.

**Development Tips:**
-   See the [Furhat developer documentation](https://docs.furhat.io/) to get started with modifying the code.
-   To see more detailed WebSocket connection logs, set the VM option: `-Dio.ktor.development=true`.
-   To run the skill on a physical robot, use the VM option: `-Dfurhatos.skills.brokeraddress=<Furhat_IP_Address>`.

---

## 3. WebSocket Contract for Building Your Own Avatar 🎭

Below is the **complete** list of WebSocket messages that the Kotlin Furhat skill and the Python server (default: `ws://localhost:8085`) currently exchange.
Implementing these correctly will let any avatar (2‑D, 3‑D, VR, etc.) drop‑in‑replace the Furhat head.

### 3‑A.  Incoming Messages (Server → Avatar)

| `action` value             | Typical payload                                                    | When it arrives / what you must do                                                                                                                                                                                          |
| -------------------------- | ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `startPatient`             | `{ "face": "Dorothy", "voice": "Jane - Professional Audiobook Reader", "new": false }`            | A new (or resumed) virtual patient starts. Switch the avatar’s **appearance** (`face`) and **TTS voice** (`voice`). The boolean `new` is *true* for a fresh case, *false* when reconnecting to an already‑running patient.  |
| `patientGeneratedResponse` | `{ "response": "It started hurting yesterday.", "time": "14:03" }` | Core patient utterance generated by the LLM. **Speak** the text and animate “talking”.                                                                                                                                      |
| `listenResponse`           | `{}`                                                               | Stop talking and begin **STT** capture; when finished, reply with `getPatientResponse`.                                                                                                                                     |
| `stopPatient`              | `{}`                                                               | End the consultation; return to an idle / waiting state.                                                                                                                                                                    |
| `conversationId`           | `{ "conversationId": "188c4b25‑e861‑4609‑9e2d‑…" }`                | Unique session ID (useful for logs or linking to dashboards).                                                                                                                                                               |

### 3‑B.  Outgoing Messages (Avatar → Server)

| `action` value       | Minimum payload                                                                                                                  | Purpose                                                                                                                                                               |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `setRole`            | `{ "role": "furhat" }`                                                                                                           | **First** message after the socket opens – tells the backend “I am the avatar”.                                                                                       |
| `furhatStatusUpdate` | `{ "status": "speaking" }`                                                                                                       | Keeps dashboards in sync. Valid states are:<br>`ready`, `thinking`, `speaking`, `listening`, `started_idle`, `terminated`. Send whenever your internal mode changes.  |
| `getPatientResponse` | • To **continue** the dialog: `{}`<br>• After the doctor has spoken: `{ "doctorResponse": "I see, can you point to the pain?" }` | Triggers the LLM to produce the next patient utterance. If you include `doctorResponse`, it is logged and used for generation; omit it to simply resume.              |
| `addDoctorResponse`  | `{ "doctorResponse": "Let me think aloud for a second." }`                                                                       | (Optional) Log a doctor utterance **without** asking for an immediate patient reply – handy for delays, chitchat, etc.                                                |
| `addPatientResponse` | `{ "patientResponse": "Doctor?" }`                                                                                               | (Optional) Same idea but from the patient side (when the avatar ad‑libs).                                                                                             |

> **Tip:** If you are building a *stateless* front‑end and prefer the server to manage all timing, you can skip the two `add…Response` calls – just send `getPatientResponse` every time the doctor finishes talking. They are included here because of Furhat limitations.

### 3‑C.  Message‑flow cheat‑sheet

```text
(1)  Avatar  →  setRole
(2)  Server  →  startPatient
(3)  Avatar  →  furhatStatusUpdate "thinking"
(4)  Avatar  →  getPatientResponse          (first turn)
(5)  Server  →  patientGeneratedResponse
(6)  Avatar  →  furhatStatusUpdate "speaking"
(7)  Avatar  speaks text …
(8)  Avatar  →  furhatStatusUpdate "listening"
(9)  Server  →  listenResponse
(10) Avatar captures student speech, then
(11) Avatar  →  getPatientResponse {doctorResponse: "..."}  ← repeat loop
```

Follow this sequence (and state updates) and your custom avatar will behave identically to the Furhat implementation.


---

## 4. License 📄

This application inherits the repository‑wide **GPL‑3.0** license. See the top-level `LICENSE` file for full text.