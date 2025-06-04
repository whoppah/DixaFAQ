from django.db import models
from django.contrib.postgres.fields import ArrayField

class Message(models.Model):
    message_id = models.CharField(max_length=100, unique=True)
    text = models.TextField()
    author_name = models.CharField(max_length=100, null=True, blank=True)
    channel = models.CharField(max_length=50, null=True, blank=True)
    embedding = ArrayField(models.FloatField(), null=True, blank=True)

class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()
    embedding = ArrayField(models.FloatField(), null=True, blank=True)
