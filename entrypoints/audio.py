from config.settings import validate
validate()
from core.audio_graph import audio_workflow

def main():
    path = input("Enter audio file path: ")
    result = audio_workflow.invoke({"query": path})
    print(result["answer"])

if __name__ == "__main__":
    main()