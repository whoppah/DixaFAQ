#backend/faq_api/models.py
from django.db import models
from django.contrib.postgres.fields import ArrayField


class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()
    embedding = ArrayField(models.FloatField(), null=True, blank=True)
    #embedding_updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.question[:80]

 
class Message(models.Model):
    message_id = models.CharField(max_length=255, primary_key=True)
    text = models.TextField()
    author_name = models.CharField(max_length=100, null=True, blank=True)
    author_email = models.EmailField(null=True, blank=True)
    channel = models.CharField(max_length=50, null=True, blank=True)
    direction = models.CharField(max_length=50, null=True, blank=True)

    csid = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    from_phone_number = models.CharField(max_length=50, null=True, blank=True)
    to_phone_number = models.CharField(max_length=50, null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)

    to = ArrayField(models.CharField(max_length=100), null=True, blank=True)
    from_field = models.CharField(max_length=100, null=True, blank=True)
    cc = ArrayField(models.CharField(max_length=100), null=True, blank=True)
    bcc = ArrayField(models.CharField(max_length=100), null=True, blank=True)

    is_automated_message = models.BooleanField(null=True, blank=True)
    voicemail_url = models.URLField(null=True, blank=True)
    recording_url = models.URLField(null=True, blank=True)
    attached_files = models.JSONField(null=True, blank=True)

    chat_input_question = models.TextField(null=True, blank=True)
    chat_input_answer = models.TextField(null=True, blank=True)
    chat_menu_text = models.TextField(null=True, blank=True)
    form_submission = models.JSONField(null=True, blank=True)

    embedding = ArrayField(models.FloatField(), null=True, blank=True)
    #embedding_updated_at = models.DateTimeField(null=True, blank=True)

    sentiment = models.CharField(max_length=20, null=True, blank=True)
    gpt_score = models.IntegerField(null=True, blank=True)
    gpt_label = models.CharField(max_length=50, null=True, blank=True)
    gpt_reason = models.TextField(null=True, blank=True)

    matched_faq = models.ForeignKey(
        FAQ, null=True, blank=True, on_delete=models.SET_NULL, related_name="matched_messages"
    )

    def __str__(self):
        return self.message_id



class ClusterRun(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    cluster_map = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Run {self.message_id} at {self.created_at.isoformat()}"


class ClusterResult(models.Model):
    run = models.ForeignKey(ClusterRun, on_delete=models.CASCADE, related_name="clusters")
    cluster_id = models.IntegerField()
    message_count = models.IntegerField()
    top_message = models.TextField()

    matched_faq = models.ForeignKey(
        FAQ, null=True, blank=True, on_delete=models.SET_NULL, related_name="matched_clusters"
    )
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
    messages = models.ManyToManyField("Message", related_name="cluster_results", blank=True)

    class Meta:
        unique_together = ("run", "cluster_id")

    def __str__(self):
        return f"Cluster {self.cluster_id} in run {self.run_id}"
