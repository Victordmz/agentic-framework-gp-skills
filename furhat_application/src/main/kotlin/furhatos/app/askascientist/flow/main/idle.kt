package furhatos.app.askascientist.flow.main

import furhatos.app.askascientist.flow.Init
import furhatos.app.askascientist.flow.Parent
import furhatos.app.askascientist.flow.askAScientist.exsay
import furhatos.app.askascientist.flow.askAScientist.sendToServer
import furhatos.flow.kotlin.*

val Idle: State = state(Parent) {

    init {
    }

    onEntry {
        sendToServer("{\"action\":\"furhatStatusUpdate\", \"status\":\"started_idle\"}")
        furhat.attendNobody()
        when {
            users.count > 0 -> {
                furhat.attend(users.random)
                goto(Start)
            }
            users.count == 0 && furhat.isVirtual() -> goto(Start) // if the skill is run on virtual furhat, ignore if there are no users and start anyway.
            users.count == 0 && !furhat.isVirtual() -> furhat.say("I can't see anyone. Step closer please. ")
        }
    }

    onUserEnter {
        furhat.attend(it)
        goto(Start)
    }

    // Only here in cases the robot fucks up
    onEvent("terminateCurrentPersona") {
        print("Terminating persona")
        sendToServer("{\"action\":\"furhatStatusUpdate\", \"status\":\"terminated\"}")
        goto(Init)
    }
}