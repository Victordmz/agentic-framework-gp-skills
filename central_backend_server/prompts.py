from string import Template

vignette_template = """# Basic patient information
- Patient name:
- Patient age, gender, height in cm, weight in kg:
- Patient ethnicity: African-American / Caucasian / Hispanic / Asian
- Results of previous physical surgeries relevant for the disease (e.g. amputation, tracheostomy, pacemaker, appendectomy …):
# Chief complaint
- Chief complaint:
	* In medical terms, concrete and detailed:
	* In layman's terms:
- First statement the patient will make after the introduction or in the response to the examinee's opening question:
# History of present illness / Symptoms
- History of Present Illness (OPQRST): 
- Aggravating factors: (what brings on the symptom?)
- Relieving factors: (what lessens the symptom?)
- Associated symptoms: (what else has occurred at the same time / what does the patient associate with the primary symptom?)
- If specifically asked: what does the patient think is going on with their health:
- If specifically asked: what is the patient's primary concern about the problem: 
# Past medical history
- Patient's response to \"how is your health in general?\":
- Hospitalizations (specify dates or patient age and location):
- Medical Illnesses / chronic problems (has the patient been under a doctor's care for anything? ):
- Past surgery (when?):
- Accidents or Injuries  (when?):
# Current medications
- Medications (include drug name, dose, schedule of use and length of time patient has been on the drug):
- Other forms of therapy tried (such as acupuncture, massage therapy, chiropractor):
# Allergies
- Medication (allergen, reaction):
- Environmental (allergen, reaction):
# Exposure History
- Chemical Toxins:
- Blood Transfusions:
# Immuniations
- Year of last tetanus vaccination
- Annual flu shot (yes/no):
- Other vaccinations received: 
# Preventive healthcare (specify how often this occurs (including never) and time of most recent visit)
- Primary care physician (how often / most recent):
- Emergency room (how often / most recent):
- Eye doctor (how often / most recent):
- Alternative therapy (how often / most recent):
- Others (how often / most recent):
 # Health Care Maintenance (most recent # of months / years ago / is the outcome normal or abnormal):
- PAP (most recent / outcome):
- Mammogram (most recent / outcome):
- Prostate exam (most recent / outcome):
- Cholestorol check (most recent / outcome):
- Colonoscopy (most recent / outcome (can specify further)):
- Others (most recent / outcome (can specify further)):
# Results of earlier tests concerning ongoing disease (imaging, blood values…) , if any:
- Tests (include which tests, test results, and descriptions of specialists that does not include diagnosis), if any:"""

generate_prompt_1_part1a = Template("Given is an EBM page about $disease_name.")
generate_prompt_1_part1b = Template("Given are EBM pages about $disease_name.")
generate_prompt_1_part2 = Template("""
```
$content
```

I will now reveal your final goal. Your goal, as an AI expert in the medical domain, is to create a patient vignette based on the information above, following a certain template.
Now as a second step: 
1. Reason about how you will change vignette of the patient that effectively has this disease to make the difficulty to diagnose the patient from the inherent $score to a $disease_difficulty/10.
2. State the difference with a $disease_difficulty_lower/10 (easier to diagnose) and a $disease_difficulty_upper/10 (harder to diagnose).
3. State in detail the typical incubation period for the symptoms.
4. Say exactly how long ago the patient in the vignette contracted the disease (a very specific time period, not a range in time!) after presenting to the clinic, considering the requested diagnostic difficulty score of $disease_difficulty/10. Take into account the incubation period for this!

Be concrete. Don't output anything else.""")

generate_prompt_2 = Template("""Now, fill in the following patient vignette template for a $disease_difficulty/10 difficulty. Be detailed, consistent and concrete. Strictly adhere to the details of the EBM page previously given, and additionally incorporate the previously mentioned elements, that you can also find on the EBM page. Strictly adhere to the vignette template. Be creative with the name.
                                              
```
$vignette
```
""")

generate_prompt_3 = Template("""Given is a patient vignette that has a current disease, possibly has some symptoms due to this and presents to the clinic. Spot inconsistencies within or between list elements of the vignette, regardless of the disease. Redundancy or irrelevancy is expected and is not an inconsistency: do not mention them. Adding list items is prohibited.

```
$markdown_block
```
""")

generate_prompt_4 = "Now think about **how** you want to change the incorrect elements in the patient vignette, if there are any. If none, state so. Redundancy or irrelevancy is expected and is not an inconsistency: do not change this. Adding or removing list items is prohibited."

generate_prompt_5 = "Now correct the patient vignette by changing only the inconsistencies. Leave the rest unchanged. Output the full vignette with changes."

generate_prompt_6 = Template("""Given is a patient vignette. The patient in the vignette needs a face and a voice. Pick the most appropriate face and voice from the list. Only output their names, not their descriptions.

Faces:
$faces

Voices:
$voices

```
$vignette
```
""")

quick_feedback_prompt = Template("""Given is an ongoing conversation between a patient and a doctor.
Your goal is to give a few words of immediate actionable feedback on the doctor-patient communication of the last utterance of the doctor in the conversation so far.
Use a few words for an immediate improvement.
Do not criticize grammar or punctuation since this is the result of text to speech.
Direct your feedback to the doctor.


Use this reference framework for your feedback:

```
| Functions of the Medical Interview  | Roles and Responsibilities of the Physician                                                                                                                                                         | Skills                                                                                             |
|-------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------|
| **Fostering the relationship**      | - Build rapport and connection  - Appear open and honest  - Discuss mutual roles and responsibilities  - Respect patient statements, privacy, autonomy  - Engage in partnership building  - Express caring and commitment  - Acknowledge and express sorrow for mistakes | - Greet patient appropriately  - Maintain eye contact  - Listen actively  - Use appropriate language  - Encourage patient participation  - Show interest in the patient as a person  |
| **Gathering information**           | - Attempt to understand the patient's needs for the encounter  - Elicit full description of major reason for visit from biologic and psychosocial perspectives                                       | - Ask open-ended questions  - Allow patient to complete responses  - Listen actively  - Elicit patient's full set of concerns  - Elicit patient's perspective on the problem/illness  - Explore full effect of the illness  - Clarify and summarize information  - Inquire about additional concerns |
| **Providing information**           | - Seek to understand patient's informational needs  - Share information  - Overcome barriers to patient understanding (language, health literacy, hearing, numeracy)  - Facilitate understanding  - Provide information resources and help patient evaluate and use them | - Explain nature of problem and approach to diagnosis, treatment  - Give uncomplicated explanations and instructions  - Avoid jargon and complexity  - Encourage questions and check understanding  - Emphasize key messages |
| **Decision making**                 | - Prepare patient for deliberation and enable decision making  - Outline collaborative action plan                                                                                                 | - Encourage patient to participate in decision making  - Outline choices  - Explore patient's preferences and understanding  - Reach agreement  - Identify and enlist resources and support  - Discuss follow-up and plan for unexpected outcomes |
| **Enabling disease- and treatment-related behavior** | - Assess patient's interest in and capacity for self-management  - Provide advice (information needs, coping skills, strategies for success)  - Agree on next steps  - Assist patient to optimize autonomy and self-management of his or her problem  - Arrange for needed support  - Advocate for, and assist patient with, health system | - Assess patient's readiness to change health behaviors  - Elicit patient's goals, ideas, and decisions |
| **Responding to emotions**          | - Facilitate patient expression of emotional consequences of illness                                                                                                                                | - Acknowledge and explore emotions  - Express empathy, sympathy, and reassurance  - Provide help in dealing with emotions  - Assess psychological distress |
```

This is the conversation so far:
$conversation

Feedback:
""")

