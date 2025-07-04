package furhatos.app.askascientist

import furhatos.app.askascientist.flow.Init
import furhatos.skills.Skill
import furhatos.flow.kotlin.*

class AskAScientistSkill : Skill() {
    override fun start() {
        Flow().run(Init)
    }
}

fun main(args: Array<String>) {
    Skill.main(args)
}
