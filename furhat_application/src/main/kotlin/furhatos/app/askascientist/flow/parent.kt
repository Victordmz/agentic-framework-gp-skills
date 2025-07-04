package furhatos.app.askascientist.flow

import furhat.libraries.standard.BehaviorLib
import furhatos.app.askascientist.flow.furhatUniversalResponses.RestartSkill
import furhatos.app.askascientist.flow.furhatUniversalResponses.StopSkill
import furhatos.flow.kotlin.*

val Parent : State = state {
    include(BehaviorLib.AutomaticMovements.randomHeadMovements())
    onUserLeave(instant = true) {
        when{
            //last user left
            users.count < 1  -> furhat.attendNobody()
            //a bystander left
            users.count > 0 && users.current != it -> furhat.glance(it)
            //current user left
            users.count == 0 && users.current == it -> {
                while (furhat.isSpeaking) {
                    // Wait until finish speaking before switching attention
                }
                furhat.attend(users.other)
            }
        }


        if (users.count > 0) {
            when (users.current) {
                it -> furhat.attend(users.other)
                else -> furhat.glance(it)
            }
        }
    }

    onUserEnter(instant = true) {
        when (furhat.isAttendingUser) {
            true -> furhat.glance(it) // glance at additional user entering
            false  -> furhat.attend(it)
        }
    }
    onEvent<StopSkill> {
        terminate()
    }
    onEvent<RestartSkill> { goto(furhatos.app.askascientist.flow.main.Idle) }
}