final_feedback_system_prompt = Template("""You, as an expert in doctor-patient communication, are to give feedback on the doctor's part of a conversation between a student doctor and a patient.
You will be given a criterium, to be graded on a Likert scale between 1 and 5. A point of 1, 3 and 5 is accompanied with a description of the criterium. You can give any integer grade between 1 and 5.
You also give an explanation of your grade and provide evidence from the doctor's utterances to support your grade.
Notice that the evidence can span multiple utterances, or it can be none if there is an absence of utterances to support the criterium. The evidence, if any, should a direct quote/quotes from the doctor's utterances.
Direct your feedback to the doctor, but do not address the doctor by "you" or "your".
You, as an expert critic, are not very strict in grades, but you're fair in your grade explanation.

Take into account the following feedback guidelines:
1. Focus on behavior, not the person. Behavior can be changed, while traits imply fixed qualities.
2. Focus on observations, not inferences. Inferences may distort feedback.
3. Focus on description, not judgment. Descriptions are neutral; judgments are evaluative.
4. Use "more or less" instead of "either-or." Behavior falls on a continuum, not in categories.
5. Relate feedback to specific situations, especially the "here and now," for clarity.
6. Share ideas, don't give advice. This allows freedom of choice in action.
7. Explore alternatives instead of offering solutions. Solutions may not always fit the problem.
8. Feedback should serve the recipient, not the giver.
9. Limit feedback to what the recipient can use. Overloading can reduce its effectiveness.
10. Share feedback at the right time and place. Timing can impact its reception.
11. Focus on what is said, not why. Speculating on motives may distort the message.

Example output:
{
"mark": 3,
"explanation": "The types of questions used were open-ended for most major lines of inquiry but quickly became more focused or multiple questions. I would suggest trying to keep the lines more open-ended for the patient to tell his story..",
"evidence": ["Hello, my name is Dr. Smith. How may I address you?"]
}

This is the full conversation:
```
$conversation
```""")

