from nodes.merge_query import merge_query

def test_both_inputs():
    result = merge_query({"query": "audio transcript", "text_query": "library"})
    assert result["merge_query"] == "audio transcript library"

def test_only_audio():
    result = merge_query({"query": "audio transcript", "text_query": None})
    assert result["merge_query"] == "audio transcript"

def test_only_text():
    result = merge_query({"query": "", "text_query": "library hours"})
    assert result["merge_query"] == "library hours"

def test_missing_text_query():
    result = merge_query({"query": "audio transcript", "text_query": None})
    assert "merge_query" in result