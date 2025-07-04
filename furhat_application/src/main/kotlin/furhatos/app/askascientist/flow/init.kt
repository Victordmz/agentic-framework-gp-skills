package furhatos.app.askascientist.flow

import furhatos.app.askascientist.flow.askAScientist.client
import furhatos.app.askascientist.flow.askAScientist.sendToServer
import furhatos.app.askascientist.flow.main.Idle
import furhatos.app.askascientist.setting.*
import furhatos.flow.kotlin.State
import furhatos.flow.kotlin.state
import furhatos.flow.kotlin.users
import furhatos.flow.kotlin.*

var state_before_init = "ready"

val Init: State = state() {
    init {
        parallel(client(), abortOnExit=false)

        /** Set our default interaction parameters */
        users.setSimpleEngagementPolicy(distanceToEngage, maxNumberOfUsers)
    }

    onEntry {
        /** Set our main character - defined in personas */
        resetPersona()
        sendToServer("{\"action\":\"furhatStatusUpdate\", \"status\":\"speaking\"}")
        furhat.say("Ready when you are!")
        sendToServer("{\"action\":\"furhatStatusUpdate\", \"status\":\"$state_before_init\"}")
    }

    onEvent("receivedPatientInfo"){
        println("receivedPatientInfo")
        goto(Idle)
    }

}
