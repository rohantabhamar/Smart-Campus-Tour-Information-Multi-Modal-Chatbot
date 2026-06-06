from core.text_graph import text_workflow

def test_text_library_query():
    result = text_workflow.invoke({"query": "Where is the library?"})
    assert "answer" in result
    assert result["answer"] != ""

def test_text_hours_query():
    result = text_workflow.invoke({"query": "What are the cafeteria opening hours?"})
    assert "answer" in result