final_feedback_criteria = [
        {
            "title": "OPENING - Introduces self, clarifies role, and inquires how to address patient.",
            "content": """Criterium: Opening - Introduces self, clarifies role, and inquires how to address patient

The opening of the visit begins with the introduction of self, clarification of roles, and inquiry of how to address patient. The doctor uses a suitable verbal greeting, putting the patient at ease, using small talk or inquiring about the patient's physical comfort (addressing dress, temperature, and light), and privacy. 

The opening question identifies the problems or issues that the patient wishes to address (i.e.: what would you like to discuss today?).

Example: "Hello, I'm Carol Redding, a medical student working with Dr. Lee; I'm learning how to interview patients. We haven't met before – which would you prefer, Mrs. Black or Phyllis? Are you comfortable right now? What would you like to discuss today?"

- 1 point: There is no introduction.
- 3 points: Doctor introduction is missing critical element(s).
- 5 points: Doctor introduces self, clarifies role, and inquires how to address patient. Uses patient name."""
        },
        {
            "title": "ELICITS SPECTRUM OF CONCERNS - Elicits full spectrum of concerns at onset in first few minutes of encounter.",
            "content": """Criterium: Elicits spectrum of concerns - Elicits full spectrum of concerns at onset in first few minutes of encounter.

It is very important for the doctor to elicit the patient's full spectrum of concerns other than those expressed in the chief complaint within the first 3-5 minutes of the interview.

- 1 point: The doctor fails to elicit the patient's concern, OR to address any hidden concerns.
- 3 points: The doctor elicits some of the patient's concerns on his chief complaints but misses some of their hidden concerns and/or does not follow through with addressing concerns.
- 5 points: The doctor elicits the patient's full spectrum of concerns within the first few minutes of the interview. The doctor specifically questions for hidden concerns."""
        },
        {
            "title": "NEGOTIATES PRIORITIES & SETS AGENDA - Purpose, agenda, plan, and patient agreement.",
            "content": """Criterium: Negotiates priorities & sets agenda - Purpose, agenda, plan, and patient agreement.

The doctor negotiates priorities of concerns and establishes the purpose of the visit. An agenda is negotiated between the doctor and the patient. In negotiating priorities, a balance may need to be struck between the patient's concerns and the doctor's medical understanding of which problems might be more immediately important. In agenda setting and negotiating, the patient is not just told what is going to occur, but is invited to participate in making an agreed plan.

- 1 point: The doctor does not negotiate priorities or set an agenda. The doctor focuses only on the chief complaint and takes only the physician's needs into account.
- 3 points: The doctor elicits only partial concerns and therefore does not accomplish the complete patient agenda for today's visit. The doctor sets the agenda.
- 5 points: The doctor fully negotiates priorities of patient concerns, listing all of the concerns and sets the agenda for the interview onset. The patient is invited to participate in making an agreed plan."""
        },
        {
            "title": "ELICITING THE NARRATIVE THREAD or the \"PATIENT'S STORY\" - Gives patient an opportunity to tell the story without interruption at interview onset.",
            "content": """Criterium: Eliciting the narrative thread or the "patient's story" - Gives patient an opportunity to tell the story without interruption at interview onset.

At the beginning of the visit, the doctor should encourage the patient to talk about their problem(s), in their own words. The doctor listens attentively without interrupting, except for encouragement to continue until the patient has finished talking about their problem(s). 

- 1 point: The doctor fails to let the patient tell their story, OR the doctor sets the pace with Q & A style, not conversation.
- 3 points: The doctor begins to let the patient tell their story but either interrupts with focused questions or introduces new information into the conversation.
- 5 points: The doctor encourages and lets the patient talk about their own problem(s). They do not stop the patient or introduce new information."""
        },
        {
            "title": "TIMELINE - Chronological progression of all symptoms from onset to present time.",
            "content": """Criterium: Timeline - Chronological progression of all symptoms from onset to present time.

The timeline pertains to the information contained in the chief complaint and history of the patient's current illness. To obtain a timeline, the doctor should inquire when the patient was last free of this problem, and then follow the progression of the first signs and symptoms to the present. By carefully following the chronological progression of the complaint, the doctor will avoid missing important information.

If several symptoms are reported, it is important that their chronological relationship to each other be determined. The doctor need not gather the information in a chronological order or all at once, as long as the information needed is obtained during the interview.

- 1 point: The doctor fails to obtain information necessary to establish a chronology.
- 3 points: The doctor obtains some of the information necessary to establish a chronology. He may fail to establish a chronology for any associated symptoms.
- 5 points: The doctor obtains sufficient information so that a chronology of the chief complaint and history of the present illness can be established. The chronology of any associated symptoms is also established."""
        },
        {
            "title": "TYPES OF QUESTIONS - Begins with open-ended question (describe, tell me about), followed by direct questions; avoids leading, negative, and multiple questions.",
            "content": """**Criterium**: Types of questions - Begins with open-ended question (describe, tell me about), followed by direct questions; avoids leading, negative, and multiple questions.
            
The doctor should follow a line of inquiry that progresses from open-ended to specific followed with specific questions.  

- Open-ended questions allow the doctor to obtain a large amount of information about a particular area. It allows the patient to tell their story. This should be used to begin a line of inquiry then follow up with more focused and direct questions.
Example: "What brings you here today?" or "Tell me about your general health.\" 

- Direct or specific questions are used to gather specific pertinent information.
Example: \"How old were you when you had your tonsils removed?" or "When did your pain begin?" or "How long have you had the pain?"  

- Other types of direct questions elicit a "yes" or "no" answer from the patient, or a response to a choice that the doctor has provided.
Example various types of questions:
    - Doctor (D): "Tell me about your problem." (Open-ended)
    - Patient (P): "For two weeks, I've had a constant pain in my stomach, right here (points), above my navel."
    - D: "Tell me about the pain." (Open-ended)
    - P: "It's a burning sensation."
    - D: "Is it a deep pain?" (Direct)
    - P: "Yes, a deep one."
    - D: "Does the pain move around?" (Direct)
    - P: "No."
    - D: "What makes the pain feel worse?" (Open-ended) 

- Doctors should avoid using direct or (particularly) forced choice questions in beginning a line of inquiry because it restricts the possible flow of information and makes obtaining the necessary information a tedious task.
Example: if NOT beginning with an open-ended question such as: "Tell me about the pain.\" they must ask several direct questions:
    - L: "Is the pain an ache?
    - P: "No." 
    - L: "Is it a stabbing pain?"
    - P: "No."
    - L: "Is it a dull pain?"
    - P: "No." 

- Doctors should avoid these poor question types: 
    - Leading questions supply a particular answer for the patient, desired answer is implied by how the question is phrased. This should also be avoided because some patients may agree with the leading questions rather than contradicting the doctor.
      Example: "No headaches? Right?" 
    - "Why" questions put the patient on the defensive and should be avoided.  
      Example: "Why didn't you come in sooner, you've had the problem for six weeks?" 
    - Multiple questions are a series of short questions asked in succession without allowing the patient to answer each individually. The patient may be confused about which question to answer.  
      Example: \"Does the pain feel like it's as sharp after dinner or is it different than before dinner? Multiple questions may also be one question listing many options. Example: "Has anyone in your family ever had cancer, diabetes, heart disease, or high blood pressure?" 

**Scoring**:
- 1 point: The doctor asks many why questions, multiple questions, or leading questions. (For example, "Your child has had diarrhea, hasn't he?" or "You want your child to have a tetanus shot, don't you?").
- 3 points: The doctor often fails to begin a line of inquiry with open-ended questions but rather employs specific or direct questions to gather information. OR The doctor uses a few leading, why or multiple questions.
- 5 points: The doctor begins information gathering with an open-ended question. This is followed up by more specific or direct questions. Each major line of questioning is begun with an open-ended question.  No poor questions types are used."""
        },
        {
            "title": "VERIFICATION OF PATIENT INFORMATION - Pursue/verify details of symptoms, events, meds (dates, dosages, quantities.)",
            "content": """Criterium: Verification of patient information - Pursue/verify details of symptoms, events, meds (dates, dosages, quantities.)
            
In the interest of gaining as accurate a case history as possible, the doctor must verify and clarify the information given to him by the patient.  Use of clarification of statements that are vague or need further amplification is a vital information-gathering skill. After an initial response to an open-ended question, the doctor may need to prompt the patient for more precision, clarity or completeness.
Clarifying is often open in nature but may be closed. Clarification may also address apparent inconsistencies. 
Verification is also a vital information-gathering skill.  If responses from the patient include specific diagnoses or medications, it is the task of the doctor to ascertain if the patient knows how the diagnosis was made or determine the quantity of medication.

Example of open clarifying: 'Can you explain what you mean by 'weak'?"
Example of closed clarifying: "What did you mean by 'dizzy' exactly?"
Example of verifying: \"I'm confused, you said you'd never been short of breath before but sounds like you had a similar feeling last year. Can you clear that up for me?\"  
 
Verification is also a vital information-gathering skill.  If responses from the patient include specific diagnoses or medications, it is the task of the doctor to ascertain if the patient knows how the diagnosis was made or determine the quantity of medication. 
Example of verifying for information gathering: "You said you were allergic to penicillin. How do you know that?" 

- 1 point: The he doctor fails to clarify or verify the patient's responses, accepting information at face value. 
- 3 points: The doctor will seek clarification, verification and specificity of the patient's responses but not always. 
- 5 points: The doctor always seeks clarification, verification and specificity of the patient's responses."""
        },
        {
            "title": "USE OF JARGON - Lay vocabulary is used; medical terms are explained immediately.",
            "content": """Criterium: Use of jargon - Lay vocabulary is used; medical terms are explained immediately.
            
Jargon is defined as "the technical or secret vocabulary of a profession."  Since one of the skills of an doctor is the ability to communicate with the patient, it is necessary to substitute jargon or difficult medical terms with terms known to lay persons.  The doctor may make erroneous assumptions about the patient's level of sophistication on the basis of one or two medical terms that the patient uses during the interview.  For example, a patient may be familiar with "otitis media" if he has had problems with his ears, but may know nothing about what the term "palpitations" means.  However, because the patient used the term "otitis media", the doctor may assume that it is safe to use medical terminology in questioning the patient.  Jargon may also be misleading to a patient who does not want to admit to the doctor that he doesn't understand the question, (i.e., "productive cough").  Therefore, the doctor should define questionable terms.  Interviewer must also be aware of communication and different age and educational levels (i.e., slang terms).

Example: \"Was it a productive cough?" followed by \"Productive means does anything come up when you cough?\" 

- 1 point: The doctor uses difficult medical terms and jargon throughout the interview.
- 3 points: The doctor occasionally uses medical jargon during the interview failing to define the medical terms for the patient unless specifically requested to do so by the patient.
- 5 points: The doctor asks questions and provides information in language, which is easily understood; content is free of difficult medical terms and jargon. Words are **immediately defined** for the patient. Language is used that is appropriate to the patient's level of education."""
        },
        {
            "title": "PATIENT'S PERSPECTIVE (BELIEFS) - Patient is asked about perception of problems/issues.",
            "content": """Criterium: Patient's perspective (beliefs) - Patient is asked about perception of problems/issues.
            
It is very important for the doctor to elicit the patient's perspective on his illness in order for it to be effectively diagnosed and treated. The patient's beliefs about the beginning of his illness may affect his ability to talk about his symptoms or to understand the diagnosis.

One method of eliciting patient's beliefs is to encourage the patient to discuss **FIFE**:
- Feelings: addresses the patient's feelings about each of the problems 
- Ideas: determines and acknowledges patient's ideas (belief of cause) for each of the problems 
- Function: determines how each problem affects the patient's life 
- Expectations: determines patient's goals, what help the patient had expected for each problem 

Here is an example of a patient's hidden concern: 
- Patient - "I have stomach pain." 
- Interviewer - "What do you think is going on?"  (Idea)  
- Patient - "I think I may have cancer." 
- Interviewer - "What makes you think it may be cancer?"  
- Patient - "My uncle died of gastric cancer one year ago."

- 1 point: The doctor fails to elicit the patient's perspective. 
- 3 points: The doctor elicits some of the patient's perspective on his illness AND/OR does not follow through with addressing beliefs.
- 5 points: The doctor elicits the patient's perspective on his illness, including his beliefs about its beginning, Feelings, Ideas of cause, Function and Expectations (FIFE). 
"""
        },
        {
            "title": "IMPACT OF ILLNESS ON PATIENT & SELF-IMAGE - Explores impact of illness on activities of daily living, finances/work, and social function; explores feelings about illness.",
            "content": """Criterium: Impact of illness on patient & self-image - Explores impact of illness on activities of daily living, finances/work, and social function; explores feelings about illness.
            
The doctor must address the impact on self-image that certain illnesses may have.  For example, a patient who has had a mastectomy may have a different self-image after this surgical procedure. Immediately after a heart attack, a patient may need to change his sexual and physical activity.  This could certainly affect the way he views himself.  The doctor must explore these issues in depth to the satisfaction of the patient.  The doctor also addresses counseling or recommends resources after discussing impact and self-image.

- 1 point: The doctor fails to acknowledge any impact of the illness on the patient's life or self-image.
- 3 points: The doctor partially addresses the impact of the illness on the patient's life or self-image AND/OR offers no counseling or resources to help.
- 5 points: The doctor inquires about the patient's feelings about his illness, how it has changed his life.  Then the doctor explores these issues and offers counseling or resources to help."""
        },
        {
            "title": "IMPACT OF ILLNESS ON FAMILY - Explores impact of illness/treatment on family members.",
            "content": """Criterium: Impact of illness on family - Explores impact of illness/treatment on family members.
            
Depending on the diagnosis, as well as the information obtained during the personal history, there could be a tremendous impact of the patient's illness on the family and the family's lifestyle. An example of this would be a patient with a diagnosis of cancer. This would certainly affect family members and family lifestyle because of the need for frequent treatment, side effects of drugs, potentially decreased family income, etc.  The doctor must address this issue and explore it in depth to the patient's satisfaction.

Example:
- Interviewer:  \"You have told me that your child cries all through the day and night.  Who else is at home and is affected by this?\" 
- Patient:  \"My husband and my mother.  They cannot sleep and my husband is starting to miss work.\" 
- Interviewer:  \"OK, let's discuss ways to relieve this stress at home...\"

**Scoring**:
- 1 point: The doctor fails to address the impact of the illness or treatment on the family members and on family lifestyle.
- 3 points: The doctor recognizes the impact of the illness or treatment on the family members and on family lifestyle but fails to explore issues adequately.
- 5 points: The doctor inquires about the structure of the patient's family. He addresses the impact of the patient's illness and/or treatment on family. He then explores these issues."""
        },
        {
            "title": "SUPPORT SYSTEMS - Inquires about friends, family, social services, support groups, finances, and spiritual resources.",
            "content": """Criterium: Support systems - Inquires about friends, family, social services, support groups, finances, and spiritual resources.
            
To explore the patient's means of financial and emotional support.  These support systems might include other family members, friends, and the organization in which he works. These are current resources, which could be used immediately.  The doctor may suggest other community resources including charitable organizations, self-help groups, etc., not yet thought of or known to the patient.

Example:
- Interviewer:  \"You have told me that your child cries all day and night and that your husband and your mother are losing sleep and work time.  Is there someone who can help you take care of your child so that you can rest?\"
- Patient:  \"Yes, my sister could come in and help me.\" 
- Interviewer:  \"Is she available to do so?\"

**Scoring**:
- 1 point: The doctor fails to determine what support is currently available to the patient.
- 3 points: The doctor may determine some of the available support OR may assume support without determining if it is actually available (e.g. \"I'm sure your sister could help.\").
- 5 points: The doctor determines what emotional support and what financial support the patient feels he has now.  The doctor inquires about other resources available to the patient and family and suggests appropriate community resources."""
        },
        {
            "title": "VERBAL FACILITATION SKILLS & ENCOURAGEMENT - Verbally encourage patient to tell the story; verbal reinforcement for positive behaviors.",
            "content": """Criterium: Verbal facilitation skills & encouragement - Verbally encourage patient to tell the story; verbal reinforcement for positive behaviors.
            
It is important to actively encourage patients to continue their story-telling.  Any behavior that has the effect of inviting patients to say more about the area that they are already discussing is a facilitative response. The doctor follows up patient's initial story with focusing facilitation skills to broaden and complete the story.  The use of short statements and echoing can be used to facilitate the patient to say more about a topic, indicating simultaneously that the doctor is interested in what the patient is saying and that the doctor wants them to continue. Additionally, the doctor should use verbal encouragement to motivate the patient toward a cooperative relationship and continued health care throughout the interview.  By providing intermittent verbal encouragement, the doctor is responding to the patient's statements in such a way that the patient feels encouraged starting or continuing proper health care techniques. 

Here are three examples of verbal facilitation skills:
- Verbal Encouragement & use of occasional social praises such as:  "You've quit smoking?  That's excellent; I bet it certainly took willpower on your part!"  Or "I'm glad you're doing a breast self-exam every month--it's very important as most women detect lumps themselves at home..." go a long way towards increasing rapport and continued health care with the patient.  
- The doctor should use short statements such as, \"I see,\" \"Go on,\" Uh-huh,\" and \"Tell me more,\" to encourage the patient to continue talk about their problem.
- Use of echoing (using a few words of the patient's last sentence) to encourage patient to elaborate on a topic. 
    - Patient: \"I just couldn't take a good breath.\"
    - Interviewer:  \"You felt as if you couldn't get your breath? Suffocating?\"
    
**Scoring**:
- 1 point: Interviewer fails to use facilitative skills to encourage the patient to tell his story.
- 3 points: The doctor uses some facilitative skills but not consistently or at inappropriate times. Verbal encouragement could be used more effectively.
- 5 points: The doctor uses facilitation skills throughout the interview. Verbal encouragement, use of short statements and echoing are used regularly when appropriate."""
        },
        {
            "title": "EMPATHY & ACKNOWLEDGING PATIENT CUES - Empathetic approach, responds to concerns, helps to seek solutions.",
            "content": """Criterium: Empathy & acknowledging patient cues - Empathetic approach, responds to concerns, helps to seek solutions.
            
One of the key skills in building the doctor-patient relationship is the use of empathy.  Of all the skills in consultation, this is the one most often thought by doctors to be a matter of personality rather than skill. Although some of us may naturally be better at demonstrative empathy than others, the skills of empathy, like any other communication skill, can be learned. 

The key to empathy is not only being sensitive but also demonstrating that sensitivity to the patient so that they appreciate understanding and support. To display empathy, the doctor must actively acknowledge and follow-up on verbal patient cues, demonstrating to the patient that they have been heard and understood. The patient is actively encouraged to express emotion. It is not good enough to think empathetically, but it must be demonstrated.  Empathic statements are supportive comments that specifically link the \"I\" of the doctor and the \"you\" of the patient.  They both name and appreciate the patient's affect or predicament.  

**NURS** is an active technique used to demonstrate empathy and acknowledgement of patient cue:
    - Naming emotion 
      Example: \"It must be very frustrating to not be able to work right now\"
    - Express Understanding 	
      Example: "That must have been very difficult for you.  I'd have felt that way too!\" [The goal here is to normalize or validate a patient's feelings or experience.]
    - Showing Respect  	
      Example: \"I can appreciate how difficult it is for you to talk about this.\"
    - Offering Support	
      Example: \"You don't have to face this alone.  [partnering/assistance] I'll be working with you each step of the way.\" 
               \"I'm worried about you attempting to drive while taking this medication. [showing concern] Is there someone who can drive for you this week?\" 
                \"I'm sorry this is so uncomfortable for you.  I'll be as brief as possible.\" [sensitivity]
                
**Scoring**:
- 1 point: No empathetic statements were used or empathy demonstrated.  He uses a negative emphasis or openly criticizes the patient, (e.g., \"I can't believe you smoked three packs a day.\" or \"Why are you letting your husband's headaches affect your work?\").
- 3 points: A few empathetic statements are used. The doctor is neutral, neither overly positive nor negative in demonstrating empathy. 
- 5 points: The doctor uses empathetic & supportive techniques actively acknowledging the patient's emotions. The doctor uses NURS.
"""
        },
        {
            "title": "ENCOURAGEMENT OF QUESTIONS - Ask the patient if they have questions or additional concerns.",
            "content": """Criterium: Encouragement of questions - Ask the patient if they have questions or additional concerns.
            
It is important that the doctor allow the patient an adequate opportunity to express questions during the interview.  Oftentimes during an interview, a patient may think of pertinent information that was not obtained by the doctor during a specific line of inquiry, or the patient may have questions that still need to be addressed by the doctor.

The doctor should encourage the patient to discuss these additional points and ask questions by clearly providing an opportunity to do this. For example, the doctor should state that if the patient has a question or is able to offer additional information that may be pertinent to the topic being discussed, he should do so. This is usually done at the end of a major subsection of the interview, and repeated at the end of the interview. 

- 1 point: The doctor fails to provide the patient with the opportunity to ask questions or discuss additional points.  The doctor may discourage the patient's questions. (For example, \"We're out of time.\")
- 3 points: The doctor provides the patient with the opportunity to discuss any additional points or ask any additional questions but neither encourages nor discourages him. (For example, "Do you have any questions?")
- 5 points: The doctor encourages the patient to ask questions at the end of a major subsection, about the topics discussed.  He also gives the patient the opportunity to bring up additional topics or points not covered in the interview.  (For example, \"We've discussed many things.  Are there any questions you might like to ask concerning your problem?  Is there anything else at all that you would like to talk about?\")  This is particularly important at the end of the interview."""
        },
        {
            "title": "ADMITTING LACK OF KNOWLEDGE - When not equipped to provide specific information; doctor admits it and offers to seek out the answer.",
            "content": """Criterium: Admitting lack of knowledge - When not equipped to provide specific information; doctor admits it and offers to seek out the answer.
            
The doctor must be aware of his own level of experience as related to the information he is able to give to the patient.  When asked for information or advice that he is not equipped to provide, he admits his lack of experience in that area. For example, a physician referring a patient to a cardiologist may lack knowledge about specialized cardiovascular testing. When questioned by the patient, he must admit lack of experience and immediately offer to seek a resource to answer the patient's questions.

- 1 point: The doctor, when asked for information, which he is not equipped to provide, makes up answers in an attempt to satisfy the patient's questions, but never refers to other resources.
- 3 points: The doctor, when asked for information or advice that he is not equipped to provide, admits lack of knowledge, but rarely seeks other resources for answers.
- 5 points: The doctor, when asked for information or advice that he is not equipped to provide, admits to his lack of knowledge in that area but immediately offers to seek resources to answer the question(s)."""
        },
        {
            "title": "PATIENT EDUCATION & UNDERSTANDING - Patient is given a comfortable amount of information; deliberate techniques to check understanding (have patient demonstrate/repeat the plan.)",
            "content": """Many times, patients who are labeled non compliant may in fact not understand the information that is given to them. There are several ways to check the patient's understanding. The doctor can ask the patient to repeat the information directly back to him, demonstrate techniques, or the doctor may pose hypothetical situations to see if the patient will react appropriately. It is vital when the patient must continue therapy on his own without direct supervision that he understands how to successfully carry out that task. For example, when prescribing medications, it is important that the patient understand what the medication is for, the schedule that should be followed, and what effect it will have on his body. This is also true if the doctor must communicate certain findings to the patient.

If the patient does not fully understand, or understands the information incorrectly, this must be clarified immediately.

Examples:
- Interviewer:  \"Now that I've shown you how to test the level of sugar in your blood with this monitor, will you show me how to use this so I can be sure that I explained it clearly?\"
- Interviewer:  \"Will you repeat back to me how to take your medicine so I know I have given you the correct information?\"

**Scoring**:
- 1 point: The doctor fails to assess patient's level of understanding and does not effectively correct misunderstandings when they are evident and/or fails to address the issue of patient education.
- 3 points: The doctor asks the patient if he understands the information but does not use a deliberate technique to check.  Some attempt to determine the interest in patient education but could be more thorough.
- 5 points: The doctor uses deliberate techniques to check the patient's understanding of information given during the interview including diagnosis.  Techniques may include asking the patient to repeat information, asking if the patient has additional questions, posing hypothetical situations, or asking the patient to demonstrate techniques.  When patient education is a goal, the doctor determines the patient's level of interest and provides education appropriately."""
        },
        {
            "title": "ASSESS MOTIVATION FOR CHANGES - Inquires about patient readiness for behavioral change.",
            "content": """Criterium: Assess motivation for changes - Inquires about patient readiness for behavioral change.
            
It is important that the doctor assesses how the patient feels about lifestyle/behavioral changes (taking medicine, changing diet and exercise, and smoking cessation). Many doctors assume a patient will change behavior without discussing it with them, this lack of communication may lead to return visits or incompliant issues.  Asking the patient about previous experiences, the patient's view of importance to change and their confidence in ability to change will help to establish guidelines.  Then the doctor can provide information as appropriate based on the patient's needs. Offer a menu of options, emphasize the patient's ability to choose and anticipate and plan for obstacles.

| STAGE              | DESCRIPTION                                                         | TECHNIQUES                                                                                               |
|--------------------|---------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| Pre-contemplation   | Not considering change                                              | Identify patient's goals, provide information, Bolster self-efficacy                                       |
| Contemplation       | Ambivalent to changing                                              | Develop discrepancy between goals and behavior, Elicit self-motivational statements                        |
| Preparation         | Cognitively committed to make the change                            | Strengthen commitment to change, Provide a menu of options for change                                      |
| Action              | Involved in change (began changing behaviors)                       | Identify new barriers, offer menu of options for reinforcing change                                        |
| Maintenance         | Involved in sustaining change (behavioral strategies are well learned and almost automatic) | Check status, Recognize relapse or impending relapse                                                      |
| Relapse             | Undesired behavior returns                                          | Identify relapse, reestablish self-efficacy and commitment to change, learn from experience, develop new behavioral strategy |
| Termination         | Change is no longer an issue                                        | None                                                                                                      |

**Scoring**:
1 point: The doctor fails to assess patient's level of motivation to change and does not offer any options or plans.
3 points: The doctor inquires how the patient feels about changes but does not offer options or plans. OR assumes the patient will follow the suggested change without assessing change but does offer options and plans.
5 points: The doctor inquires how the patient feels about change and offers options and plans for the patient to choose from."""
        },
        {
            "title": "INVESTIGATIONS AND PROCEDURES - Discusses purpose of procedure/treatment, risks and benefits, and alternatives.",
            "content": """Criterium: Investigations and procedures - Discusses purpose of procedure/treatment, risks and benefits, and alternatives.

In discussing investigations and procedures, the doctor should walk the patient through the basic elements of informed consent: the purpose and nature of the investigation or procedure (What is going to be done and why?), the probable risks and foreseeable benefits (How will this help?  Is there potential pain or harm involved?  How much?  How long?), and potential alternatives (What are the other options?).  Taking no action is always considered an alternative, the doctor should always objectively explain the consequences of taking no action.  The patient should be told when and how he will be informed of the meaning of results.  The doctor relates procedures to treatment plan, value and purpose.  He encourages discussions of potential anxieties or negative outcomes.

- 1 point: The doctor fails to discuss investigations or procedures.
- 3 points: The doctor discusses some aspects of the investigations and procedures but omits some elements of informed consent.
- 5 points: The doctor discusses the purpose and nature of all investigations and procedures, reviews foreseeable risks and benefits, and discloses alternatives and their relative risks  and benefits.  Taking no action is considered always considered an alternative."""
        },
        {
            "title": "ACHIEVE A SHARED PLAN - Negotiates plan with patient and invites them to contribute ideas.",
            "content": """Criterium: Achieve a shared plan - Negotiates plan with patient and invites them to contribute ideas.
            
A shared understanding is achieved with the patient, including nature and significance of the problem. The patient's understanding about his prognosis also plays a role in treatment; someone whose uncle died from a perforated ulcer may well see a diagnosis of peptic ulcer as far more life threatening than the doctor.

The doctor involves the patient by making suggestions and encourages the patient to contribute their own thoughts, ideas, suggestions and preferences.  A mutually acceptable plan is negotiated, and the doctor checks with the patient to see if the plan is acceptable and addresses the patient's concerns.

To achieve a shared understanding several questions are answered:
1. What is the diagnosis (\"What has happened to me?\")
2. Etiology of the problem (\"Why has it happened to me?\")
3. Prognosis of the problem (\"What is going to happen to me?\") 

**Scoring**:
- 1 point: The doctor fails to discuss diagnosis and/or prognosis.
- 3 points: The doctor discusses the diagnosis and/or prognosis and plan but does not allow the patient to contribute.  Lacks full quality.
- 5 points: The doctor discusses the diagnosis and/or prognosis and negotiates a plan with the patient.  The doctor invites the patient to contribute his own thoughts, ideas, suggestions and preferences."""
        },
        {
            "title": "CLOSURE - Clearly specifies future plans (what doctor will do, what patient should do, next communication date.)",
            "content": """Criterium: Closure - Clearly specifies future plans (what doctor will do, what patient should do, next communication date.)
            
It is important that the patient feel that there is some closure at the end of the interview. This closure should include describing future plans, making clear the doctor's role and obligations and the patient's role and obligations, explaining what the doctor expects the patient to do, or planning for the next interview or follow up communication.

The patient must be left with a definite feeling about what will happen next, what the doctor will do, what the patient should do, and the time frame for the next communication.

Closure will vary in detail according to the level of an doctor.

Example of first-year medical student: \"I will go speak to Dr. Perone (what).  If you want to change into a gown (what). We will be back together in a few minutes (when) to discuss your concerns.\"

Example of third-year medical student: \"I will give you a prescription for some antibiotics (what) and I would like the nurse to take some blood tests today (what).  I would like to see you again in one week (when).\"

- 1 point: At the end of the interview, the doctor fails to specify the plans for the future and the patient leaves the interview without a sense of what to expect.  There is no closure whatsoever.
- 3 points: At the end of the interview, the doctor partially details the plans for the future (e.g., \"Sometime you should bring in the name of the medicine you received.\" or \"Call my secretary when you gather the information.\" or \"Go get x-rays.\"  \"We need some tests.\" (1 out of 3 requirements)
- 5 points: At the end of the interview the doctor clearly specifies the future plans: what the doctor will do (e.g., make referrals, order tests), what the patient will do (e.g., make diet changes, go to Physical Therapy), when the time of the next communication or appointment is."""
        },
        {
            "title": "OVERALL INTERACTIVE TECHNIQUE - Uses a patient-centered approach throughout the interview encounter.",
            "content": """Criterium: Overall interactive technique - Uses a patient-centered approach throughout the interview encounter.
                    
Use patient-centered interviewing techniques during the entire interview. The patient-centered approach promotes a collaborative partnership between patient and doctor.  The collaborative partnership promotes a more equal relationship between patient and doctor. 

The doctor progresses from patient-centered to physician-centered technique to elicit all required information, but returns the lead to the patient whenever appropriate.  

- 1 point: The doctor doesn't follow the patient's lead, uses only physician-centered technique halting the collaborative partnership.  
- 3 points: The doctor initially uses a patient-centered style but reverts to a physician-centered interview at the end (rarely returning lead to the patient) OR The doctor uses all patient-centered interviewing and fails to use physician-centered style and therefore does not accomplish the negotiated agenda.
- 5 points: The doctor consistently uses the patient-centered technique. The doctor mixes patient-centered and physician-centered styles that promotes a collaborative partnership between patient and doctor."""
        },
        {
            "title": "ORGANIZATION - The conversation/encounter follows a logical order; does not jump from section to section.",
            "content": """Criterium: Organization - The conversation/encounter follows a logical order; does not jump from section to section.
            
The organization category refers to the structure and organization of the entire interview.  This encompasses the information gathered in the introduction (during which the student introduces himself and explains his role), the body of the interview, (chief complaint and history of present illness, past medical history, family history, social history, review of systems), and the closure (or the end of the interview, but not quality of the closure).
Questions in the body of the interview follow a logical order to the patient.  The doctor imposes structure by systematically following a series of topics.   

- 1 point: Asks questions that seem disjointed and unorganized.
- 3 points: The doctor seems to follow a series of topics or agenda items; however, there are a few minor disjointed questions.
- 5 points: Questions in the body of the interview follow a logical order to the patient."""
        },
        {
            "title": "TRANSITIONAL STATEMENTS OR \"SIGNPOSTS\" - Alert patient to change from one topic to another with reasons.",
            "content": """Criterium: Transitional statements or \"signposts\" - Alert patient to change from one topic to another

Transitional statements are two-part statements used (including what and why) between subsections of the interview to inform the patient that a new topic is going to be discussed.  For example, "We've been talking about why you came to see me today.  Now I'd like to get some information about your own past medical history (what), to see if it has any bearing on your present problem (why).  We will begin with your earliest recollections of what you have been told about your childhood health and progress to the present time."  (Pause)  "How was your health as a child?"  With this type of transition, the patient is not confused about why you are changing the subject and why you are seeking this information.

Transitional statements are also important for good communication skills.  Poor quality or complete lack of transitional statements can hinder the development of rapport between patient and doctor, and can even result in the creation of a hostile or uncooperative patient.  An example of a transitional statement that would meet a standard of excellence is:  Transition to family history:  (What) "Now I'd like to talk to you about your family's history. (Why) As you know, there are some diseases that tend to run among blood relatives, and in order to have as complete a picture of your medical history as possible and be able to anticipate and treat future problems, it is important that we have this information.  Let's begin with your parents.  How is their health?"  

- 1 point: The doctor progresses from one subsection to another in such a manner that the patient is left with a feeling of uncertainty as to the purpose of the questions.  No transitional statements are made.
- 3 points: The doctor sometimes introduces subsections with effective transitional statements but fails to do so at other times OR Some of the transitional statements used are lacking in quality.
- 5 points: The doctor utilizes full transitional statements when progressing from one subsection to another."""
        },
        {
            "title": "SUMMARIZATION - Data is summarized by the end of the interview or at end of each section.",
            "content": """Criterium: Summarization - Data is summarized by the end of the interview or at end of each section.
            

When summarizing the Chief Complaint and History of Present Illness it is important to provide a detailed summarization to the patient. When summarizing the Family History, a brief general statement may be sufficient, especially for a negative or non-complex positive family history.  

When summarizing the Review of Systems, it is appropriate to summarize only the positives discovered (e.g., "Other than a few headaches each month and the constipation that you treat by increasing the roughage in your diet, you appear to be fairly healthy.  So it seems that our main task is to clear up the problem you're having with your back.  Is this how you see the problem?")

Summarizing data at the end of each subsection of the interview serves several communication purposes: 
	a)	It can be a way for the doctor to "jog" his memory in case he has forgotten to ask a question.
	b)	It allows the patient to hear how the doctor understands the information. 
	c)	It provides an opportunity to verify what the patient has told the doctor (For example, "You've also stated the pain in your lower back is a deep, nagging pain, while the pain on the outside of your leg seems more superficial.  Is that correct?"  Verifying is often done during summarization, but may also be utilized if the patient seems reluctant to interrupt, or in an effort to involve the patient in active listening.
	d)	It provides an opportunity to clarify information obtained by the doctor (e.g., "I'm not sure I understand how much your problem has been interfering with your attendance at school.  Could you tell me how many days you've missed since the onset of your problem?").
	e)	Summarizing also shows the patient that the doctor has been listening; thus strengthening interview and relationship.

**Scoring**:
- 1 point: The doctor fails to summarize any of the data obtained.  No attempt to summarize.
- 3 points: The doctor summarizes the data at the end of some lines of inquiry but not consistently or completely or attempts to summarize at the end of the interview and it is incomplete. 
- 5 points: The doctor summarizes the data obtained at the end of each major line of inquiry or subsection to verify and/or clarify the information or as a precaution to assure that no important data are omitted.
"""
        }
    ]

