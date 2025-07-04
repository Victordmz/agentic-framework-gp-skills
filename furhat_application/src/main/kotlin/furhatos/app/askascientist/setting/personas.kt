package furhatos.app.askascientist.setting

import furhatos.flow.kotlin.FlowControlRunner
import furhatos.flow.kotlin.furhat
import furhatos.flow.kotlin.voice.AzureVoice
import furhatos.flow.kotlin.voice.PollyNeuralVoice
import furhatos.flow.kotlin.voice.Voice

class Persona(val name: String = "Furhat",
              val mask: String = "adult",
              val face: List<String> = listOf("Titan"),
              val voice: List<Voice> = listOf(PollyNeuralVoice("Gregory-Neural")),
)

fun FlowControlRunner.activate(persona: Persona) {
    for (voice in persona.voice) {
        if (voice.isAvailable) {
            furhat.voice = voice
            break
        }
    }
    for (face in persona.face) {
        if (furhat.faces.get(persona.mask)?.contains(face)!!){
            furhat.setCharacter(face)
            break
        }
    }
}

private val defaultPersona = Persona()
var currentPersona = defaultPersona
var latest_conversationId = "UNSET"

fun FlowControlRunner.resetPersona() {
    currentPersona = defaultPersona
    activate(currentPersona)
}