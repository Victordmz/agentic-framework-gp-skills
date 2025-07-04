package furhatos.app.askascientist.flow.main

import furhatos.app.askascientist.flow.askAScientist.AskAScientist
import furhatos.app.askascientist.flow.Parent
import furhatos.flow.kotlin.State
import furhatos.flow.kotlin.furhat
import furhatos.flow.kotlin.state

val Start: State = state(Parent) {
    onEntry {
        //furhat.say("Hello Doctor.")
        call(AskAScientist)
        furhat.say("It was great to speak with you! That marks the end of this conversation. Over and out.")
        exit()
    }
}
