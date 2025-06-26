#backend/faq_api/serializers.py
from rest_framework import serializers
from faq_api.models import Message, FAQ, ClusterRun, ClusterResult


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ["id", "question", "answer"]


class MessageSerializer(serializers.ModelSerializer):
    matched_faq = FAQSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            "message_id",
            "text",
            "author_name",
            "channel",
            "embedding",
            "created_at",
            "sentiment",
            "gpt_label",
            "gpt_score",
            "gpt_reason",
            "matched_faq"
        ]


class ClusterRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClusterRun
        fields = ["id", "created_at", "notes", "cluster_map"]


class ClusterResultSerializer(serializers.ModelSerializer):
    matched_faq = FAQSerializer(read_only=True)
    run = ClusterRunSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True) 

    class Meta:
        model = ClusterResult
        fields = [
            "cluster_id",
            "run",
            "message_count",
            "top_message",
            "matched_faq",
            "similarity",
            "gpt_evaluation",
            "sentiment",
            "keywords",
            "summary",
            "created_at",
            "coverage",
            "resolution_score",
            "resolution_reason",
            "faq_suggestion",
            "topic_label",
            "messages"
        ]

