from core.audio_with_text_graph import audio_text_workflow


def test_audio_and_text(mock_whisper, mock_llm, mock_kb):
    result = audio_text_workflow.invoke({
        "query": "fake_audio.wav",
        "text_query": "Where is the library?",
    })
    assert "answer" in result
    assert result["answer"] != ""


def test_audio_only(mock_whisper, mock_llm, mock_kb):
    result = audio_text_workflow.invoke({
        "query": "fake_audio.wav",
        "text_query": None,
    })
    assert "answer" in result


def test_missing_audio(mock_whisper, mock_llm, mock_kb):
    mock_whisper.transcribe.side_effect = FileNotFoundError
    result = audio_text_workflow.invoke({
        "query": "nonexistent.wav",
        "text_query": "library",
    })
    assert "answer" in result or "error" in result