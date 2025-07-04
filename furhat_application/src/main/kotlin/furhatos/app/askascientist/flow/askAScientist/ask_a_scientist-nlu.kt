package furhatos.app.askascientist.flow.askAScientist

import furhatos.nlu.EnumEntity
import furhatos.nlu.Intent
import furhatos.util.Language

class QuestionWord : EnumEntity() {
    override fun getEnum(lang: Language): List<String> {
        return listOf(
            "who",
            "what",
            "where",
            "when",
            "how",
            "why"
        )
    }
}

class Question(val questionWord: QuestionWord? = null) : Intent() {
    override fun getExamples(lang: Language): List<String> {
        return listOf(
            "@questionWord"
        )
    }
}

class LetMeThink(val questionWord: QuestionWord? = null) : Intent() {
    override fun getExamples(lang: Language): List<String> {
        return listOf(
            "let me think",
            "can I think about that",
            "give me a moment",
            "a little time",
            "a bit of time"
        )
    }
}

class WhatCanIAsk(val questionWord: QuestionWord? = null) : Intent() {
    override fun getExamples(lang: Language): List<String> {
        return listOf(
            "what can I ask you",
            "what kind of question can I ask you",
            "what can you answer",
            "what kind of things do you know",
            "what do you know"
        )
    }
}

class IAmDone : Intent() {
    override fun getExamples(lang: Language): List<String> {
        return listOf(
            "I am done",
            "I am good",
            "I think I'm done",
            "I am finished",
            "alright I'm done"
        )
    }
}