from nodes.audio_to_text import audio_to_text

def test_transcription(mock_whisper):
    result = audio_to_text({"query": "data/audio_samples/sample.wav"})
    assert result["query"] == "where is the library"

def test_file_not_found(mock_whisper):
    mock_whisper.transcribe.side_effect = FileNotFoundError
    result = audio_to_text({"query": "nonexistent.wav"})
    assert "error" in result

def test_empty_path(mock_whisper):
    mock_whisper.transcribe.side_effect = Exception("no file")
    result = audio_to_text({"query": ""})
    assert "error" in result