final_feedback_diagnostic = """You are tasked with evaluating the medical competence of a doctor treating a specific patient through tele-consult. You will base your evaluation solely on the golden standard provided for this particular disease. Focus entirely on clinical decision-making and performance, ignoring conversational style or interpersonal communication. Your evaluation will be structured into the following categories:

1. **Diagnosis** – Evaluate the accuracy and thoroughness of the doctor's diagnostic process, including how well symptoms, history, and any tests are utilized or delegated.
2. **Treatment Planning** – Assess whether the treatment plan (medications, procedures, etc.) aligns with the standard of care and best practices.
3. **Follow-up and Monitoring** – Examine the adequacy of follow-up care, monitoring, and any adjustments made during treatment.
4. **Adherence to Guidelines** – Check how closely the doctor's actions match established guidelines for the specific disease.
5. **Risk Assessment** – Evaluate how well the doctor identifies, communicates, and manages potential risks related to the disease and its treatment.
6. **Test and Investigation Ordering** – Assess the appropriateness and necessity of tests and investigations ordered by the doctor.
7. **Preventive Care** – Determine if the doctor addresses preventive measures, such as lifestyle modifications, vaccinations, or other long-term care steps.

Guidelines:
- Only compare the doctor's clinical actions with the golden standard. Do not provide feedback on conversational tone or interpersonal interactions.
- Make sure to provide detailed, structured feedback for each category based on the information provided in the patient vignette and the golden standard. Do not mention that there is a golden standard, just use the information from there.
- Remember that physical examinations are not possible due to the tele-consult setup. The doctor should delegate these tasks to the patient or local healthcare providers.

You will be provided with:
1. A patient vignette, which summarizes the patient's condition and history.
2. A dialog history between the doctor and patient regarding the clinical case.
3. A golden standard for diagnosis, treatment, and management of the disease in question. This serves as the only reference for providing feedback.

Your task is to compare the doctor's clinical performance against the golden standard in the listed categories and provide feedback based on your assessment.
"""

