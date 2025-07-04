# ⚠️ WARNING: RESEARCH DEMO ONLY – NOT FOR PRODUCTION USE ⚠️
#
# This code is a research prototype and should NOT be deployed in any
# production environment. It lacks critical features required for safe and
# scalable operation, including:
#
# - No transport security (no HTTPS, no authentication)
# - Global shared state with no isolation between clients
# - Blocking I/O inside async handlers (can freeze the event loop)
# - No error recovery, retry logic, or request timeouts
# - Uses `print()` instead of structured logging
#
# Use at your own risk. This repository is intended for experimentation only.

import json
import random
import re
from datetime import datetime, timedelta

from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.core import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.tools import QueryEngineTool
from llama_index.core.vector_stores.types import VectorStoreQueryMode
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI as RAGOpenAI
from llama_index.vector_stores.pinecone import PineconeVectorStore
from mdextractor import extract_md_blocks
from openai import OpenAI
from pinecone import Pinecone

import config
import conversion_tables
import globals_conversation_logic
import predefined_patients
import prompts
from globals_server import broadcast_message

print("Initializing language models...")

client = OpenAI(api_key=config.OPENAI_API_KEY)
cerebras_client = OpenAI(base_url = "https://api.cerebras.ai/v1/",
                         api_key=config.CEREBRAS_API_KEY)
groq_client = OpenAI(base_url="https://api.groq.com/openai/v1/",
                            api_key=config.GROQ_API_KEY)  # Only one key for now
Settings.llm = RAGOpenAI(model=config.VSP_model_ragprocessing, temperature=0.1) # Used in the response synthesizer of RAG, a.o.
pc = Pinecone(api_key=config.PINECONE_API_KEY)
pinecone_index = pc.Index(config.pinecone_index_name)

print("Downloading/loading embedding model...")

embed_model = HuggingFaceEmbedding(
    model_name="dunzhang/stella_en_400M_v5",
    device="cuda:0",
    #device="cpu",
    trust_remote_code=True,
)

print("Initializing vector stores and indices...")
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_vector_store(
    vector_store, storage_context=storage_context, embed_model=embed_model
)

print("Loading tools...")
medical_knowledge_tool = QueryEngineTool.from_defaults(
    query_engine = RetrieverQueryEngine(
        retriever=VectorIndexRetriever(
            index=index,
            similarity_top_k=3,
            vector_store_query_mode=VectorStoreQueryMode.HYBRID
        ),
        response_synthesizer=get_response_synthesizer(),
        # Optional: enable LLMRerank
        # node_postprocessors=[LLMRerank(
        #         choice_batch_size=5,
        #         top_n=3,
        #     )],
     ),
    name="medical_knowledge",
    description="A RAG engine that is the only source of medical knowledge for a general practitioner.",
)

async def stop_patient():
    """
    Sends a broadcast message to stop the patient interaction, and sets the patient as not running.
    """
    await globals_conversation_logic.stop_patient()
    await broadcast_message({"action": "stopPatient"})

