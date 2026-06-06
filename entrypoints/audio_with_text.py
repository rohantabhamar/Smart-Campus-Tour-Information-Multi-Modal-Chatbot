from config.settings import validate
validate()
from core.audio_with_text_graph import audio_text_workflow


def main():
    text_query = input("Enter text query (press Enter to skip): ").strip() or None
    audio_path = input("Enter audio file path: ").strip()

    result = audio_text_workflow.invoke({
        "text_query": text_query,
        "query":      audio_path,
    })
    print(result["answer"])

if __name__ == "__main__":
    main()