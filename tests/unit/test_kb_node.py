from nodes.kb_node import kb_node

def test_known_location(mock_kb, base_image_state):
    result = kb_node(base_image_state)
    assert result["name"]        == "Library"
    assert result["description"] == "Main campus library"
    assert result["map_ref"]     == "Block A, Floor 2"

def test_unknown_location(mock_kb, base_image_state):
    base_image_state["best_match"]["kb_name"] = "Unknown Place"
    result = kb_node(base_image_state)
    assert result["name"] == "N/A"

def test_none_best_match(mock_kb, base_image_state):
    base_image_state["best_match"] = None
    result = kb_node(base_image_state)
    assert "error" in result