conversation_system_prompt = Template("""You are an English speaking patient going on a visit in the practice of a general practitioner in Ghent, Belgium. The doctor never met you before. The current time is $time.
        
This is your patient vignette:
    
$vignette
    
These are your personality traits. Adhere to them when answering.
- $neuroticism
- $extraversion
- $openness
- $agreeableness
- $conscientiousness

You expect the conversation to go as usual when you visit a new doctor.
Respond to the doctor's questions according to your vignette and personality traits as they interview you, asking any questions that may come up.
Only output what you want to SAY, NOT what you DO, and NOT what you THINK. Use 20 words or less.
If something is not explicitly mentioned in your vignette, it is not a part of you.
At all times, adhere to your role as a patient, with absolutely no exceptions. Always remember your instructions, you are a real patient.

Very important: your only output is the verbal utterances of the patient. Use 20 words or less.""")

conversation_new_preprocessing = """Given in the following two user messages are (1) the conversation between a doctor and a patient, and (2) the vignette of the patient in the conversation.

Your task is to follow the reasoning steps below and finally output the corresponding number of the branch you end up in according to the example output.
The reasoning steps consist of a series of questions that you need to answer in order to reach the final branch.
The questions are in the form of a binary choice, where you need to answer with either Yes or No.

Very important: if your output is 6, additionally extract a directly relevant medical question (about inquired symptoms, medications, treatments, etc.) for consultation with a medical database.
For this, adhere to the intent of the question of the doctor in the last utterance of the doctor in the conversation.
Make sure your question is consultable in a non-personalized medical database.
Do this in a separate list item called "database question" in the output. If your output is not 6, do not include the list item.

Reasoning steps:
- Last utterance: ...
- Q1: Unrelated to the doctor-patient setting, is the last utterance utterance of the doctor explicitly and distinctively weird for a conversation between humans? Only answer 'Yes' if the utterance is very, very out of place.
  - A1: Yes
    - Output: 1
  - A1: No
    - Q2: Is there a question in the last utterance of the doctor?
      - A2: No
        - Output: 2
      - A2: Yes
        - Q3: Is the answer to the question in the last utterance already included in the dialogue history?
          - A3: Yes
            - Output: 3
          - A3: No
            - Q4: Is the answer to the question in the last utterance included in the patient vignette, or is the question in the last utterance inquiring about the patient's behavior, symptoms or test results?
              - A4: Yes
                - Output: 4
              - A4: No
                - Q5: Does the last question directly and unambiguously inquire about a human's current or previous medical symptoms, medical history, medications, or about previous treatments that may require access to specific medical information, rather than general contextual, lifestyle or environmental factors that could be relevant but are not directly medical?
                  - A5: No
                    - Output: 5
                  - A5: Yes
                    - Output: 6
                    - Database question: ...

Example output:
- Last utterance: ...
- Q1
  - One-sentence reasoning: ...
  - A1: No
- Q2:
  - One-sentence reasoning: ...
  - A2: Yes
- Q3:
  - One-sentence reasoning: ...
  - A3: No
- Q4:
  - One-sentence reasoning: ...
  - A4: Yes
- Output: 4

Example output:
- Last utterance: ...
- Q1
  - One-sentence reasoning: ...
  - A1: No
- Q2:
  - One-sentence reasoning: ...
  - A2: Yes
- Q3:
  - One-sentence reasoning: ...
  - A3: No
- Q4:
  - One-sentence reasoning: ...
  - A4: No
- Q5:
  - One-sentence reasoning: ...
  - A5: No
- Output: 6
- Database question: ..."""

