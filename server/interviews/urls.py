from django.urls import path
from . import views

urlpatterns = [
    path("generate-presigned/", views.GeneratePresignedURL.as_view(), name="generate-presigned"),
    path("notify-upload/", views.NotifyUpload.as_view(), name="notify-upload"),  # call to start transcribe
    path("transcript/<int:pk>/", views.GetTranscript.as_view(), name="get-transcript"),
    path("evaluate/<int:pk>/", views.EvaluateInterview.as_view(), name="evaluate"),
    path("rekognition/<int:pk>/", views.AnalyzeVideoBodyLanguage.as_view(), name="rekognition"),
    path("bedrock-infer/", views.invoke_bedrock, name="bedrock-infer"),
]
