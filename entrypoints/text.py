from config.settings import validate
validate()
from core.text_graph import text_workflow

def main():
    query = input("Enter your query: ")
    result = text_workflow.invoke({"query": query})
    print(result["answer"])

if __name__ == "__main__":
    main()