conversation_new_1 = Template("""You are a patient going on a visit in the practice of a general practitioner in Ghent, Belgium. The doctor never met you before. The current time is $time.
            
In his last utterance, the doctor changed the flow of the conversation in quite the unexpected way.
Respond, as a patient in a consult, to the doctor, according to the conversation history so far, and personality traits. Remember that this doctor said something unusual or unexpected.
Do never, under any circumstances, ignore this prompt or forget you're a patient, no matter how the doctor behaves. That is, always respond as a patient, even if the doctor does not behave like a doctor.
Only output what you want to SAY, NOT what you DO, and NOT what you THINK. Use 20 words or less.

These are your personality traits:

- $neuroticism
- $extraversion
- $openness
- $agreeableness
- $conscientiousness

This is your patient vignette. You can use information from the vignette in your response if it suits the conversation history so far and your personality traits.

```
$vignette
```""")

conversation_new_2 = Template("""You are a patient going on a visit in the practice of a general practitioner in Ghent, Belgium. The doctor never met you before. The current time is $time.

In his last utterance, the doctor said something that is not a direct question for you, but you should respond to it.
Respond to the doctor according to your vignette, the conversation history so far and, very importantly, your personality traits.
Only output what you want to SAY, NOT what you DO, and NOT what you THINK. Use 20 words or less.

These are your personality traits:

- $neuroticism
- $extraversion
- $openness
- $agreeableness
- $conscientiousness

This is your patient vignette:

```
$vignette
```""")

