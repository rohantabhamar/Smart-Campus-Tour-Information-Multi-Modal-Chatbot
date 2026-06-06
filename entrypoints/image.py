from config.settings import validate
validate()
from core.image_graph import image_workflow

def main():
    path = input("Enter image file path: ")
    result = image_workflow.invoke({"image_path": path})
    print(result["answer"])

if __name__ == "__main__":
    main()