from nodes.llm_node import llm_node

def test_normal_response(mock_llm, base_image_state):
    result = llm_node(base_image_state)
    assert "answer" in result
    assert result["answer"] != ""

def test_upstream_error(mock_llm, base_image_state):
    base_image_state["error"] = "FAISS failed"
    result = llm_node(base_image_state)
    assert "Sorry" in result["answer"]
    mock_llm.invoke.assert_not_called()

def test_llm_failure(mock_llm, base_image_state):
    mock_llm.invoke.side_effect = Exception("Groq timeout")
    result = llm_node(base_image_state)
    assert "unable" in result["answer"].lower()