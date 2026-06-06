from core.audio_graph import audio_workflow


def test_audio_transcription_and_answer(mock_whisper, mock_llm, mock_kb):
    result = audio_workflow.invoke({"query": "fake_audio.wav"})
    assert "answer" in result
    assert result["answer"] != ""


def test_audio_missing_file(mock_whisper, mock_llm, mock_kb):
    mock_whisper.transcribe.side_effect = FileNotFoundError
    result = audio_workflow.invoke({"query": "nonexistent.wav"})
    assert "answer" in result or "error" in result