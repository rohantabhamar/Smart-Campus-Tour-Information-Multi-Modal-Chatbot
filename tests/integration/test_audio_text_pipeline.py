from core.audio_with_text_graph import audio_text_workflow

result = audio_text_workflow.invoke({'text_query': "Where is the library?",'query':r'E:\Rohanta_AI_workbook\campus_chatbot\data\audio_samples\sample_0050.wav'})["answer"]
print(result)