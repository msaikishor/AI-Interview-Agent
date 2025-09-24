import json
import boto3
import os
import urllib.request

# Lambda to be deployed in AWS that handles Transcribe job completion event,
# fetches transcript from transcript file URI and posts back to Django API to store transcript + trigger evaluation.
API_ENDPOINT = os.getenv("BACKEND_API_ENDPOINT")  # e.g. https://your-backend.example.com/api/transcribe-callback/
API_KEY = os.getenv("BACKEND_API_KEY")

def lambda_handler(event, context):
    # This lambda assumes it is triggered by EventBridge rule for Transcribe job state change to COMPLETED
    print("Event received:", json.dumps(event))
    detail = event.get("detail", {})
    job_name = detail.get("TranscriptionJobName")
    if not job_name:
        return {"status":"ignored"}

    # call transcribe to get full job info
    transcribe = boto3.client("transcribe")
    resp = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    transcript_uri = resp['TranscriptionJob']['Transcript']['TranscriptFileUri']
    # fetch transcript content (public s3 url or presigned) - in many setups you'll need oauth or s3 signed URL
    with urllib.request.urlopen(transcript_uri) as f:
        data = json.loads(f.read().decode())
        transcript_text = data.get("results",{}).get("transcripts",[{}])[0].get("transcript","")

    # POST back to backend to save and optionally trigger evaluation
    import requests
    requests.post(API_ENDPOINT, json={"job_name":job_name, "transcript":transcript_text}, headers={"x-api-key":API_KEY})

    return {"status":"ok"}
