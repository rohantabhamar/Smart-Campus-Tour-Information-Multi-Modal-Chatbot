from langgraph.graph import StateGraph , START , END
from core.state import AudioBotState
# from nodes.audio_workflow_nodes import audio_to_text,intent_entity_extraction,kb_search,final_ans_generation
from nodes.audio_to_text import audio_to_text
from nodes.intent_entity_extraction import intent_entity_extraction
from nodes.kb_search import kb_search
from nodes.final_ans_generation import final_ans_generation


graph = StateGraph(AudioBotState)

graph.add_node("audio_to_text",audio_to_text)
graph.add_node("intent_entity_extraction",intent_entity_extraction)
graph.add_node("kb_search",kb_search)
graph.add_node("final_ans_generation",final_ans_generation)

graph.add_edge(START,'audio_to_text')
graph.add_edge('audio_to_text',"intent_entity_extraction")
graph.add_edge("intent_entity_extraction","kb_search")
graph.add_edge("kb_search","final_ans_generation")
graph.add_edge("final_ans_generation",END)

audio_workflow = graph.compile()

