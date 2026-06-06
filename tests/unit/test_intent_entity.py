from nodes.intent_entity_extraction import intent_entity_extraction

def test_library_query():
    result = intent_entity_extraction({"query": "Where is the library?"})
    assert "intent"         in result
    assert "entities"       in result
    assert "category_hints" in result
    assert "nav_pair"       in result

def test_navigation_query():
    result = intent_entity_extraction({"query": "route from library to gym"})
    assert result["intent"] == "navigation"
    assert result["nav_pair"] is not None
    assert result["nav_pair"]["source"] != ""
    assert result["nav_pair"]["destination"] != ""
    assert "entities" in result
    assert "category_hints" in result

def test_empty_query():
    result = intent_entity_extraction({"query": ""})
    assert "intent" in result

def test_unknown_query():
    result = intent_entity_extraction({"query": "asdfghjkl"})
    assert "intent" in result