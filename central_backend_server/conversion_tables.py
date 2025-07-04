# 10 examples from https://www.ugent.be/ge/nl/studenten/opleidingsspecifieke-informatie/stages/eindtermen/hoofdstuk3.pdf/@@download/file/Eindtermen%20Hfdst%20III.pdf
# Disease name, document file names (without extension), and difficulty to diagnose
# Difficulty was estimated with GPT-4o, but might not be accurate.
diseases = {
    "norovirus": [[],3],
    "acute bronchitis": [[], 3],
    "chronic obstructive pulmonary disease": [[], 7.5],
    "idiopathic pulmonary fibrosis": [[], 8],
    "Zollinger-Ellison syndrome": [[], 9],
    "functional dyspepsia": [[], 7],
    "celiac disease": [[], 8],
    "acute pancreatitis": [[], 7],
    "choledocholithiasis": [[], 8],
    "frozen shoulder": [[], 6],
    "external otitis": [[], 6.5],
    "infectious mononucleosis": [[], 6],
    "acute simple cystitis": [[], 3],

}

neuroticism_score_conversion_table = {
    "neuroticism": {
        0: "Consistently discusses even serious symptoms with a calm, detached tone, rarely expressing any worry or seeking emotional reassurance",
        1: "Usually maintains a calm demeanor when describing symptoms, seldom expressing anxiety and typically focusing on factual aspects",
        2: "Occasionally mentions mild worry or concern about symptoms but quickly pivots back to practical questions, generally remaining composed",
        3: "Expresses a moderate level of worry appropriate to the health concern, asking questions seeking both information and reasonable reassurance",
        4: "Often expresses significant anxiety about symptoms or potential outcomes, frequently asking 'what if' questions and seeking repeated reassurance from the doctor",
        5: "Consistently voices strong fears and worries about their health, often catastrophizing minor symptoms and persistently seeking reassurance"
    },
    "extraversion": {
        0: "Speaks only in minimal, quiet, one-or-two-word responses when directly questioned, never initiating conversation or small talk",
        1: "Rarely offers information beyond direct, brief answers, speaking softly and infrequently making unsolicited comments",
        2: "Answers questions politely but succinctly, seldom elaborating unprompted and maintaining a noticeably reserved, quiet demeanor",
        3: "Engages in polite back-and-forth, answers questions reasonably fully, and might offer a brief, relevant personal comment occasionally",
        4: "Often elaborates extensively on answers, readily initiates small talk or shares personal anecdotes, speaking with noticeable energy",
        5: "Consistently dominates the conversation with lengthy, energetic explanations and frequent personal stories, often filling any potential silences"
    },
    "openness": {
        0: "Consistently dismisses any non-standard treatment options mentioned and asks only about the most practical, established procedures",
        1: "Frequently steers the conversation back to concrete symptoms and immediate practical steps, rarely asking 'why' things work",
        2: "Occasionally asks a clarifying question about the basic mechanisms but primarily focuses on routine and known procedures",
        3: "Asks standard questions about the diagnosis and treatment plan, accepting information straightforwardly without much speculation or resistance",
        4: "Often asks speculative 'what if' questions about their condition or expresses curiosity about the underlying biological processes involved",
        5: "Consistently brings up alternative therapies or research they've read, eagerly exploring various theoretical possibilities for their condition"
    },
    "agreeableness": {
        0: "Consistently voices suspicion about the diagnosis or doctor's motives, frequently using challenging or critical language towards recommendations",
        1: "Often questions the doctor's suggestions or expertise, expressing skepticism about the necessity or effectiveness of his utterances",
        2: "Occasionally voices mild disagreement or doubt about a recommendation, asking probing questions before reluctantly agreeing",
        3: "Generally cooperates with the doctor's requests and asks questions politely, expressing concerns in a non-confrontational manner",
        4: "Often expresses explicit trust and gratitude towards the doctor, readily agreeing with suggestions with minimal questioning",
        5: "Consistently defers to the doctor's judgment with strong verbal agreement, frequently offering praise and avoiding any hint of conflict"
    },
    "conscientiousness": {
        0: "Consistently gives vague, disorganized accounts of symptoms and frequently mentions forgetting instructions or medication doses",
        1: "Often struggles to recall specific details like symptom timelines or medication names, needing frequent prompting from the doctor",
        2: "Sometimes provides incomplete information or needs reminders about previous advice, occasionally mentioning difficulties sticking to the plan",
        3: "Provides a reasonably clear account of their main issues and generally affirms understanding of instructions, asking a few basic clarifying questions",
        4: "Often comes prepared with specific notes or a list of questions and frequently asks for detailed clarification on treatment instructions to ensure accuracy",
        5: "Consistently presents detailed, often written, logs of symptoms and medication adherence, meticulously double-checking every aspect of the treatment plan"
    }
}

def translate_score(dimension, score):
    """
    Translates a score from the Big Five personality test to a description.

    Args:
        dimension (str): The dimension of the Big Five personality test.
        score (int): The score on the dimension.

    Returns:
        str: The description of the score.
    """
    table = neuroticism_score_conversion_table

    if dimension in table and score in table[dimension]:
        return table[dimension][score]
    else:
        return "Invalid dimension or score"

furhat_faces_list = """- Alex: white male, blue eyes
- Brooklyn: African female, average aged, dark eyes
- Chen: Asian middle-aged to young adult person, can be both male and female
- Dorothy: elderly white female, pale, blue eyes
- Fedora: white young adult Muslim female, blue eyes
- Fernando: African average middle-aged male
- Gyeong: Asian elderly female
- Hayden: African young adult female, clear skin
- Isabel: white young adult to middle-aged female, make upped
- James: white young adult male, very Caucasian
- Jamie: white young adult male, very Caucasian, somewhat innocent looking
- Jamie: white young adult female, very Caucasian
- Kione: African young adult female, clear skin, darker skin than Hayden
- Lamin: African young to middle aged person, can be both male or female.
- Marty: white young to middle aged male
- Maurice: African middle aged to elderly male
- Nazar: white Muslim young adult female
- Omar: white Muslim young adult male
- Patricia: white Muslim young adult to middle aged female
- Rania: white young adult to middle aged female
- Samuel: Caucasian tanned young adult to middle aged male
- Vinnie: white pale young adult female
- Yi: Asian young adult female
- Yumi: Asian young adult to middle aged female
- Zhen: Asian middle aged female"""

furhat_elevenlabs_voices_list = """- Aria: female, middle-aged, American, expressive, social media
Roger: male, middle-aged, American, confident, social media
Sarah: female, young, American, soft, news
Laura: female, young, American, upbeat, social media
Charlie: male, middle-aged, Australian, natural, conversational
George: male, middle-aged, British, warm, narration
Callum: male, middle-aged, Transatlantic, intense, characters
River: non-binary, middle-aged, American, confident, social media
Liam: male, young, American, articulate, narration
Charlotte: female, young, Swedish, seductive, characters
Alice: female, middle-aged, British, confident, news
Matilda: female, middle-aged, American, friendly, narration
Will: male, young, American, friendly, social media
Jessica: female, young, American, expressive, conversational
Eric: male, middle-aged, American, friendly, conversational
Chris: male, middle-aged, American, casual, conversational
Brian: male, middle-aged, American, deep, narration
Daniel: male, middle-aged, British, authoritative, news
Lily: female, middle-aged, British, warm, narration
Bill: male, old, American, trustworthy, narration
"""