async def final_feedback():
    """
    Generates and sends final feedback for the patient interaction.

    This function performs the following steps:
    1. Generates clinical feedback.
    2. Generates conversational feedback.

    Returns:
        None
    """

    """
    Clinical feedback
    """

    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "output",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "diagnosis_feedback": {"type": "string"},
                    "treatment_planning_feedback": {"type": "string"},
                    "follow_up_and_monitoring_feedback": {"type": "string"},
                    "adherence_to_guidelines_feedback": {"type": "string"},
                    "risk_assessment_feedback": {"type": "string"},
                    "test_and_investigation_ordering_feedback": {"type": "string"},
                    "preventive_care_feedback": {"type": "string"}
                },
                "required": ["diagnosis_feedback", "treatment_planning_feedback", "follow_up_and_monitoring_feedback",
                             "adherence_to_guidelines_feedback", "risk_assessment_feedback", "test_and_investigation_ordering_feedback",
                             "preventive_care_feedback"],
                "additionalProperties": False
            }
        }
    }

    disease_name = globals_conversation_logic.get_patient().disease

    # Use this for diagnostic feedback
    disease_documents, score = conversion_tables.diseases[disease_name]
    disease_documents_content = []
    for document in disease_documents:
        with open(f"{config.EBM_path}{document}.{config.EBM_file_extension}", "r", encoding="utf-8") as f:
            content = f.read()
            disease_documents_content.append(content)

    system_prompt = prompts.final_feedback_diagnostic

    user_prompt = "**Patient Vignette:**\n\n"
    user_prompt += f"```\n{globals_conversation_logic.get_patient().vignette}\n```\n\n"
    user_prompt = "**Doctor-Patient Dialog History:**\n\n"
    user_prompt += "```"
    for entry in globals_conversation_logic.get_conversation_history():
        role = "Doctor" if entry["origin"] == "doctor" else "Patient"
        user_prompt += f"\n{role}: {entry['message']}"
    user_prompt += "\n```"
    user_prompt += "**Golden Standard for Diagnosis and Treatment:**\n\n"
    for document in disease_documents_content:
        user_prompt += f"```\n{document}\n```\n\n"

    completion = client.chat.completions.create(model=config.full_feedback_api_model, messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ], response_format=response_format)
    response_message = completion.choices[0].message.content
    response_message_json = json.loads(response_message)

    print(system_prompt)
    print(user_prompt)

    feedback_dict = {"action":"clinicalFeedbackResponse",
                     "feedback" : [
        {"criterium": "Diagnosis", "feedback": response_message_json["diagnosis_feedback"]},
        {"criterium": "Treatment planning", "feedback": response_message_json["treatment_planning_feedback"]},
        {"criterium": "Follow-up and monitoring", "feedback": response_message_json["follow_up_and_monitoring_feedback"]},
        {"criterium": "Adherence to guidelines", "feedback": response_message_json["adherence_to_guidelines_feedback"]},
        {"criterium": "Risk assessment", "feedback": response_message_json["risk_assessment_feedback"]},
        {"criterium": "Test and investigation ordering", "feedback": response_message_json["test_and_investigation_ordering_feedback"]},
        {"criterium": "Preventive care", "feedback": response_message_json["preventive_care_feedback"]},
    ]}

    print(feedback_dict)
    globals_conversation_logic.add_final_feedback(feedback_dict)
    await broadcast_message(feedback_dict)

    """
    Conversational feedback
    """

    def generate_conversational_feedback(criterium, system_prompt, response_format):
        prompt = [{"role": "system", "content": system_prompt}, {"role": "user", "content": criterium}]
        completion = client.chat.completions.create(model=config.full_feedback_api_model, messages=prompt,
                                                    temperature=0.1,
                                                    response_format=response_format)
        response_message = completion.choices[0].message.content
        response_message_json = json.loads(response_message)
        return response_message_json

    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "output",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "mark": {"type": "number"},
                    "explanation": {"type": "string"},
                    "evidence": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["mark", "explanation", "evidence"],
                "additionalProperties": False
            }
        }
    }

    system_prompt = ""
    for entry in globals_conversation_logic.get_conversation_history():
        role = "Doctor" if entry["origin"] == "doctor" else "Patient"
        system_prompt += f"\n{role}: {entry['message']}"

    system_prompt = prompts.final_feedback_system_prompt.substitute(conversation=system_prompt)
    for i, criterium in enumerate(prompts.final_feedback_criteria):
        feedback = generate_conversational_feedback(criterium['content'], system_prompt, response_format)
        feedback_dict = {"action": "feedbackResponse", "i": i, "criterium": criterium["title"], "mark": feedback["mark"], "explanation": feedback["explanation"],
             "evidence": feedback["evidence"]}
        globals_conversation_logic.add_final_feedback(feedback_dict)
        await broadcast_message(feedback_dict)

