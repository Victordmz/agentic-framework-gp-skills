package furhatos.app.askascientist.flow.askAScientist

import furhatos.app.askascientist.flow.state_before_init
import furhatos.app.askascientist.setting.Persona
import furhatos.app.askascientist.setting.activate
import furhatos.app.askascientist.setting.currentPersona
import furhatos.app.askascientist.setting.latest_conversationId
import furhatos.flow.kotlin.state
// import furhatos.flow.kotlin.voice.PollyNeuralVoice
import furhatos.flow.kotlin.voice.ElevenlabsVoice
import furhatos.flow.kotlin.*
import io.ktor.client.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.websocket.*
import io.ktor.http.*
import io.ktor.utils.io.core.*
import io.ktor.websocket.*
import kotlinx.coroutines.channels.ClosedReceiveChannelException
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.*
import kotlinx.serialization.json.Json
import java.io.IOException
import java.net.ConnectException
import java.util.concurrent.CancellationException

@Serializable data class jsonMessage(val action: String)
@Serializable data class patientGeneratedResponseMessage(val action: String = "patientGeneratedResponse", val response : String, val time : String)
@Serializable data class startPatientMessage(val action: String = "startPatient", val face : String, val voice: String, val new : Boolean)
@Serializable data class conversationIdMessage(val action: String = "conversationId", val conversationId : String)

// Global variable to hold the WebSocket session
var webSocketSession: DefaultClientWebSocketSession? = null

private val json: Json = Json { ignoreUnknownKeys = true }

fun client() = state {
    init{

            val client = HttpClient(CIO) {

            install(WebSockets) {
                pingInterval = 100_000
            }
        }

        // To prevent the flow from overfilling the buffer, we need to run the websocket in a separate coroutine
        call {
            runBlocking {
                while(true){
                    try {
                        println("Trying to connect to server...")
                        client.webSocket(method = HttpMethod.Get, host = "localhost", port = 8085, path = "/") {
                            println("Connected to server!")
                            furhat.ledStrip.solid(java.awt.Color(0,0,0))
                            webSocketSession = this

                            // Authenticate
                            send("{\"action\":\"setRole\",\"role\":\"furhat\"}")
                            sendToServer("{\"action\":\"furhatStatusUpdate\", \"status\":\"ready\"}")
                            state_before_init = "ready"

                            while (true) {
                                val message = incoming.receive() as? Frame.Text
                                val text = message?.readText()
                                if (text != null) {
                                    // Parse as jsonMessage
                                    try {
                                        val jsonMessage = json.decodeFromString<jsonMessage>(text)
                                        println("Received message: ${text}")

                                        // Try to parse as patientResponseMessage: the response of the patient
                                        try {
                                            val patientGeneratedResponseMessage = Json.decodeFromString<patientGeneratedResponseMessage>(text)
                                            if (patientGeneratedResponseMessage.action == "patientGeneratedResponse") {
                                                println("Received patient generated response: ${patientGeneratedResponseMessage.response}")
                                                raise(ResponseEvent(patientGeneratedResponseMessage.response))
                                                continue
                                            }
                                        } catch (_: SerializationException) {
                                        }

                                        // Try to parse as listenResponseMessage: the patient should listen
                                        try {
                                            val jsonMessage = Json.decodeFromString<jsonMessage>(text)
                                            if (jsonMessage.action == "listenResponse") {
                                                println("Received listen response message")
                                                raise("ListenEvent")
                                                continue
                                            }
                                        } catch (_: SerializationException) {
                                        }

                                        // Try to parse as startPatientMessage: start the conversation with the given patient
                                        try {
                                            val startPatientMessage = Json.decodeFromString<startPatientMessage>(text)
                                            if (startPatientMessage.action == "startPatient") {
                                                println("Received start patient message")
                                                val patient = Persona(
                                                    name = "Patient",
                                                    face = listOf(startPatientMessage.face),
//                                                    voice = listOf(PollyNeuralVoice(startPatientMessage.voice))
                                                    voice = listOf(ElevenlabsVoice(startPatientMessage.voice))
                                                    )
                                                currentPersona = patient
                                                activate(currentPersona)
                                                raise("receivedPatientInfo")
                                                continue
                                            }
                                        } catch (_: SerializationException) {
                                        }

                                        // Parse conversationId message
                                        try {
                                            val conversationIdMessage = Json.decodeFromString<conversationIdMessage>(text)
                                            if (conversationIdMessage.action == "conversationId") {
                                                println("Received conversation ID message:" + conversationIdMessage.conversationId)
                                                latest_conversationId = conversationIdMessage.conversationId
                                                continue
                                            }
                                        } catch (_: SerializationException) {
                                        }

                                        // Try to parse as stopPatientMessage: the patient should stop
                                        try {
                                            val jsonMessage = Json.decodeFromString<jsonMessage>(text)
                                            if (jsonMessage.action == "stopPatient") {
                                                println("stop patient message!")
                                                raise("terminateCurrentPersona")
                                                continue
                                            }
                                        } catch (_: SerializationException) {
                                        }

                                        println("Unknown message: $text")

                                    } catch (e: SerializationException) {
                                        println("Can't parse message $text")
                                    }
                                }
                            }
                        }
                    } catch (e: ConnectException) {
                        furhat.ledStrip.solid(java.awt.Color.RED)
                        println(e)
                        println("Connection failed, retrying in 5 seconds...")
                        delay(5000)
                    } catch (e: ClosedReceiveChannelException) {
                        furhat.ledStrip.solid(java.awt.Color.RED)
                        println(e)
                        println("Connection failed, retrying in 5 seconds...")
                        delay(5000)
                    } catch (e: CancellationException) {
                        furhat.ledStrip.solid(java.awt.Color.RED)
                        print(e)
                        println("Connection failed, restarting client...")
                        delay(5000)

                        // Somehow it needs this distinction to work properly
                        if(furhat.isVirtual()){
                            terminate()
                        }else{
                            parallel(thisState)
                        }

                    } catch (e: EOFException){
                        furhat.ledStrip.solid(java.awt.Color.RED)
                        println(e)
                        println("Connection failed, retrying in 5 seconds...")
                        delay(5000)
                    } catch (e: IOException){
                        furhat.ledStrip.solid(java.awt.Color.RED)
                        println(e)
                        println("Connection failed, retrying in 5 seconds...")
                        delay(5000)
                    }
                }
            }
        }
    }
    onExit {
        parallel(thisState)
    }
}

/**
 * Sends a message to the server via WebSocket.
 *
 * This function checks if the global WebSocket session is not null. If it is not null,
 * it sends the provided message to the server within a blocking coroutine context.
 *
 * @param message The message to be sent to the server.
 * @return Boolean indicating whether the message was successfully sent.
 */
fun sendToServer(message: String) : Boolean {
    print("Sending message: $message")
    if (webSocketSession != null) {
        runBlocking {
            webSocketSession!!.send(message)
        }
        println("Message sent!!")
        return true
    }else{
        println("Message not sent!!")
        return false
    }
}