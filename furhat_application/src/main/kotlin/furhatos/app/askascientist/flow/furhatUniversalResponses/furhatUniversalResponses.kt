package furhatos.app.askascientist.flow.furhatUniversalResponses

import furhatos.event.Event
import furhatos.flow.kotlin.furhat
import furhatos.flow.kotlin.onResponse
import furhatos.flow.kotlin.partialState
import furhatos.flow.kotlin.raise
import furhatos.nlu.common.AskName
import furhatos.nlu.common.RequestRepeat

class StopSkill : Event()
class RestartSkill : Event()

/** These are responses to common questions which can be inluded in other states right above the general onResponse {}
 * use with include(FurhatUniversalResponses)
 * @author Charlie Caper
 * */
val FurhatUniversalResponses = partialState {

    onResponse(listOf("less loud", "lower")) { //Todo: test if 'lower' is too wide?
        furhat.system.volume -= 8
        furhat.ask("Ok, I will speak a bit less loud.")
        reentry()
    }
    onResponse(listOf("loud", "louder")) {
        furhat.system.volume += 8
        furhat.ask("Ok, I will speak a bit louder.")
        reentry()
    }
    // this will only work if you catch the created event
    onResponse(listOf("please stop", "just stop")) {
        furhat.say("ok")
        send(StopSkill())
        delay(1000) // these lines below are here in case the event is not caught
        furhat.say("I'm sorry. I'm afraid I can't do that.")
        reentry()
    }
    // this will only work if you catch the created event
    onResponse(listOf("restart the demo", " please restart", "start from the beginning", "start over")) {
        furhat.say {
            random { +"Sure,"; +"No problem," }
            random { +"I'll start over."; +"I'll take it from the top." }
        }
        send(RestartSkill())
        delay(1000) // these lines below are here in case the event is not caught
        furhat.say("I'm sorry. I'm afraid I can't do that.")
        reentry()
    }
    onResponse<AskName> {
        furhat.say("My name is Furhat.")
        reentry()
    }
    onResponse("who are you") {
        raise(AskName())
    }
    onResponse("old are you", "your age") {
        furhat.say("I was born in Stockholm in 2011.")
        reentry()
    }
    onResponse("where are you from", "where you from") {
        furhat.say("I am from Stockholm, Sweden")
        reentry()
    }
    onResponse<RequestRepeat> {
        furhat.say(furhat.dialogHistory.utterances.last().toUtterance())
        reentry()
    }
//    onResponse<CanYouSpeak> {
//        //var word = ""
//        //var whatLanguage: Language? = it.intent.language
//        //Todo: Catch all languages + if the language is in spoken or understood languages and repeat back
//        furhat.say {
//            +"While I can speak and understand many languages,"
//        }
//        furhat.say {
//            +"I'm currently only able to do this demo in english."
//        }
//        furhat.say {
//            +"Now,"
//        }
//        delay(200)
//        reentry()
//    }
    onResponse("what time is it?", "what's the time") {
        val calendar = java.util.Calendar.getInstance()
        val time = calendar.time.minutes.toString() + " past " + (calendar.time.hours % 12).toString()
        furhat.say("Why do people keep asking me this? It is $time.")
        delay(200)
        reentry()
    }
}