async def ask_quick_feedback():
    messages = globals_conversation_logic.get_conversation_history()

    prompt = ""
    for i in range(len(messages)):
        if messages[i]["origin"] == "doctor":
            if i == len(messages) - 1 or i == len(messages) - 2:
                prompt += f"Last utterance of the doctor: {messages[i]['message']}\n"
            else:
                prompt += f"Doctor: {messages[i]['message']}\n"
        elif messages[i]["origin"] == "patient" and i != len(messages) - 1: # Last condition: don't include the last patient message
            prompt += f"Patient: {messages[i]['message']}\n"

    prompt = prompts.quick_feedback_prompt.substitute(conversation=prompt)
    prompt_formatted = {"role": "user", "content": prompt}
    completion = client.chat.completions.create(model=config.quick_feedback_api_model, messages=[prompt_formatted])
    response_message = completion.choices[0].message.content
    await globals_conversation_logic.set_quick_feedback(response_message)

async def generate_patient(disease_difficulty, neuroticism, extraversion, openness, agreeableness, conscientiousness):
    NR_OF_STEPS = 8

    print("Generating patient...")
    await broadcast_message({"action": "generationStart"})

    await broadcast_message({"action": "generationUpdate", "text": "Picking a disease with given parameters...", "step": 1,"totalSteps": NR_OF_STEPS})

    disease_name = random.choice(list(conversion_tables.diseases.keys()))

    disease_documents, score = conversion_tables.diseases[disease_name]

    await globals_conversation_logic.add_debug_log(f"""1. Picked the disease: {disease_name} with a difficulty of {score}/10.""")

    await broadcast_message({"action": "generationUpdate",
                       "text": f"Reasoning about changing the difficulty to {disease_difficulty}/10...",
                       "step": 2,
                       "totalSteps": NR_OF_STEPS})

    disease_difficulty_lower = ((disease_difficulty // 5) * 5) - 5 if disease_difficulty % 5 == 0 else (
                                                                                                                   disease_difficulty // 5) * 5
    disease_difficulty_upper = ((disease_difficulty // 5) * 5) + 5

    if len(disease_documents) == 1:
        prompt_pt1 = prompts.generate_prompt_1_part1a.substitute(disease_name=disease_name)
    else:
        prompt_pt1 = prompts.generate_prompt_1_part1b.substitute(disease_name=disease_name)

    prompt_blocks = [prompt_pt1]

    for document in disease_documents:
        with open(f"{config.EBM_path}{document}.{config.EBM_file_extension}", "r", encoding="utf-8") as f:
            content = f.read()
        prompt_blocks.append(
            prompts.generate_prompt_1_part2.substitute(
                content=content,
                score=score,
                disease_difficulty=disease_difficulty,
                disease_difficulty_lower=disease_difficulty_lower,
                disease_difficulty_upper=disease_difficulty_upper
            )
        )

    prompt = "\n".join(prompt_blocks)

    await globals_conversation_logic.add_debug_log(
        "2a. Prompt\n```\n" + prompt_pt1 + prompts.generate_prompt_1_part2.safe_substitute(score=score,
                                                                                         disease_difficulty=disease_difficulty,
                                                                                         disease_difficulty_lower=disease_difficulty_lower,
                                                                                         disease_difficulty_upper=disease_difficulty_upper).replace(
            "`", "'") + "\n```")

    running_prompt = [{"role": "user", "content": prompt}]
    completion = client.chat.completions.create(model=config.vignette_generation_model, messages=running_prompt)
    response_message = completion.choices[0].message.content
    running_prompt.append({"role": "assistant", "content": response_message})
    response_message_cleaned = response_message.replace('`', "'")
    await globals_conversation_logic.add_debug_log(f"2b. Answer:\n```\n{response_message_cleaned}\n```")

    await broadcast_message({"action": "generationUpdate",
                       "text": "Generating the first version of the patient...",
                       "step": 3,
                       "totalSteps": NR_OF_STEPS})

    prompt = prompts.generate_prompt_2.substitute(disease_difficulty=disease_difficulty,
                                                           vignette=prompts.vignette_template)
    await globals_conversation_logic.add_debug_log(
        "3a. Prompt\n```\n" + prompts.generate_prompt_2.safe_substitute(disease_difficulty=disease_difficulty).replace(
            "`", "'") + "\n```")

    running_prompt.append({"role": "user", "content": prompt})
    completion = client.chat.completions.create(model=config.vignette_generation_model, messages=running_prompt)
    response_message = completion.choices[0].message.content
    if response_message.strip().replace("\n", "").replace(" ", "")[0] == "#":
        markdown_block = response_message
    else:
        markdown_blocks = extract_md_blocks(response_message)
        if len(markdown_blocks) == 0:
            await broadcast_message({"action": "generationStop", "state": "error",
                               "text": "Failed to parse the result. Please try again."})
            print(response_message)
            return
        markdown_block = markdown_blocks[0]

    markdown_block_cleaned = markdown_block.replace('`', "'")
    await globals_conversation_logic.add_debug_log(f"3b. Answer:\n```\n{markdown_block_cleaned}\n```")

    await broadcast_message({"action": "generationUpdate",
                       "text": "Scanning the generated patient's parameters...",
                       "step": 4,
                       "totalSteps": NR_OF_STEPS})

    prompt = prompts.generate_prompt_3.substitute(markdown_block=markdown_block)

    await globals_conversation_logic.add_debug_log("4a. Prompt\n```\n" + prompts.generate_prompt_3.safe_substitute().replace("`", "'") + "\n```")

    running_prompt = [{"role": "user", "content": prompt}]
    completion = client.chat.completions.create(model=config.vignette_generation_model, messages=running_prompt)
    response_message = completion.choices[0].message.content
    response_message_cleaned = response_message.replace('`', "'")
    await globals_conversation_logic.add_debug_log(f"4b. Answer:\n```\n{response_message_cleaned}\n```")
    running_prompt.append({"role": "assistant", "content": response_message})

    await broadcast_message({"action": "generationUpdate",
                       "text": "Reasoning about post-process changes...",
                       "step": 5,
                       "totalSteps": NR_OF_STEPS})
    prompt = prompts.generate_prompt_4
    await globals_conversation_logic.add_debug_log("5a. Prompt\n```\n" + prompt + "\n```")

    running_prompt.append({"role": "user", "content": prompt})
    completion = client.chat.completions.create(model=config.vignette_generation_model, messages=running_prompt)
    response_message = completion.choices[0].message.content
    response_message_cleaned = response_message.replace('`', "'")
    await globals_conversation_logic.add_debug_log(f"5b. Answer:\n```\n{response_message_cleaned}\n```")

    running_prompt.append({"role": "assistant", "content": response_message})

    await broadcast_message({"action": "generationUpdate",
                       "text": "Generating the final version of the patient...",
                       "step": 6,
                       "totalSteps": NR_OF_STEPS})

    prompt = prompts.generate_prompt_5
    await globals_conversation_logic.add_debug_log("6a. Prompt\n```\n" + prompt + "\n```")

    running_prompt.append({"role": "user", "content": prompt})
    completion = client.chat.completions.create(model=config.vignette_generation_model, messages=running_prompt)
    response_message = completion.choices[0].message.content
    # This means that the response is already a markdown block, so we don't need to extract it.
    if response_message.strip().replace("\n", "").replace(" ", "")[0] == "#":
        markdown_block = response_message
    else:
        markdown_blocks = extract_md_blocks(response_message)
        if len(markdown_blocks) == 0:
            await broadcast_message({"action": "generationStop", "state": "error",
                               "text": "Failed to parse the result. Please try again."})
            print(response_message)
            return
        markdown_block = markdown_blocks[0]

    markdown_block_cleaned = markdown_block.replace('`', "'")
    await globals_conversation_logic.add_debug_log(f"6b. Answer:\n```\n{markdown_block_cleaned}\n```")

    await broadcast_message({"action": "generationUpdate",
                       "text": "Choosing an avatar...",
                       "step": 7,
                       "totalSteps": NR_OF_STEPS})

    prompt = prompts.generate_prompt_6.substitute(faces=conversion_tables.furhat_faces_list,
                                                  voices=conversion_tables.furhat_elevenlabs_voices_list, vignette=markdown_block)
    await globals_conversation_logic.add_debug_log("7a. Prompt\n```\n" + prompts.generate_prompt_6.safe_substitute().replace("`", "'") + "\n```")

    prompt_new = [{"role": "user", "content": prompt}]
    completion = client.chat.completions.create(model=config.vignette_generation_model, messages=prompt_new,
                                                response_format={
                                                    "type": "json_schema",
                                                    "json_schema": {
                                                        "name": "output",
                                                        "strict": True,
                                                        "schema": {
                                                            "type": "object",
                                                            "properties": {
                                                                "face": {
                                                                    "type": "string"
                                                                },
                                                                "voice": {
                                                                    "type": "string"
                                                                }
                                                            },
                                                            "required": [
                                                                "face",
                                                                "voice"
                                                            ],
                                                            "additionalProperties": False
                                                        }
                                                    }
                                                })
    response_message = completion.choices[0].message.content
    response_message_cleaned = response_message.replace('`', "'")
    await globals_conversation_logic.add_debug_log(f"7b. Answer:\n```\n{response_message_cleaned}\n```")

    # Parse the response
    response_message_json = json.loads(response_message)

    face = response_message_json["face"]
    voice = response_message_json["voice"]

    await broadcast_message({"action": "generationUpdate",
                       "text": "Sending generated details to the robot head...",
                       "step": 8,
                       "totalSteps": NR_OF_STEPS})

    patient = globals_conversation_logic.Patient(
        disease=disease_name,
        vignette=markdown_block,
        face=face,
        voice = voice,
        neuroticism=conversion_tables.translate_score("neuroticism", neuroticism),
        extraversion=conversion_tables.translate_score("extraversion", extraversion),
        openness=conversion_tables.translate_score("openness", openness),
        agreeableness=conversion_tables.translate_score("agreeableness", agreeableness),
        conscientiousness=conversion_tables.translate_score("conscientiousness", conscientiousness)
    )

    await globals_conversation_logic.start_patient(patient)

async def launch_predefined_patient(patient_nr):
    """
    Launches a predefined patient.

    Args:
        patient_nr (int): The number of the predefined patient.

    Returns:
        None
    """
    patient = predefined_patients.mapping[patient_nr]
    await globals_conversation_logic.add_debug_log(
        f"""Picked the patient with the following parameters:

- Disease: {patient.disease}
- Face: {patient.face}
- Voice: {patient.voice}
- Personality

    - Neuroticism: {patient.neuroticism}
    - Extraversion: {patient.extraversion}
    - Openness: {patient.openness}
    - Agreeableness: {patient.agreeableness}
    - Conscientiousness: {patient.conscientiousness}
- Vignette:
```
{patient.vignette}
```"""
    )
    print("Patient started")
    await globals_conversation_logic.start_patient(patient)

def post_process(was_doctor_utterance: bool, answer: str, conversation_history, patient) -> str:
    """
    Post-processes the answer generated by the model.

    Args:
        was_doctor_utterance (bool): There was an utterance by the doctor.
        answer (str): The answer generated by the model.
        conversation_history (list): The conversation history.
        patient (Patient): The patient object.

    Returns:
        str: The post-processed answer.
    """
    global client
    if was_doctor_utterance:
        first_sentence = prompts.post_processing_first_sentence_previous_messages
        for element in conversation_history:
            if element["origin"] == "doctor":
                first_sentence += f"Doctor: {element['message']}\n"
            else:
                first_sentence += f"Patient: {element['message']}\n"
        first_sentence += "\n"
        last_sentence = prompts.post_processing_last_sentence_previous_messages + prompts.post_processing_final
    else:
        first_sentence = prompts.post_processing_first_sentence_no_previous_messages
        last_sentence = prompts.post_processing_last_sentence_no_previous_messages + prompts.post_processing_final

    messages = [
        {"role":"system","content":first_sentence + prompts.post_processing.substitute(
                neuroticism=patient.neuroticism,
                extraversion=patient.extraversion,
                openness=patient.openness,
                agreeableness=patient.agreeableness,
                conscientiousness=patient.conscientiousness
            ) + last_sentence},
        {"role":"user","content":answer}
    ]
    print("Now post-processing answer:" + answer)
    completion = client.chat.completions.create(model=config.VSP_model_postprocessing,
                                                              messages=messages)

    return completion.choices[0].message.content

async def generate_patient_response():
    global cerebras_client

    def parse_output_and_question(text):
        # Use regular expressions to extract the "Output" and "Database question"
        output_match = re.search(r'Output:\s*(\d+)', text)
        question_match = re.search(r'Database question:\s*(.*)', text)

        output = int(output_match.group(1)) if output_match else None
        database_question = question_match.group(1) if question_match else None

        return output, database_question

    current_time = datetime.now()

    patient = globals_conversation_logic.get_patient()
    conversation_history = globals_conversation_logic.get_conversation_history()

    conversation_history_string = ""
    for hist_item in conversation_history:
        conversation_history_string += f"{hist_item['origin']}: {hist_item['message']}\n"

    caution_when_answering = False

    if len(conversation_history) == 0:
        system_prompt = prompts.conversation_new_firstmessage.substitute(
            time=datetime.now().strftime("%H:%M"),
            vignette=patient.vignette,
            neuroticism=patient.neuroticism,
            extraversion=patient.extraversion,
            openness=patient.openness,
            agreeableness=patient.agreeableness,
            conscientiousness=patient.conscientiousness
        )
        # A timedelta of 0
        time_difference = timedelta()

    else:
        messages = [
                {"role": "system", "content": prompts.conversation_new_preprocessing},
                {"role": "user", "content": f"""(1) The conversation history with as last utterance "{conversation_history[-1]['message']}":
    
    {conversation_history_string}
            
        (2) The patient vignette
    
        {patient.vignette}""", },
            ]


        completion = cerebras_client.chat.completions.create(
            model=config.VSP_model_preprocessing,
            messages=messages,
        )

        # response = json.loads(completion.choices[0].message.content)
        response = completion.choices[0].message.content
        output, database_question = parse_output_and_question(response)

        print(response)
        time_difference = datetime.now() - current_time
        print(f"Time taken to preprocess response: {time_difference.total_seconds()*100} milliseconds")
        current_time = datetime.now()

        match output:
            case 1:
                system_prompt = prompts.conversation_new_1.substitute(
                    time=datetime.now().strftime("%H:%M"),
                    vignette=patient.vignette,
                    neuroticism=patient.neuroticism,
                    extraversion=patient.extraversion,
                    openness=patient.openness,
                    agreeableness=patient.agreeableness,
                    conscientiousness=patient.conscientiousness
                )
                caution_when_answering = True

            case 2:
                system_prompt = prompts.conversation_new_2.substitute(
                    time=datetime.now().strftime("%H:%M"),
                    vignette=patient.vignette,
                    neuroticism=patient.neuroticism,
                    extraversion=patient.extraversion,
                    openness=patient.openness,
                    agreeableness=patient.agreeableness,
                    conscientiousness=patient.conscientiousness
                )
            case 3:
                system_prompt = prompts.conversation_new_3.substitute(
                    time=datetime.now().strftime("%H:%M"),
                    neuroticism=patient.neuroticism,
                    extraversion=patient.extraversion,
                    openness=patient.openness,
                    agreeableness=patient.agreeableness,
                    conscientiousness=patient.conscientiousness
                )
            case 4:
                system_prompt = prompts.conversation_new_4.substitute(
                    time=datetime.now().strftime("%H:%M"),
                    vignette=patient.vignette,
                    neuroticism=patient.neuroticism,
                    extraversion=patient.extraversion,
                    openness=patient.openness,
                    agreeableness=patient.agreeableness,
                    conscientiousness=patient.conscientiousness
                )
            case 5:
                system_prompt = prompts.conversation_new_5.substitute(
                    time=datetime.now().strftime("%H:%M"),
                    vignette=patient.vignette,
                    neuroticism=patient.neuroticism,
                    extraversion=patient.extraversion,
                    openness=patient.openness,
                    agreeableness=patient.agreeableness,
                    conscientiousness=patient.conscientiousness
                )
            case 6:
                if database_question is None: # Should not happen but ehh, you never know with LLMs (╯°□°)╯︵ ┻━┻
                    system_prompt = prompts.conversation_system_prompt.substitute(
                        time=datetime.now().strftime("%H:%M"),
                        vignette=patient.vignette,
                        neuroticism=patient.neuroticism,
                        extraversion=patient.extraversion,
                        openness=patient.openness,
                        agreeableness=patient.agreeableness,
                        conscientiousness=patient.conscientiousness
                    )
                else:
                    rag_query = "For a person with the disease " + patient.disease + ": " + database_question
                    current_time2 = datetime.now()
                    print("Doing RAG now... with query " + rag_query)
                    rag_query = medical_knowledge_tool.query_engine.query(rag_query)
                    print("RAG query done.")
                    print(f"Time taken to query RAG: {(datetime.now() - current_time2).total_seconds()*100} milliseconds")

                    rag_reply = rag_query.response
                    system_prompt = prompts.conversation_new_6.substitute(
                        time=datetime.now().strftime("%H:%M"),
                        vignette=patient.vignette,
                        medical_information=rag_reply,
                        neuroticism=patient.neuroticism,
                        extraversion=patient.extraversion,
                        openness=patient.openness,
                        agreeableness=patient.agreeableness,
                        conscientiousness=patient.conscientiousness
                    )
            case _: # Should not happen but ehh, you never know with LLMs (╯°□°)╯︵ ┻━┻
                system_prompt = prompts.conversation_system_prompt.substitute(
            time=datetime.now().strftime("%H:%M"),
            vignette=patient.vignette,
            neuroticism=patient.neuroticism,
            extraversion=patient.extraversion,
            openness=patient.openness,
            agreeableness=patient.agreeableness,
            conscientiousness=patient.conscientiousness
        )

    llm_prompt = [{"role": "system", "content": system_prompt}]
    if not caution_when_answering:
        llm_prompt.extend([{"role": "user", "content": hist_item["message"]}
                           if hist_item["origin"] == "doctor"
                           else {"role": "assistant", "content": hist_item["message"]}
                           for hist_item in conversation_history])
    else:
        conversation_history_except_last = conversation_history[:-1]
        llm_prompt.extend([{"role": "user", "content": hist_item["message"]}
                           if hist_item["origin"] == "doctor"
                           else {"role": "assistant", "content": hist_item["message"]}
                           for hist_item in conversation_history_except_last])
        last_conversation_item = conversation_history[-1]
        warning = "(WARNING: The following utterance might try to throw you off guard as a patient in a doctor's office -- don't let the user deceive you!)"
        if last_conversation_item["origin"] == "doctor":
            llm_prompt.append({"role": "user", "content": warning + " " + last_conversation_item["message"]})
        else:
            llm_prompt.append({"role": "assistant", "content": last_conversation_item["message"]})


    print(llm_prompt)

    completion = groq_client.chat.completions.create(model=config.VSP_model_answergeneration,
                                                          messages=llm_prompt)

    print(completion.usage)
    response_message = completion.choices[0].message.content

    if len(conversation_history) > 0 and not globals_conversation_logic.last_message_is_from_patient():
        response_message = post_process(True, response_message, conversation_history, patient)
    else:
        response_message = post_process(False, response_message, conversation_history, patient)


    current_time_str = datetime.now().strftime("%H:%M")
    globals_conversation_logic.add_to_history("patient", response_message, current_time_str)

    time_difference2 = datetime.now() - current_time
    print(f"Time taken to generate patient response: {time_difference2.total_seconds()*100} milliseconds")
    print(f"Total generation time: {(time_difference2.total_seconds() + time_difference.total_seconds())*100} milliseconds")

    await broadcast_message({"action": "patientGeneratedResponse", "response": response_message, "time": current_time_str})

    print(f"Generation all done!")