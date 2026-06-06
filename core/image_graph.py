from core.state import ImageBotState
from nodes.clip_node import clip_node
from nodes.kb_node import kb_node
from nodes.faiss_node import faiss_node
from nodes.llm_node import llm_node
# from nodes.image_workflow_node import clip_node,faiss_node,kb_node,llm_node
from langgraph.graph import StateGraph , END


graph = StateGraph(ImageBotState)

graph.add_node("clip",  clip_node)
graph.add_node("faiss", faiss_node)
graph.add_node("kb",    kb_node)
graph.add_node("llm",   llm_node)

graph.set_entry_point("clip")
graph.add_edge("clip",  "faiss")
graph.add_edge("faiss", "kb")
graph.add_edge("kb",    "llm")
graph.add_edge("llm",   END)


image_workflow = graph.compile()

