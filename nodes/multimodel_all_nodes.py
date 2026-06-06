import torch
import numpy as np
from PIL import Image
from core.model_loader import get_whisper_model, get_distilbert, get_clip_model, get_faiss, get_fusion_mlp, get_kb, DEVICE
from models.rules_model.rules_extractor import rules_classify_intent as predict_rules
from langchain_groq import ChatGroq
from config.settings import GROQ_API_KEY, GROQ_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS, GROQ_MAX_RETRIES
import time
from config.logger import get_logger
logger = get_logger(__name__)

_llm = None


def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            model=GROQ_MODEL,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
            api_key=GROQ_API_KEY,
        )
    return _llm


def whisper_node(state: dict) -> dict:
    logger.debug("whisper_node → entry")
    t0 = time.perf_counter()
    try:
        audio_path = state.get("audio_path")
        if not audio_path:
            return {"transcript": None, "final_voice_query": None,
                    "voice_intent": None, "voice_intent_embedding": None}
        transcript = get_whisper_model().transcribe(audio_path, language="en")["text"].strip()
        logger.info(f"whisper_node → duration={time.perf_counter()-t0:.3f}s")
        return {"transcript": transcript, "final_voice_query": transcript}
    except Exception as e:
        logger.error(f"whiesper node → failed: {e}", exc_info=True)
        return {"error": str(e)}


def text_distilbert_node(state: dict) -> dict:
    logger.debug("text_distilbert_node → entry")
    t0 = time.perf_counter()
    try:
        query = state.get("query")
        if not query:
            return {"text_intent": None, "text_intent_embedding": None, "final_text_query": None}

        tokenizer, model = get_distilbert()
        enc = tokenizer(query, max_length=64, padding="max_length",
                        truncation=True, return_tensors="pt")
        with torch.no_grad():
            out = model(input_ids=enc["input_ids"].to(DEVICE),
                        attention_mask=enc["attention_mask"].to(DEVICE))
            emb = out.last_hidden_state[:, 0, :]
            emb = emb / emb.norm(dim=-1, keepdim=True)

        logger.info(f"text_distilbert_node → duration={time.perf_counter()-t0:.3f}s")

        return {
            "text_intent_embedding": emb.cpu().numpy().squeeze().tolist(),
            "text_intent": predict_rules(query),
            "final_text_query": query,
        }

    except Exception as e:
        logger.error(f"text distilbert node → failed: {e}", exc_info=True)
        return {"error": str(e)}


def voice_distilbert_node(state: dict) -> dict:
    logger.debug("voice_distilbert_node → entry")
    t0 = time.perf_counter()
    try:
        transcript = state.get("transcript")
        if not transcript:
            return {"voice_intent": None, "voice_intent_embedding": None}

        tokenizer, model = get_distilbert()
        enc = tokenizer(transcript, max_length=64, padding="max_length",
                        truncation=True, return_tensors="pt")
        with torch.no_grad():
            out = model(input_ids=enc["input_ids"].to(DEVICE),
                        attention_mask=enc["attention_mask"].to(DEVICE))
            emb = out.last_hidden_state[:, 0, :]
            emb = emb / emb.norm(dim=-1, keepdim=True)

        logger.info(f"voice_distilbert_node → duration={time.perf_counter()-t0:.3f}s")

        return {
            "voice_intent_embedding": emb.cpu().numpy().squeeze().tolist(),
            "voice_intent": predict_rules(transcript),
        }

    except Exception as e:
        logger.error(f"voice distilbert node → failed: {e}", exc_info=True)
        return {"error": str(e)}


def clip_node(state: dict) -> dict:
    logger.debug("clip_node → entry")
    t0 = time.perf_counter()
    try:
        image_path = state.get("image_path")
        if not image_path:
            return {"image_embedding": None, "final_image_location": None}

        clip_model, preprocess = get_clip_model()
        image = preprocess(Image.open(image_path).convert("RGB")).unsqueeze(0).to(DEVICE)
        with torch.no_grad():
            emb = clip_model.encode_image(image)
            emb = emb / emb.norm(dim=-1, keepdim=True)

        logger.info(f"clip_node → duration={time.perf_counter()-t0:.3f}s")

        return {"image_embedding": emb.cpu().numpy().squeeze().tolist(), "final_image_location": None}
    except Exception as e:
        logger.error(f"clip node → failed: {e}", exc_info=True)
        return {"error": str(e)}


