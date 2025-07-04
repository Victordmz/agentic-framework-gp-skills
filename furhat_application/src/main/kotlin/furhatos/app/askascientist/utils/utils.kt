package furhatos.app.epigreeter.utils

import furhatos.flow.kotlin.Furhat
import java.math.BigInteger
import java.security.MessageDigest
import kotlin.random.Random

var saidOptions = mutableMapOf<Int, Int>()
fun Furhat.say(vararg args: String) {
    val hash = args.contentHashCode()
    var randomVal = Random.nextInt(0, args.size)
    if (args.size > 1) {
        while (saidOptions.containsKey(hash) && saidOptions[hash] == randomVal) {
            randomVal = Random.nextInt(0, args.size)
        }
    }
    saidOptions[hash] = randomVal
    say(args[randomVal])
    println("done")
}
fun random(vararg args: String): String{
    val hash = args.contentHashCode()
    var randomVal = Random.nextInt(0, args.size)
    if (args.size > 1) {
        while (saidOptions.containsKey(hash) && saidOptions[hash] == randomVal) {
            randomVal = Random.nextInt(0, args.size)
        }
    }
    saidOptions[hash] = randomVal
    return (args[randomVal])
}

fun md5(input:String): String {
    val md = MessageDigest.getInstance("MD5")
    return BigInteger(1, md.digest(input.toByteArray())).toString(16).padStart(32, '0')
}