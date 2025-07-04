package furhatos.app.askascientist.nlu

import furhatos.nlu.Intent
import furhatos.util.Language

class TellMeAboutYourself : Intent() {
    override fun getExamples(lang: Language): List<String> {
        return listOf(
                "who are you",
                "present yourself",
                "introduce yourself",
                "tell us who you are",
                "tell us about yourself",
                "can you present yourself",
                "can you introduce yourself",
                "can you tell us a little bit more about you",
                "tell me about yourself",
                "and who are you",
                "tell me a bit more about yourself"
        )
    }
}