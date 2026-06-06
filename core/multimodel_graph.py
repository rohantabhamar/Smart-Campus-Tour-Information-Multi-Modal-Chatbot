from langgraph.graph import StateGraph, START, END
from core.state import MultiModalState
from nodes.multimodel_all_nodes import whisper_node, text_distilbert_node, clip_node, faiss_node, voice_distilbert_node, fusion_mlp_node, llm_node, multimodal_kb_node

graph = StateGraph(MultiModalState)

graph.add_node("whisper_node", whisper_node)
graph.add_node("text_distilbert_node", text_distilbert_node)
graph.add_node("clip_node", clip_node)
graph.add_node("faiss_node", faiss_node)
graph.add_node("voice_distilbert_node", voice_distilbert_node)
graph.add_node("fusion_mlp_node", fusion_mlp_node)
graph.add_node("kb_search_node", multimodal_kb_node)
graph.add_node("llm_node", llm_node)

graph.add_edge(START, "whisper_node")
graph.add_edge(START, "text_distilbert_node")
graph.add_edge(START, "clip_node")

graph.add_edge("clip_node", "faiss_node")
graph.add_edge("whisper_node", "voice_distilbert_node")

graph.add_edge("faiss_node", "fusion_mlp_node")
graph.add_edge("voice_distilbert_node", "fusion_mlp_node")
graph.add_edge("text_distilbert_node", "fusion_mlp_node")

graph.add_edge("fusion_mlp_node", "kb_search_node")
graph.add_edge("kb_search_node", "llm_node")
graph.add_edge("llm_node", END)

multimodal_workflow = graph.compile()
