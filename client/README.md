# Interview Platform (template)

## Quick start (dev)
1. Copy `.env.example` to `.env` and fill AWS credentials and names.
2. Start backend:
   cd backend
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver 0.0.0.0:8000

3. Start frontend:
   cd frontend
   npm install
   npm run dev

## What you must change (IMPORTANT)
- In backend/.env:
  - AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
  - AWS_S3_BUCKET: create S3 bucket
  - BEDROCK_MODEL_ID: default `meta.llama3-70b-instruct-v1:0` or your chosen model. (Example docs). :contentReference[oaicite:2]{index=2}
  - REKOG_ROLE_ARN and REKOG_SNS_TOPIC_ARN for Rekognition Video asynchronous jobs.
  - SAGEMAKER_ENDPOINT: your deployed SageMaker model endpoint if you will use a custom body-language ML model.

- IAM roles and permissions:
  - Backend EC2 / ECS / Lambda role needs S3 Get/Put, Transcribe Start/Get, Rekognition (if used), bedrock:InvokeModel permission, SageMaker:InvokeEndpoint.
  - See AWS docs for precisely required actions and the `bedrock:InvokeModel` permission. :contentReference[oaicite:3]{index=3}

## Key AWS flows & references
- Bedrock invoke_model: see examples and model IDs. :contentReference[oaicite:4]{index=4}
- Transcribe: upload media to S3 then StartTranscriptionJob. You can use EventBridge/Lambda for completion. :contentReference[oaicite:5]{index=5}
- S3 presigned POST usage: boto3.generate_presigned_post examples. :contentReference[oaicite:6]{index=6}
- Rekognition Video StartLabelDetection: requires SNS and IAM Role for notifications. :contentReference[oaicite:7]{index=7}