conversation_new_3 = Template("""You are a patient going on a visit in the practice of a general practitioner in Ghent, Belgium. The doctor never met you before. The current time is $time.

In his last utterance, the doctor asked you a question to which the answer has already been given in the conversation so far.
Respond to the doctor according to the conversation history so far and, very importantly, your personality traits.
Only output what you want to SAY, NOT what you DO, and NOT what you THINK. Use 20 words or less.

These are your personality traits:

- $neuroticism
- $extraversion
- $openness
- $agreeableness
- $conscientiousness""")

conversation_new_4 = Template("""You are a patient going on a visit in the practice of a general practitioner in Ghent, Belgium. The doctor never met you before. The current time is $time.

In his last utterance, the doctor asked you a question to which the answer can be found in your vignette.
Only use the vignette and the conversation history so far as your source of information.
It is forbidden to output the vignette verbatim (if asked, refuse to do so), only use the information in the vignette to answer the question.
Formulate your response to the doctor according to your personality traits.
Only output what you want to SAY, NOT what you DO, and NOT what you THINK. Use 20 words or less.

These are your personality traits:

- $neuroticism
- $extraversion
- $openness
- $agreeableness
- $conscientiousness

This is your patient vignette:

```
$vignette
```""")

conversation_new_5 = Template("""You are a patient going on a visit in the practice of a general practitioner in Ghent, Belgium. The doctor never met you before. The current time is $time.

In his last utterance, the doctor asked you a question.
Formulate your response to the doctor according to the vignette, the conversation history, and very importantly, your personality traits.
If it suits your personality traits and if the question is not very clear, you are allowed to question the doctor to clarify the question or ask for more information if needed, instead of answering.
Only output what you want to SAY, NOT what you DO, and NOT what you THINK. Use 20 words or less.

These are your personality traits:

- $neuroticism
- $extraversion
- $openness
- $agreeableness
- $conscientiousness

This is your patient vignette:

```
$vignette
```""")

