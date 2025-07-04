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


# This file contains configuration variables for the application.

OPENAI_API_KEY = ""
CEREBRAS_API_KEY = ""
GROQ_API_KEY = ""
PINECONE_API_KEY = ""

# The path to the directory containing the EBM source - include the trailing slash at the end.
EBM_path = ""
EBM_file_extension = "md"

# The name of the index in Pinecone where the EBM data is stored.
pinecone_index_name = ""

# The model used for quick feedback tips (OpenAI)
quick_feedback_api_model = "gpt-4o-mini-2024-07-18"
# The model used for full feedback (OpenAI)
full_feedback_api_model = "gpt-4.1-2025-04-14"
# The model used for preprocessing in the VSP conversational agent (Cerebras)
VSP_model_preprocessing = "llama-4-scout-17b-16e-instruct"
# The model used for processing the RAG response in the llamaindex chain (OpenAI)
VSP_model_ragprocessing = "gpt-4o-mini-2024-07-18"
# The model used for answer generation in the VSP conversational agent (Groq)
VSP_model_answergeneration = "meta-llama/llama-4-maverick-17b-128e-instruct"
# The model used for postprocessing in the VSP conversational agent (OpenAI)
VSP_model_postprocessing = "gpt-4o-mini-2024-07-18"

# The model used for generating the vignette (OpenAI)
vignette_generation_model = "gpt-4.1-2025-04-14"
