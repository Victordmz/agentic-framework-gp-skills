package furhatos.app.askascientist.flow

import furhatos.app.askascientist.flow.main.Start
import furhatos.flow.kotlin.State
import furhatos.flow.kotlin.furhat
import furhatos.flow.kotlin.onUserEnter
import furhatos.flow.kotlin.state

fun WaitForUser(timeout: Int): State = state() {
    onEntry{

    }
    onUserEnter {
        furhat.attend(it)
        terminate(true)
    }
    onTime(timeout) {
        terminate(false)
    }
}