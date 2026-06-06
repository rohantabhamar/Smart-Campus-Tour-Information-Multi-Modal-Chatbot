from core.multimodel_graph import multimodal_workflow
from core.state import MultiModalState


def default_state(
    query: str | None = None,
    audio_path: str | None = None,
    image_path: str | None = None,
) -> MultiModalState:
    return {
        "query":                  query,
        "audio_path":             audio_path,
        "image_path":             image_path,
        "transcript":             None,
        "text_intent":            None,
        "text_intent_embedding":  None,
        "voice_intent":           None,
        "voice_intent_embedding": None,
        "image_embedding":        None,
        "top_3_matches":          None,
        "best_match":             None,
        "fusion_location":        None,
        "fusion_confidence":      None,
        "kb_context":             None,
        "final_text_query":       None,
        "final_voice_query":      None,
        "final_image_location":   None,
        "answer":                 None,
        "error":                  None,
    }


def test_text_and_image(mock_llm, mock_clip, mock_faiss, mock_kb):
    result = multimodal_workflow.invoke(default_state(
        query="Where is this place?",
        image_path="fake_image.jpg",
    ))
    assert "answer" in result
    assert result["answer"] != ""


def test_voice_and_image(mock_whisper, mock_llm, mock_clip, mock_faiss, mock_kb):
    result = multimodal_workflow.invoke(default_state(
        audio_path="fake_audio.wav",
        image_path="fake_image.jpg",
    ))
    assert "answer" in result
    assert result["answer"] != ""


def test_text_voice_and_image(mock_whisper, mock_llm, mock_clip, mock_faiss, mock_kb):
    result = multimodal_workflow.invoke(default_state(
        query="What events are happening here?",
        audio_path="fake_audio.wav",
        image_path="fake_image.jpg",
    ))
    assert "answer" in result
    assert result["answer"] != ""


def test_image_only(mock_llm, mock_clip, mock_faiss, mock_kb):
    result = multimodal_workflow.invoke(default_state(
        image_path="fake_image.jpg",
    ))
    assert "answer" in result
    assert result["answer"] != ""


def test_no_input(mock_llm, mock_clip, mock_faiss, mock_kb):
    result = multimodal_workflow.invoke(default_state())
    assert "answer" in result