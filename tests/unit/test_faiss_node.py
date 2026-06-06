from nodes.faiss_node import faiss_node

def test_normal_search(mock_faiss):
    result = faiss_node({"embedding": [0.1] * 512})
    assert "top_3_matches" in result
    assert "best_match"    in result
    assert result["best_match"]["kb_name"] == "Library"

def test_empty_embedding(mock_faiss):
    result = faiss_node({"embedding": []})
    assert "error" in result or "best_match" in result