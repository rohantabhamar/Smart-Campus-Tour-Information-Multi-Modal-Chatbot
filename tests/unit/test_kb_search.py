from nodes.kb_search import kb_search

def test_regular_query(base_text_state):
    result = kb_search(base_text_state)
    assert "kb_results"   in result
    assert "kb_context"   in result
    assert "is_list_mode" in result

def test_navigation_query():
    state = {
        "query":          "directions from library to gym",
        "intent":         "navigation",
        "entities":       [],
        "category_hints": [],
        "nav_pair":       {"source": "library", "destination": "gym"},
        "merge_query":    None,
    }
    result = kb_search(state)
    assert "kb_context" in result

def test_unknown_location(base_text_state):
    base_text_state["query"]    = "where is xyzabc"
    base_text_state["entities"] = [{"text": "xyzabc", "type": "misc", "score": 1.0}]
    result = kb_search(base_text_state)
    assert "kb_context" in result