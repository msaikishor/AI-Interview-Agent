import os
import uuid
import json
import boto3
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Interview
from .serializers import InterviewSerializer
from botocore.client import Config

# S3 client
s3 = boto3.client("s3", region_name=settings.AWS_REGION)

# Bedrock runtime client (bedrock-runtime)
bedrock = boto3.client("bedrock-runtime", region_name=settings.AWS_REGION)

# Transcribe
transcribe = boto3.client("transcribe", region_name=settings.AWS_REGION)

# Rekognition
rekognition = boto3.client("rekognition", region_name=settings.AWS_REGION)

class GeneratePresignedURL(APIView):
    """
    Generate a presigned POST for client to directly upload video to S3.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        filename = request.data.get("filename")
        candidate_name = request.data.get("candidate_name","candidate")
        if not filename:
            return Response({"error":"filename required"}, status=400)

        key = f"interviews/{candidate_name}/{uuid.uuid4()}_{filename}"

        # policy/form fields:
        presigned_post = s3.generate_presigned_post(
            Bucket=settings.AWS_S3_BUCKET,
            Key=key,
            Fields={"acl":"private"},
            Conditions=[
                {"acl":"private"},
                ["content-length-range", 1, 200 * 1024 * 1024],  # up to 200MB
            ],
            ExpiresIn=3600
        )

        # create DB row
        interview = Interview.objects.create(candidate_name=candidate_name, s3_video_key=key)
        return Response({"presigned_post": presigned_post, "interview_id": interview.id})

class NotifyUpload(APIView):
    """
    Client notifies backend after upload (or you can wire S3 Event -> Lambda -> Endpoint).
    This will start a Transcribe job and return job info.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        interview_id = request.data.get("interview_id")
        interview = Interview.objects.get(pk=interview_id)
        media_uri = f"s3://{settings.AWS_S3_BUCKET}/{interview.s3_video_key}"

        job_name = f"transcribe-{interview_id}-{uuid.uuid4().hex[:8]}"
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": media_uri},
            MediaFormat="mp4",  # or "mp3"/"wav" depending on your upload
            LanguageCode="en-US",
            OutputBucketName=settings.AWS_S3_BUCKET  # transcript will be saved here by Transcribe
        )

        return Response({"job_name": job_name, "interview_id": interview_id})

class GetTranscript(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        # find transcription file or job
        interview = Interview.objects.get(pk=pk)
        # naive: list objects under expected transcription prefix to find transcript file
        # A robust implementation should call transcribe.get_transcription_job(jobName)
        # Then read the transcript URI from response['TranscriptionJob']['Transcript']['TranscriptFileUri']
        return Response({"transcript_uri": interview.transcript_uri or ""})

class EvaluateInterview(APIView):
    permission_classes = [permissions.AllowAny]
    """
    Use Bedrock model to evaluate candidate answers and Amazon Q (if desired).
    """
    def post(self, request, pk=None):
        # Accept raw text or use stored transcript (if available)
        interview = Interview.objects.get(pk=request.data.get("interview_id") or pk)
        text = request.data.get("text")
        if not text:
            # If transcript saved in S3, fetch it
            if interview.transcript_uri:
                s3r = boto3.resource("s3", region_name=settings.AWS_REGION)
                # transcript_uri likely points to an S3 object URL; implement fetching appropriately.
                # For template, assume text provided.
                text = "transcript text placeholder - please pass text in request"
            else:
                return Response({"error":"text required"}, status=400)

        # Build a prompt to evaluate candidate performance
        prompt = f"""
You are an interview evaluator. Given the candidate transcript below, produce:
1) A 3-point summary of strengths.
2) A 3-point summary of weaknesses.
3) A suggested score (0-10) in categories: Communication, Technical, Culture-Fit.
Format as JSON with keys: strengths, weaknesses, scores, recommendations.

Transcript:
{text}
"""

        # call bedrock runtime invoke_model
        model_id = settings.BEDROCK_MODEL_ID
        response = bedrock.invoke_model(
            modelId=model_id,
            contentType="application/json",
            body=json.dumps({
                "input": prompt,
                "max_tokens": 800,
                "temperature": 0.2
            })
        )

        # response body is a stream of bytes — decode
        body_bytes = response["body"].read()
        body_text = body_bytes.decode("utf-8")
        # Depending on model format you may need to parse JSON inside the model output
        interview.bedrock_result = {"raw": body_text}
        interview.save()

        return Response({"bedrock_raw": body_text})

class AnalyzeVideoBodyLanguage(APIView):
    permission_classes = [permissions.AllowAny]
    """
    Trigger Rekognition StartLabelDetection or call SageMaker endpoint to analyze body language.
    Here we show a Rekognition video example starting an asynchronous job (you need SNS/Role configured).
    """
    def post(self, request, pk):
        interview = Interview.objects.get(pk=pk)
        s3_bucket = settings.AWS_S3_BUCKET
        video_key = interview.s3_video_key

        response = rekognition.start_label_detection(
            Video={'S3Object': {'Bucket': s3_bucket, 'Name': video_key}},
            NotificationChannel={
                # Must configure SNS topic ARN and IAM role ARN for Rekognition to publish completion
                'SNSTopicArn': os.getenv("REKOG_SNS_TOPIC_ARN"),
                'RoleArn': os.getenv("REKOG_ROLE_ARN")
            }
        )
        return Response({"job_id": response.get("JobId")})