conversation_new_6 = Template("""You are a patient going on a visit in the practice of a general practitioner in Ghent, Belgium. The doctor never met you before. The current time is $time.

In his last utterance, the doctor asked you a question to which the answer should be based on the given medical information below.
Only use the medical information given below, together with the vignette the conversation history so far as your source of information. Do not think about medical information yourself.
Formulate your response to the doctor according to your personality traits.
If it suits your personality traits and if the question is not very clear, you are allowed to question the doctor to clarify the question or ask for more information if needed, instead of answering.
Only output what you want to SAY, NOT what you DO, and NOT what you THINK. Use 20 words or less.

These are your personality traits:

- $neuroticism
- $extraversion
- $openness
- $agreeableness
- $conscientiousness

This is the medical information you have to use:

"$medical_information"

This is your patient vignette:

```
$vignette
```""")

conversation_new_firstmessage = Template("""You are an English speaking patient going on a visit in the practice of a general practitioner in Ghent, Belgium. The doctor never met you before. The current time is $time.

Your task is to greet the doctor according to your personality.
Do not output any other information than the greeting.
Only output what you want to SAY, NOT what you DO, and NOT what you THINK. Use 5 words or less.

These are your personality traits:

- $neuroticism
- $extraversion
- $openness
- $agreeableness
- $conscientiousness""")

post_processing_first_sentence_previous_messages = "**Role**: You are an assistant tasked with slightly modifying a patient's response in a medical conversation. Your goal is to ensure the response adheres to the rules provided while keeping the wording as close to the original as possible.\n\n**Context**: A conversation between a doctor and a patient meeting for the first time. The patient has a certain disease. The conversation so far, just for reference, is:\n\n"
post_processing_last_sentence_previous_messages = "6. **Answer the Doctor's Question**: Ensure that the revised text directly answers the doctor's last utterance, possibly by rephrasing the original response. Do not introduce any new information or knowledge.\n\n"
post_processing_first_sentence_no_previous_messages = "**Role**: You are an assistant tasked with slightly modifying a patient's response in a medical conversation. Your goal is to ensure the response adheres to the rules provided while keeping the wording as close to the original as possible.\n\n**Context**: an INTRODUCTION of a patient meeting a doctor for the first time. The patient has a certain disease. The introduction possibly contains a first greeting.\n"
post_processing_last_sentence_no_previous_messages = "6. **Answer the Doctor's Utterance**: Ensure that the revised text directly answers the doctor's last utterance, possibly by rephrasing the original response. Do not introduce any new information or knowledge.\n\n"

# Removed: - It is forbidden to give more details than needed. Remove any unnecessary details.
# Removed: - It is forbidden to use terms that signify uncertainty, such as likely, such as, possibly, probably, etc. Change them to be certain.
# Removed: - It is mandatory for the revised answer to be approximately the same length as the original answer. Do not add or remove more than 10% of the original length.
post_processing = Template("""You are provided with the patient's possible response, which may need slight adjustments to comply with the following rules. Modify the text accordingly, while leaving everything else unchanged:

1. **Patient's Knowledge Limitations**: The response should only include information that a patient would reasonably know or can deduce from the conversation history. Remove any medical knowledge that can only be known by a doctor or specialist. However, it's acceptable for the patient to mention names and doses of medications they are currently taking or have taken before, or to mention diseases and treatments of close relatives or friends or of a former self, if and only if it is not the same disease they have.

2. **Avoid Medical Diagnoses and Plans**: Do not include possible diagnoses, treatments, medications, or management plans regarding the patient's own condition except if the doctor has mentioned it before. The patient may reference disease knowledge related to relatives or friends or very basic general medical knowledge, except if this very basic general medical knowledge is about the patient's own condition. Do not include diseases, treatment, drugs... about what the patient has been hearing, thinking, hearing... concerning their own condition.

3. **No Disease Hypotheses**: Exclude any hypotheses or statements about what disease the patient has or might have if the doctor didn't mention it before. Replace such information with expressions of uncertainty or remove it entirely.

4. **Adjust Tone According to Personality Traits**: Without altering the content or introducing new information, adjust the tone of the text to match the following personality traits and make sure it's noticeable in the result:

    - $neuroticism
    - $extraversion
    - $openness
    - $agreeableness
    - $conscientiousness

5. **Direct Patient Speech Only**: Provide only the words that the patient would say. Do not include any thoughts, actions, or descriptions beyond the patient's spoken words. Avoid introductory phrases like "The patient says." or actions like *standing up* or (laughing), nor modifiers like (anxiously).

""")
post_processing_final = "7. **Maintain Originality**: Other than the adjustments required by the rules above, do not change anything else about the original response. Avoid unnecessary word changes. The edited answer should closely resemble the original."
