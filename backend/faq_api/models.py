#backend/faq_api/models.py
from django.db import models
from django.contrib.postgres.fields import ArrayField

class Message(models.Model):
    message_id = models.CharField(max_length=100, unique=True)
    text = models.TextField()
    author_name = models.CharField(max_length=100, null=True, blank=True)
    channel = models.CharField(max_length=50, null=True, blank=True)
    embedding = ArrayField(models.FloatField(), null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()
    embedding = ArrayField(models.FloatField(), null=True, blank=True)

class ClusterResult(models.Model):
    cluster_id = models.IntegerField()
    message_count = models.IntegerField()
    top_message = models.TextField()
    matched_faq = models.TextField()
    similarity = models.FloatField()
    gpt_evaluation = models.TextField()
    sentiment = models.CharField(max_length=20)
    keywords = models.JSONField()
    summary = models.TextField()
    created_at = models.DateTimeField()
    coverage = models.CharField(max_length=20)
    resolution_score = models.IntegerField()
    resolution_reason = models.TextField()
    faq_suggestion = models.JSONField(null=True, blank=True)
    topic_label = models.CharField(max_length=100)

    class Meta:
        unique_together = ("cluster_id", "created_at")

