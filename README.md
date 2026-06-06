# Smart Campus Tour & Information Multi-Modal Chatbot

> A production-grade, multi-modal conversational AI system for campus navigation and information retrieval — built with LangGraph, custom-trained NLP models, and a fully containerised REST API.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Pipeline Design](#3-pipeline-design)
   - [Text Pipeline](#31-text-pipeline)
   - [Audio Pipeline](#32-audio-pipeline)
   - [Image Pipeline](#33-image-pipeline)
   - [Audio + Text Pipeline](#34-audio--text-pipeline)
   - [Multimodal Pipeline](#35-multimodal-pipeline)
4. [Model Stack](#4-model-stack)
5. [Knowledge Base](#5-knowledge-base)
6. [API Layer](#6-api-layer)
7. [Frontend](#7-frontend)
8. [Engineering Practices](#8-engineering-practices)
9. [Project Structure](#9-project-structure)
10. [Setup & Installation](#10-setup--installation)
11. [Running the System](#11-running-the-system)
12. [Testing](#12-testing)
13. [CI/CD](#13-cicd)
14. [Results & Evaluation](#14-results--evaluation)

---

## 1. Project Overview

This project addresses a common problem at large university campuses — students and visitors struggle to find locations, understand timetables, and navigate between buildings. The system provides a conversational AI assistant capable of understanding queries expressed as **text**, **voice**, **image**, or any combination of all three.

### Key Contributions

- Five distinct inference pipelines implemented as directed acyclic graphs using LangGraph
- A custom-trained **Fusion MLP** that combines visual, textual, and acoustic embeddings for multimodal location prediction
- A structured **campus knowledge base** of 154 entries covering buildings, departments, labs, cafeterias, events, and opening hours
- A production REST API with retry logic, async request handling, request latency tracking, and health monitoring
- An interactive Streamlit chat interface with persistent history and a live admin dashboard
- A full CI/CD pipeline on GitHub Actions with automated testing, linting, and security scanning

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          User Interfaces                                │
│                                                                         │
│   Streamlit Chat App          Streamlit Admin Dashboard                 │
│   (port 8501)                 (port 8502)                               │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │ HTTP
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         FastAPI REST API                                │
│                         (port 8000)                                     │
│                                                                         │
│  POST /query/text          POST /query/audio                            │
│  POST /query/image         POST /query/audio-text                       │
│  POST /query/multimodal    GET  /health                                 │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      LangGraph Pipeline Engine                          │
│                                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │   Text   │  │  Audio   │  │  Image   │  │ Audio+   │  │  Multi   │ │
│  │ Pipeline │  │ Pipeline │  │ Pipeline │  │  Text    │  │  modal   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
┌─────────────────┐   ┌─────────────────────┐   ┌──────────────────┐
│   Model Layer   │   │  Knowledge Base      │   │   LLM (Groq)     │
│                 │   │                      │   │                  │
│  Whisper base   │   │  campus_kb.json      │   │  LLaMA 3.1 8B    │
│  CLIP ViT-B/32  │   │  154 entries         │   │  (via API)       │
│  DistilBERT     │   │  Locations, Hours    │   │  Temperature 0.2 │
│  Fusion MLP     │   │  Events, Directions  │   │  Max tokens 512  │
│  spaCy NER      │   │  Coordinates         │   │  Retry x3        │
│  FAISS Index    │   │                      │   │                  │
│  Rules Engine   │   │                      │   │                  │
└─────────────────┘   └─────────────────────┘   └──────────────────┘
```

### Core Design Principles

- **Graph-based execution** — each pipeline is a LangGraph StateGraph where nodes are pure functions that read from and write to a typed state dictionary. No global mutable state.
- **Lazy model loading** — models are loaded on first use and cached globally. Startup is fast; memory is allocated only when a pipeline is invoked.
- **Fail-safe error propagation** — every node catches exceptions and writes `{"error": str(e)}` to state. Downstream nodes check for upstream errors before executing.
- **Strict environment separation** — `dev`, `staging`, and `prod` environments each have their own `.env` file. Secrets are loaded from AWS Secrets Manager in non-dev environments.

---

## 3. Pipeline Design

All five pipelines are implemented as LangGraph `StateGraph` objects compiled into executable workflows. Each node is a typed Python function. The state is a `TypedDict` that defines exactly which fields each pipeline reads and writes.

### 3.1 Text Pipeline

Handles plain text queries about campus locations, directions, events, and hours.

```
query
  │
  ▼
intent_entity_extraction
  │  Extracts: intent, entities, category_hints, nav_pair
  │  Models: spaCy NER + Rules Engine
  ▼
kb_search
  │  Searches: campus_kb.json using RapidFuzz fuzzy matching
  │  Returns: kb_context (formatted string)
  ▼
final_ans_generation
  │  LLM: LLaMA 3.1 8B via Groq API
  │  Input: kb_context + user query
  ▼
answer
```

**State:** `TextBotState` — query → intent, entities, category_hints, nav_pair → kb_results, kb_context → answer

### 3.2 Audio Pipeline

Handles voice queries by first transcribing the audio, then routing through the text pipeline.

```
audio_file_path
  │
  ▼
audio_to_text
  │  Model: OpenAI Whisper (base)
  │  Output: transcript text
  ▼
intent_entity_extraction → kb_search → final_ans_generation → answer
```

**State:** `AudioBotState` — same as TextBotState but input is an audio file path

### 3.3 Image Pipeline

Handles image queries by identifying the campus location in the image using CLIP and FAISS.

```
image_file_path
  │
  ▼
clip_node
  │  Model: CLIP ViT-B/32
  │  Output: 512-dimensional image embedding (L2 normalised)
  ▼
faiss_node
  │  Index: Flat IP FAISS index of campus location images
  │  Output: top 3 matches with confidence scores
  ▼
kb_node
  │  Lookup: campus_kb.json by kb_name
  │  Output: name, description, hours, directions, events
  ▼
llm_node
  │  LLM: LLaMA 3.1 8B via Groq
  │  Prompt: identified location + details + follow-up offer
  ▼
answer
```

**State:** `ImageBotState` — image_path → embedding → top_3_matches, best_match → kb fields → answer

### 3.4 Audio + Text Pipeline

Combines a voice query with an optional text query before routing through intent extraction.

```
audio_file_path + text_query (optional)
  │
  ├── audio_to_text ──────────────────────────────┐
  │   Model: Whisper base                          │
  │                                                ▼
  └─────────────────────────────────── merge_query
                                          │  Concatenates: transcript + text_query
                                          ▼
                              intent_entity_extraction → kb_search → final_ans_generation → answer
```

**State:** `AudioTextBotState` — query (audio path) + text_query → merge_query → intent, entities → kb_context → answer

### 3.5 Multimodal Pipeline

The most complex pipeline. Combines text, voice, and image inputs using a trained Fusion MLP to predict the campus location, then retrieves KB context and generates a response.

```
text_query + audio_path + image_path
  │              │              │
  ▼              ▼              ▼
text_distilbert  whisper_node  clip_node
  │              │              │
  │   DistilBERT │   Whisper    │  CLIP ViT-B/32
  │   intent emb │   transcript │  image embedding
  │              ▼              ▼
  │         voice_distilbert  faiss_node
  │              │              │
  │   DistilBERT │              │  FAISS search
  │   voice emb  │              │
  └──────────────┴──────────────┘
                 │
                 ▼
           fusion_mlp_node
                 │  Model: custom 3-layer MLP
                 │  Input: [image_emb(512) | nlp_emb(768)] = 1280-dim
                 │  Output: location class + confidence score
                 ▼
         multimodal_kb_node
                 │  Lookup: campus_kb.json by fusion_location
                 │  Output: kb_context
                 ▼
            llm_node
                 │  LLM: LLaMA 3.1 8B via Groq
                 │  Prompt: text query + voice transcript + identified location + KB context
                 ▼
              answer
```

**State:** `MultiModalState` — 22 typed fields covering all inputs, intermediate embeddings, fusion outputs, and final answer

---

## 4. Model Stack

| Model | Version | Role | Training |
|-------|---------|------|----------|
| OpenAI Whisper | base | Audio → text transcription | Pre-trained, no fine-tuning |
| CLIP | ViT-B/32 | Image → 512-dim embedding | Pre-trained, no fine-tuning |
| FAISS | Flat IP index | Nearest-neighbour image search | Built from campus image embeddings |
| DistilBERT | distilbert-base-uncased | Intent → 768-dim embedding | Fine-tuned on campus intent dataset |
| Fusion MLP | v1 | Multimodal location classification | Trained from scratch on campus data |
| spaCy NER | en_core_web_md-3.8.0 | Named entity recognition | Fine-tuned on campus entity dataset |
| Rules Engine | custom | Intent classification fallback | Hand-crafted regex + keyword rules |
| LLaMA 3.1 | 8B Instant | Answer generation | Pre-trained, prompted via Groq API |

### Fusion MLP Architecture

```
Input: [CLIP image embedding (512) || DistilBERT intent embedding (768)]
       = 1280-dimensional concatenated vector

Layer 1: Linear(1280 → 512) → ReLU → Dropout(0.3)
Layer 2: Linear(512 → 128)  → ReLU → Dropout(0.2)
Layer 3: Linear(128 → N)    → Softmax

Output: location class probability distribution over N campus locations
```

---

## 5. Knowledge Base

The campus knowledge base is a structured JSON file (`data/campus_kb.json`) containing **154 entries** covering every navigable location on campus.

### Entry Schema

```json
{
  "name": "Main Library",
  "category": "library",
  "description": "The central academic library...",
  "map_reference": "Block A, Floor 2",
  "directions_from_entrance": "Enter main gate, turn left...",
  "opening_hours": {
    "Mon-Fri": "8:00 AM - 8:00 PM",
    "Saturday": "9:00 AM - 5:00 PM"
  },
  "events": ["Book fair on June 10"],
  "coordinates": {"lat": 52.5068, "lng": 13.4024},
  "floor_map": {}
}
```

### Category Distribution

| Category | Count |
|----------|-------|
| Departments | 7 |
| Classrooms | 80+ |
| Labs | 20+ |
| Administrative offices | 10 |
| Facilities (library, cafeteria, gym, etc.) | 15 |
| Outdoor spaces | 5 |
| Other | remainder |

### KB Search Strategy

KB search uses a multi-stage fuzzy matching approach:

1. **Entity matching** — extracted named entities are matched against KB entry names using RapidFuzz (`token_sort_ratio`)
2. **Category filtering** — category hints from intent extraction narrow the search space
3. **Navigation mode** — for `FROM → TO` queries, source and destination are resolved separately and merged into a single context block
4. **List mode** — for queries like "list all labs" or "how many departments", all matching entries are returned and counted

---

## 6. API Layer

The system exposes a FastAPI REST API with five inference endpoints and a health check.

### Endpoints

| Method | Endpoint | Pipeline | Input |
|--------|----------|----------|-------|
| POST | `/query/text` | Text | `{"query": str}` |
| POST | `/query/audio` | Audio | `{"audio_path": str}` |
| POST | `/query/image` | Image | `{"image_path": str}` |
| POST | `/query/audio-text` | Audio+Text | `{"query": str, "text_query": str}` |
| POST | `/query/multimodal` | Multimodal | `{"query": str, "audio_path": str, "image_path": str}` |
| GET | `/health` | — | — |
| GET | `/docs` | — | Swagger UI |

### Response Schema

All endpoints return a consistent `ChatResponse`:

```json
{
  "answer": "The library is located on Floor 2 of Block A...",
  "pipeline": "text",
  "error": null
}
```

### Production Features

- **Async execution** — all endpoints use `asyncio.run_in_executor` to avoid blocking the event loop during model inference
- **Semaphores** — Whisper and CLIP endpoints are rate-limited to 2 concurrent calls each
- **Retry logic** — LLM nodes retry up to 3 times on Groq API failures
- **Latency middleware** — every request logs response time and appends `X-Response-Time` header
- **Startup validation** — `config.validate()` is called at startup; the server refuses to start if any model file or API key is missing
- **Global error handler** — unhandled exceptions return a structured JSON error response instead of a 500 stack trace

---

## 7. Frontend

### Chat Interface (`frontend/chat_app.py`)

- Streamlit app running on port 8501
- Three input fields: text query, audio file path, image file path
- Pipeline is selected automatically based on which inputs are provided
- Chat history is persisted to `frontend/chat_history.json` between sessions
- Interactive campus map in the sidebar built with Folium — 154 location pins, colour-coded by category, with popup cards showing hours, events, and sample questions

### Admin Dashboard (`frontend/admin_app.py`)

- Streamlit app running on port 8502
- Real-time system health check — all 6 model files verified on every refresh
- Pipeline usage bar chart — shows which pipelines are being called most
- Average response time per node — identifies bottlenecks
- Recent queries table — last 15 queries with timestamp, pipeline, and query text
- Error log viewer — filters out test-generated errors, shows only real production errors
- Auto-refresh every 5–60 seconds (configurable)

---

## 8. Engineering Practices

### Logging

Structured logging via Python `logging` module. Every node logs entry, exit, duration, and key output values. In production, logs are formatted as JSON for ingestion into centralised log management (Grafana + Loki planned).

### Error Handling

Every node follows the same pattern:

```python
try:
    # node logic
except SpecificException as e:
    logger.error(f"node_name → failed: {e}", exc_info=True)
    return {"error": str(e)}
```

Downstream nodes check `state.get("error")` before executing. Final answer nodes return a user-friendly message if an upstream error exists.

### Testing

33 tests across unit and integration levels:

| Type | Count | Description |
|------|-------|-------------|
| Unit | 26 | Each node tested in isolation with mocked models |
| Integration | 7 | Full pipeline invocations with real models |

Models are mocked in unit tests using `pytest` fixtures and `monkeypatch`. Integration tests use real model files and real Groq API calls.

### CI/CD (GitHub Actions)

Three jobs run on every push to `main`:

| Job | Tool | Purpose |
|-----|------|---------|
| Run Tests | pytest | Verify all 26 unit tests pass |
| Code Quality | flake8 | Enforce style and catch bad code |
| Security Scan | bandit + safety | Detect hardcoded secrets and vulnerable packages |

---

## 9. Project Structure

```
campus_chatbot/
├── api/                        # FastAPI application
│   ├── main.py                 # App entry point, middleware, health check
│   ├── schemas.py              # Pydantic request/response models
│   └── routes/                 # One file per endpoint
├── config/                     # Configuration and secrets
│   ├── settings.py             # All constants, paths, model versions
│   ├── secrets.py              # AWS Secrets Manager / .env loader
│   └── logger.py               # Structured logging setup
├── core/                       # LangGraph pipeline definitions
│   ├── state.py                # TypedDict state classes for all pipelines
│   ├── model_loader.py         # Lazy model loading with health check
│   ├── text_graph.py           # Text pipeline graph
│   ├── audio_graph.py          # Audio pipeline graph
│   ├── image_graph.py          # Image pipeline graph
│   ├── audio_with_text_graph.py# Audio+Text pipeline graph
│   └── multimodel_graph.py     # Multimodal pipeline graph
├── nodes/                      # Individual pipeline nodes
│   ├── intent_entity_extraction.py
│   ├── kb_search.py
│   ├── final_ans_generation.py
│   ├── audio_to_text.py
│   ├── merge_query.py
│   ├── clip_node.py
│   ├── faiss_node.py
│   ├── kb_node.py
│   ├── llm_node.py
│   └── multimodel_all_nodes.py
├── services/                   # Reusable business logic
│   ├── kb_search.py            # Fuzzy KB search with RapidFuzz
│   └── intent_extractor.py     # Category hint extraction
├── models/                     # Trained model files (not in git)
│   ├── campus_spacy/           # Fine-tuned spaCy NER model
│   ├── distilbert_campus/      # Fine-tuned DistilBERT
│   ├── clip_faiss/             # FAISS index + image records
│   ├── fusion_mlp/             # Trained Fusion MLP weights
│   └── rules_model/            # Rule-based intent extractor
├── data/                       # Knowledge base and media
│   ├── campus_kb.json          # 154-entry structured knowledge base
│   ├── images/                 # Campus location images
│   └── audio_samples/          # Sample audio queries
├── frontend/                   # Streamlit interfaces
│   ├── chat_app.py             # Chat UI
│   ├── admin_app.py            # Admin dashboard
│   ├── campus_map.py           # Folium map builder
│   └── utils.py                # API call helpers
├── tests/                      # Test suite
│   ├── conftest.py             # Shared fixtures and mocks
│   ├── unit/                   # Node-level unit tests
│   └── integration/            # Full pipeline integration tests
├── entrypoints/                # CLI entry points per pipeline
├── .github/workflows/ci.yml    # GitHub Actions CI/CD pipeline
├── requirements.txt            # Pinned dependencies
└── pyproject.toml              # Project config and pytest settings
```

---

## 10. Setup & Installation

### Prerequisites

- Python 3.11
- Git
- A Groq API key (free at [console.groq.com](https://console.groq.com))
- A HuggingFace API token (free at [huggingface.co](https://huggingface.co))

### Installation

```bash
# Clone the repository
git clone https://github.com/rohantabhamar/Smart-Campus-Tour-Information-Multi-Modal-Chatbot.git
cd Smart-Campus-Tour-Information-Multi-Modal-Chatbot

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create `.env.dev` in the project root:

```ini
APP_ENV=dev
GROQ_API_KEY=your_groq_api_key_here
HUGGINGFACE_API_TOKEN=your_hf_token_here
```

---

## 11. Running the System

### Start the API server

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Start the chat interface

```bash
streamlit run frontend/chat_app.py
```

Open: [http://localhost:8501](http://localhost:8501)

### Start the admin dashboard

```bash
streamlit run frontend/admin_app.py
```

Open: [http://localhost:8502](http://localhost:8502)

### Test individual pipelines via CLI

```bash
python -m entrypoints.text
python -m entrypoints.audio
python -m entrypoints.image
python -m entrypoints.audio_with_text
python -m entrypoints.multimodal
```

---

## 12. Testing

```bash
# Run all tests
pytest tests/ -v

# Run unit tests only (fast, no model files needed)
pytest tests/unit/ -v

# Run integration tests (requires model files)
pytest tests/integration/ -v

# Run with coverage
pytest tests/ -v --tb=short
```

---

## 13. CI/CD

The project uses GitHub Actions for continuous integration. Three jobs run automatically on every push to `main`:

```yaml
Run Tests     → pytest tests/unit/ (26 tests)
Code Quality  → flake8 (style + correctness)
Security Scan → bandit (hardcoded secrets) + safety (vulnerable packages)
```

View pipeline runs at: [GitHub Actions](https://github.com/rohantabhamar/Smart-Campus-Tour-Information-Multi-Modal-Chatbot/actions)

---

## 14. Results & Evaluation

### Pipeline Performance (on development hardware, CPU only)

| Pipeline | Avg Response Time | Bottleneck |
|----------|------------------|-----------|
| Text | ~2–4 seconds | Groq API latency |
| Audio | ~15–25 seconds | Whisper transcription |
| Image | ~3–6 seconds | CLIP encoding + Groq |
| Audio + Text | ~15–25 seconds | Whisper transcription |
| Multimodal | ~20–35 seconds | Whisper + DistilBERT + Fusion MLP + Groq |

### Model Accuracy (from training notebooks)

| Model | Metric | Score |
|-------|--------|-------|
| DistilBERT intent classifier | Accuracy | See `notebook/distilbert_training.png` |
| Fusion MLP location classifier | Accuracy | See `notebook/fusion_final_results.png` |
| spaCy NER | F1 | See `notebook/ner_prf.png` |
| Whisper (WER) | Word Error Rate | See `notebook/voice_wer_analysis.png` |
| CLIP + FAISS retrieval | Top-1 accuracy | See `notebook/clip_final_evaluation.png` |

---

## License

This project was developed as an academic research project. All rights reserved.

---

## Author

**Rohanta Bhamar**
[GitHub](https://github.com/rohantabhamar) · [Smart Campus Chatbot Repository](https://github.com/rohantabhamar/Smart-Campus-Tour-Information-Multi-Modal-Chatbot)
