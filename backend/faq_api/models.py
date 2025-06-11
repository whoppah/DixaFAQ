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

    def __str__(self):
        return self.message_id


class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()
    embedding = ArrayField(models.FloatField(), null=True, blank=True)

    def __str__(self):
        return self.question[:80]  # to show just a short preview


class ClusterRun(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    cluster_map = models.JSONField(null=True, blank=True)  

    def __str__(self):
        return f"Run {self.id} at {self.created_at.isoformat()}"


class ClusterResult(models.Model):
    run = models.ForeignKey(ClusterRun, on_delete=models.CASCADE, related_name="clusters")
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
        unique_together = ("run", "cluster_id")

    def __str__(self):
        return f"Cluster {self.cluster_id} in run {self.run_id}"
