from config.settings import validate
validate()
from core.multimodel_graph import multimodal_workflow

def main():
    query      = input("Text query (press Enter to skip): ").strip() or None
    audio_path = input("Audio path (press Enter to skip): ").strip() or None
    image_path = input("Image path (press Enter to skip): ").strip() or None

    result = multimodal_workflow.invoke({
        "query": query, "audio_path": audio_path, "image_path": image_path,
        "transcript": None, "text_intent": None, "text_intent_embedding": None,
        "voice_intent": None, "voice_intent_embedding": None,
        "image_embedding": None, "top_3_matches": None, "best_match": None,
        "fusion_location": None, "fusion_confidence": None, "kb_context": None,
        "final_text_query": None, "final_voice_query": None,
        "final_image_location": None, "answer": None, "error": None,
    })
    print(result["answer"])

if __name__ == "__main__":
    main()