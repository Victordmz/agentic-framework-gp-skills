# Central‑Backend Server README

*Accompanies the paper **“An Agentic AI Framework for Training General‑Practitioner Student Skills”** and the top‑level project README.*

---

## 1. What the backend does 🚦

The **central‑backend server** is the single coordination point that glues the three agents described in the paper:

| Agent (paper section)                   | Implemented in backend                                  | Purpose                                                                                                                              |
| --------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| *Generator Agent*                       | `utils.generate_patient()` and helpers                  | Builds an EBM‑grounded vignette, assigns Big‑Five personality & a Furhat avatar face/voice, then broadcasts a `startPatient` command |
| *Virtual‑Simulated‑Patient (VSP) Agent* | `utils.generate_patient_response()`                     | Produces persona‑consistent dialogue, optionally uses RAG via Pinecone + Stella embeddings                                           |
| *Critic Agent*                          | `utils.ask_quick_feedback()` + `utils.final_feedback()` | Streams real‑time “quick tips” and standards‑based summative feedback                                                                |

All traffic between agents, the Streamlit dashboard, and a Furhat (real or virtual) head flows through an **async WebSocket API** exposed by `ws_server.py`.

A high‑level runtime architecture is shown in `../architecture.png`.

---

## 2. File/Module tour 🗂

| Path                                | What it contains                                                                                         |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------- |
| **`ws_server.py`**                  | Asyncio WebSocket gateway; parses JSON “actions”, maintains connected‑client roles, and forwards events |
| **`globals_server.py`**             | Thread‑unsafe global connection registry + `broadcast_message()` helper                                 |
| **`globals_conversation_logic.py`** | Cross‑agent shared state: current patient, conversation log, debug log, feedback queue, Furhat status   |
| **`utils.py`**                      | Heavy‑lifting orchestrator for generation, RAG, answer post‑processing, and feedback routines           |
| **`conversion_tables.py`**          | Lookup tables for diseases, Big‑Five score → persona text, and Furhat voice/face catalog                |
| **`predefined_patients.py`**        | A handful of hard‑coded vignettes for quick demos/tests                                                 |
| **`prompts.py`**                    | All system/user templates used by the LLMs                                                              |
| **`requirements.txt`**              | Minimal Python deps – intentionally pinned short for a demo repo                                        |
| **`config.py`**                     | **Never commit secrets!** Holds model names and empty API‑key slots                                     |

> **Prototype warning** – Most modules carry a banner that the code is **research–only** (no auth, no https, blocking I/O in event loop, etc.). Do not deploy as‑is in production.

---

## 3. Configuration reference 🛠

`config.py` fields most users tweak:

| Key                                                                                               | Meaning                                                   |
| ------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| `OPENAI_API_KEY`, `CEREBRAS_API_KEY`, `GROQ_API_KEY`, `PINECONE_API_KEY`                          | Provider credentials                                      |
| `EBM_path`, `EBM_file_extension`                                                                  | Folder & extension of your evidence‑based medicine corpus |
| `pinecone_index_name`                                                                             | Name of your Pinecone index                               |
| `vignette_generation_model`, `VSP_model_*`, `quick_feedback_api_model`, `full_feedback_api_model` | Names of LLMs available in their respective providers     |

Remember to **never commit real keys**. See TODO for migrating to `.env`.

---

## 4. Development & debugging tips 🐛

* Every generation pipeline step appends to a **debug log** (`globals_conversation_logic.add_debug_log`) which the UI can stream live.
* Tests are still missing; stubs are in the TODO in the top-level README—PRs welcome!


## 5. License 📄

This backend inherits the repository‑wide **GPL‑3.0** license. See `LICENSE` for full text.
