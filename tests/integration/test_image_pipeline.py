from core.image_graph import image_workflow


result = image_workflow.invoke({'image_path':r'E:\Rohanta_AI_workbook\campus_chatbot\data\images\gym\gym_02.jpg'})["answer"]

print(result)