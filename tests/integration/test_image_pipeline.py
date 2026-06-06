from core.image_graph import image_workflow


def test_image_library(mock_clip, mock_faiss, mock_kb, mock_llm):
    result = image_workflow.invoke({"image_path": "fake_image.jpg"})
    assert "answer" in result
    assert result["answer"] != ""


def test_image_missing_file(mock_clip, mock_faiss, mock_kb, mock_llm):
    import unittest.mock as m
    mock_clip[0].encode_image.side_effect = FileNotFoundError
    result = image_workflow.invoke({"image_path": "nonexistent.jpg"})
    assert "answer" in result or "error" in result