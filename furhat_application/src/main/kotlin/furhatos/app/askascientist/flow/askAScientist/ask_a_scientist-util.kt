package furhatos.app.askascientist.flow.askAScientist

import furhatos.flow.kotlin.*

val BASE_URL =
        "https://api.wolframalpha.com/v1/spoken" // Endpoint for Wolfram Alpha's API with answers tailored for spoken interactions
val APP_ID = "EQKLKA-5EGTXH74UG" // Test account, feel free to use it for testing.
val FAILED_RESPONSES = listOf("No spoken result available", "Wolfram Alpha did not understand your input")
val TIMEOUT = 4000 // 4 seconds

/** State to conduct the query to the API */
fun query(question: String) = state {
    onEntry {
        val question = question
                .replace("+", "plus")
                .replace("-", "minus")
                .replace(" x ", " times ")
                .replace("%", " percent")
                .replace(" ", "+")
        println("modified question: $question")
        val query = "$BASE_URL?i=$question&appid=$APP_ID"

        /** Call to WolframAlpha API made in an anynomous substate (https://docs.furhat.io/flow/#calling-anonymous-states)
        to allow our timeout below to stop the call if it takes to long. Note that you explicitly have to cast the result to a String.
         */
        val response = call {
            khttp.get(query).text
        } as String

        // Reply to user depending on the returned response
        val reply = when {
            FAILED_RESPONSES.contains(response) -> {
                println("No answer to question: $question")
                random(
                        "Sorry my friend, I can't answer that",
                        "My apologies, I don't know that.",
                        "Sorry, I have no idea",
                        "Apologies, that, I don't know"
                )
            }
            else -> response
        }
        // Return the response
        terminate(reply)
    }

    onTime(TIMEOUT) {
        println("Issues connecting to Wolfram alpha")
        // If timeout is reached, we return nothing
        terminate("I'm having issues connecting to my brain. Try again later!")
    }
}