def faiss_node(state: dict) -> dict:
    logger.debug("faiss_node → entry")
    t0 = time.perf_counter()
    try:
        image_embedding = state.get("image_embedding")
        if not image_embedding:
            return {"top_3_matches": None, "best_match": None}

        faiss_index, image_records = get_faiss()
        query = np.array(image_embedding, dtype="float32").reshape(1, -1)
        scores, indices = faiss_index.search(query, 3)

        top_3 = [{"score": round(float(s), 3),
                  "category": image_records[i]["category"],
                  "kb_name": image_records[i]["kb_name"]}
                 for s, i in zip(scores[0], indices[0])]

        non_self = [r for r in top_3 if r["score"] < 0.999]
        best = non_self[0] if non_self else top_3[0]
        logger.info(f"faiss_node → duration={time.perf_counter()-t0:.3f}s")
        return {"top_3_matches": top_3, "best_match": best}
    except Exception as e:
        logger.error(f"faiss node → failed: {e}", exc_info=True)
        return {"error": str(e)}


def fusion_mlp_node(state: dict) -> dict:
    logger.debug("fusion_mlp_node → entry")
    t0 = time.perf_counter()
    try:
        image_emb = state.get("image_embedding")
        text_emb = state.get("text_intent_embedding")
        voice_emb = state.get("voice_intent_embedding")

        nlp_emb = text_emb or voice_emb
        if not nlp_emb or not image_emb:
            return {"fusion_location": None, "fusion_confidence": None}

        fusion_vec = np.concatenate([np.array(image_emb, dtype="float32"),
                                     np.array(nlp_emb, dtype="float32")])
        input_tensor = torch.tensor(fusion_vec).unsqueeze(0).to(DEVICE)

        model, idx_to_class = get_fusion_mlp()
        with torch.no_grad():
            probs = torch.softmax(model(input_tensor), dim=1).cpu().numpy().squeeze()
            pred = probs.argmax()

        logger.info(f"fusion_mlp_node → duration={time.perf_counter()-t0:.3f}s")
        return {
            "fusion_location": idx_to_class[pred],
            "fusion_confidence": round(float(probs[pred]), 3),
            "final_image_location": idx_to_class[pred],
        }
    except Exception as e:
        logger.error(f"fusion mlp node → failed: {e}", exc_info=True)
        return {"error": str(e)}


def llm_node(state: dict):
    logger.debug("llm_node → entry")
    t0 = time.perf_counter()

    if state.get("error"):
        logger.warning(f"llm_node → skipped due to upstream error: {state['error']}")
        return {"answer": f"Sorry, something went wrong: {state['error']}"}

    kb_context = state.get("kb_context", "No KB data available.")
    text_query = state.get("final_text_query")
    voice_query = state.get("final_voice_query")
    image_loc = state.get("final_image_location")
    confidence = state.get("fusion_confidence", 0.0)

    user_context = ""
    if text_query:
        user_context += f"Text query   : {text_query}\n"
    if voice_query:
        user_context += f"Voice query  : {voice_query}\n"
    if image_loc:
        user_context += f"Image shows  : {image_loc} (confidence: {confidence})\n"

    prompt = f"""You are a campus navigation assistant.

        User provided the following inputs:
        {user_context}

        Campus Knowledge Base:
        {kb_context}

        Based on the above information give a helpful friendly response.
        First tell what location was identified.
        Then answer what the user is asking about.
        If user asked about directions, give step by step directions.
        If user asked about hours, state them clearly.
        Keep it concise.
        """

    for attempt in range(1, GROQ_MAX_RETRIES + 1):
        try:
            response = get_llm().invoke(prompt)
            logger.info(f"llm_node → attempt={attempt} duration={time.perf_counter()-t0:.3f}s")
            return {"answer": response.content.strip()}
        except Exception as e:
            logger.warning(f"llm_node → attempt {attempt} failed: {e}")
            if attempt == GROQ_MAX_RETRIES:
                logger.error(f"llm_node → all {GROQ_MAX_RETRIES} attempts failed", exc_info=True)
                return {"answer": "Sorry, I was unable to generate a response. Please try again."}


def multimodal_kb_node(state: dict) -> dict:
    logger.debug("multimodal_kb_node→ entry")
    t0 = time.perf_counter()
    try:
        fusion_location = state.get("fusion_location")
        if not fusion_location:
            return {"kb_context": "No location identified."}

        kb_lookup = get_kb()
        entry = kb_lookup.get(fusion_location, {})

        if not entry:
            return {"kb_context": f"No KB entry found for: {fusion_location}"}

        kb_context = f"""Name        : {entry.get('name', 'N/A')}
            Description : {entry.get('description', 'N/A')}
            Location    : {entry.get('map_reference', 'N/A')}
            Directions  : {entry.get('directions_from_entrance', 'N/A')}
            Hours       : {entry.get('opening_hours', {})}
            Events      : {entry.get('events', [])}"""

        logger.info(f"multimodal_kb_node → duration={time.perf_counter()-t0:.3f}s")

        return {"kb_context": kb_context}
    except Exception as e:
        logger.error(f"multi modal kb note → failed: {e}", exc_info=True)
        return {"error": str(e)}
