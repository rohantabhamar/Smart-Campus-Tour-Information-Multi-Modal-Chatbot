from core.text_graph import text_workflow


def test_text_library_query(mock_llm, mock_kb):
    result = text_workflow.invoke({"query": "Where is the library?"})
    assert "answer" in result
    assert result["answer"] != ""


def test_text_hours_query(mock_llm, mock_kb):
    result = text_workflow.invoke({"query": "What are the cafeteria opening hours?"})
    assert "answer" in result


def test_text_empty_query(mock_llm, mock_kb):
    result = text_workflow.invoke({"query": "unknown place xyz"})
    assert "answer" in result


def test_text_navigation_query(mock_llm, mock_kb):
    result = text_workflow.invoke({"query": "route from library to gym"})
    assert "answer" in result