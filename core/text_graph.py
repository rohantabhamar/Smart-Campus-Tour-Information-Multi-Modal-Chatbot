from langgraph.graph import StateGraph , START , END
from core.state import TextBotState
# from nodes.text_workflow_nodes import intent_entity_extraction,kb_search,final_ans_generation

from nodes.intent_entity_extraction import intent_entity_extraction
from nodes.kb_search import kb_search
from nodes.final_ans_generation import final_ans_generation



graph = StateGraph(TextBotState)

graph.add_node("intent_entity_extraction",intent_entity_extraction)
graph.add_node("kb_search",kb_search)
graph.add_node("final_ans_generation",final_ans_generation)

graph.add_edge(START,"intent_entity_extraction")
graph.add_edge("intent_entity_extraction","kb_search")
graph.add_edge("kb_search","final_ans_generation")
graph.add_edge("final_ans_generation",END)

text_workflow = graph.compile()
