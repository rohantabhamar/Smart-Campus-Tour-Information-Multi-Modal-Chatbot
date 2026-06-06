from core.state import AudioTextBotState
from langgraph.graph import StateGraph , START , END
from nodes.audio_to_text import audio_to_text
from nodes.text_input import text_input
from nodes.merge_query import merge_query
from nodes.intent_entity_extraction import intent_entity_extraction
from nodes.kb_search import kb_search
from nodes.final_ans_generation import final_ans_generation


graph = StateGraph(AudioTextBotState)

graph.add_node("audio_to_text",audio_to_text)
graph.add_node("merge_query",merge_query)
graph.add_node('text_input',text_input)
graph.add_node("intent_entity_extraction",intent_entity_extraction)
graph.add_node("kb_search",kb_search)
graph.add_node("final_ans_generation",final_ans_generation)

graph.add_edge(START,'audio_to_text')
graph.add_edge(START,"text_input")
graph.add_edge("text_input","merge_query")
graph.add_edge('audio_to_text',"merge_query")
graph.add_edge("merge_query","intent_entity_extraction")
graph.add_edge("intent_entity_extraction","kb_search")
graph.add_edge("kb_search","final_ans_generation")
graph.add_edge("final_ans_generation",END)

audio_text_workflow = graph.compile()

