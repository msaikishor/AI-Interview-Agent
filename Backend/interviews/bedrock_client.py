import boto3
import json
import os

class BedrockClient:
    def __init__(self, model_id="meta.llama3-70b-instruct-v1:0"):
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=os.getenv("AWS_REGION_NAME"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        self.model_id = model_id

    def generate_text(self, prompt, max_tokens=500, temperature=0.7):
        body = {
            "prompt": prompt,
            "max_gen_len": max_tokens,
            "temperature": temperature,
        }

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )

        result = json.loads(response["body"].read())
        return result.get("generation", "")
