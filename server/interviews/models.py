import uuid
import requests
from django.conf import settings
from django.db import models
from django.db import models
from django.contrib.auth.models import User

class Interview(models.Model):
    candidate_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    s3_video_key = models.CharField(max_length=1024, blank=True, null=True)
    transcript_uri = models.URLField(blank=True, null=True)
    bedrock_result = models.JSONField(blank=True, null=True)
    body_lang_result = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.candidate_name} @{self.created_at}"
