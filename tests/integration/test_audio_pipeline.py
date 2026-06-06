from core.audio_graph import audio_workflow


result = audio_workflow.invoke({'query':r'E:\Rohanta_AI_workbook\campus_chatbot\data\audio_samples\sample_0032.wav'})
print(result)
print(f"Intent     : {result.get('intent')}")
print(f"Entities   : {result.get('entities')}")
print(f"KB context : {result.get('kb_context')}")
print(f"Answer     : {result.get('answer')}")