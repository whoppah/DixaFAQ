#backend/faq_api/serializers.py
from rest_framework import serializers

class ClusterResultSerializer(serializers.Serializer):
    cluster_id = serializers.IntegerField()
    message_count = serializers.IntegerField()
    top_message = serializers.CharField()
    matched_faq = serializers.CharField()
    similarity = serializers.FloatField()
    gpt_evaluation = serializers.CharField()
    sentiment = serializers.CharField()
    keywords = serializers.ListField(child=serializers.CharField())
    summary = serializers.CharField()

