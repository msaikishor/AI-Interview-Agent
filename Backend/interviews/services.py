from .bedrock_client import BedrockClient
from .prompts import interviewer_prompt

def generate_interview_questions(role, resume_text, model="llama"):
    model_map = {
        "llama": "meta.llama3-70b-instruct-v1:0",
        "mixtral": "mistral.mixtral-8x7b-instruct-v0:1"
    }

    client = BedrockClient(model_id=model_map.get(model, model_map["llama"]))
    prompt = interviewer_prompt(role, resume_text)
    response = client.generate_text(prompt)
    return response
