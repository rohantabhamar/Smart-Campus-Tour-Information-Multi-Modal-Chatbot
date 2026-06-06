from nodes.final_ans_generation import final_ans_generation

def test_normal_answer(mock_llm, base_text_state):
    result = final_ans_generation(base_text_state)
    assert result["answer"] == "The library is on Floor 2 of Block A."

def test_upstream_error(mock_llm):
    state  = {"error": "KB search failed", "query": "library", "kb_context": ""}
    result = final_ans_generation(state)
    assert "Sorry" in result["answer"]
    mock_llm.invoke.assert_not_called()

def test_empty_kb_context(mock_llm, base_text_state):
    base_text_state["kb_context"] = ""
    result = final_ans_generation(base_text_state)
    assert "answer" in result

def test_llm_failure(mock_llm, base_text_state):
    mock_llm.invoke.side_effect = Exception("Groq rate limit")
    result = final_ans_generation(base_text_state)
    assert "answer" in result
    assert "unable" in result["answer"].lower()