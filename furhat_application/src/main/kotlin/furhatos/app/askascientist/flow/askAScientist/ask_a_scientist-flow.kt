package furhatos.app.askascientist.flow.askAScientist

import furhatos.app.askascientist.audiofeed.FurhatAudioFeedStreamer
import furhatos.app.askascientist.audiofeed.FurhatAudioFeedRecorder
import furhatos.app.askascientist.flow.Init
import furhatos.app.askascientist.flow.Parent
import furhatos.app.askascientist.flow.WaitForUser
import furhatos.app.askascientist.flow.main.Idle
import furhatos.app.askascientist.flow.state_before_init
import furhatos.app.askascientist.setting.latest_conversationId
import furhatos.event.Event
import furhatos.flow.kotlin.*
import java.io.File
import java.util.*
import kotlin.math.max


fun Furhat.exsay(message:String) {
    say(message)
}

class ResponseEvent(val text : String) : Event()
class ListenEvent : Event()

var timer_start: Long = 0

val AskAScientist: State = state(Parent) {
    onEntry {
        // Set the timer to the current time
        timer_start = System.currentTimeMillis()    
        sendToServer("{\"action\":\"furhatStatusUpdate\", \"status\":\"thinking\"}")
        sendToServer("{\"action\":\"getPatientResponse\"}")

    }

    onEvent("receivedPatientInfo"){ // Server got restarted, Furhat didn't.
        timer_start = System.currentTimeMillis()
        sendToServer("{\"action\":\"furhatStatusUpdate\", \"status\":\"thinking\"}")
        sendToServer("{\"action\":\"getPatientResponse\"}")
    }
    onReentry {
        // Check if we still have a user present. Skip this if it's running virtually.
        if (!furhat.isVirtual() && users.count == 0) {
            // wait and see if a user reappears
            if (call(WaitForUser(timeout = 8000)) as Boolean) {
                // user reappeared - continue on as normal
            } else {
                // user did not reappear - abort
                goto(Idle)
            }
        }

        sendToServer("{\"action\":\"addPatientResponse\", \"patientResponse\":\"Doctor?\"}")
        sendToServer("{\"action\":\"furhatStatusUpdate\", \"status\":\"speaking\"}")
        furhat.exsay("Doctor?")
        sendToServer("{\"action\":\"furhatStatusUpdate\", \"status\":\"listening\"}")
        //furhat.say("Hello, doctor?")
        furhat.listen(9000, endSil = 3000, maxSpeech = 60000)
        sendToServer("{\"action\":\"furhatStatusUpdate\", \"status\":\"started_idle\"}")
    }

    onResponse<LetMeThink> {

        // Choose one of the following responses at random
        val randomNumber = Random().nextInt(3)
        var response = ""
        when (randomNumber) {
            0 -> response = "Of course."
            1 -> response = "Sure, I have time."
            2 -> response = "Take your time."
        }
        sendToServer("{\"action\":\"addDoctorResponse\", \"doctorResponse\":\"${it.text}\"}")
        sendToServer("{\"action\":\"addPatientResponse\", \"patientResponse\":\"$response\"}")
        sendToServer("{\"action\":\"furhatStatusUpdate\", \"status\":\"speaking\"}")
        furhat.exsay(response)
        sendToServer("{\"action\":\"furhatStatusUpdate\", \"status\":\"listening\"}")
        furhat.listen(25000, endSil = 3000, maxSpeech = 60000)
        sendToServer("{\"action\":\"furhatStatusUpdate\", \"status\":\"started_idle\"}")
    }

    onResponse {
        timer_start = System.currentTimeMillis()
        sendToServer("{\"action\":\"furhatStatusUpdate\", \"status\":\"thinking\"}")
        sendToServer("{\"action\":\"getPatientResponse\", \"doctorResponse\":\"${it.text}\"}")

//        furhat.exsay(response)
//        furhat.listen(15000, endSil = 1600)
    }
    onNoResponse {
        println("No response")
        reentry()
    }

    onEvent("terminateCurrentPersona") {
        print("Terminating persona")
        sendToServer("{\"action\":\"furhatStatusUpdate\", \"status\":\"terminated\"}")
        state_before_init = "terminated"
        goto(Init)
    }

    onEvent<ResponseEvent> {
        // Calculate time taken to respond
        val timer_end = System.currentTimeMillis()
        val time_taken = timer_end - timer_start
        println("Time taken to respond: $time_taken ms")
        sendToServer("{\"action\":\"furhatStatusUpdate\", \"status\":\"speaking\"}")
        furhat.exsay(it.text)
        sendToServer("{\"action\":\"furhatStatusUpdate\", \"status\":\"listening\"}")
        furhat.listen(15000, endSil = 3000, maxSpeech = 60000)
        sendToServer("{\"action\":\"furhatStatusUpdate\", \"status\":\"started_idle\"}")
    }

    onEvent("ListenEvent") {
        println("Listen event.")
        sendToServer("{\"action\":\"furhatStatusUpdate\", \"status\":\"listening\"}")
        furhat.listen(15000, endSil = 3000, maxSpeech = 60000)
        println("End of listen")
        sendToServer("{\"action\":\"furhatStatusUpdate\", \"status\":\"started_idle\"}")
    }

}