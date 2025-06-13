#backend/faq_api/views.py
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, filters
from django.conf import settings
from django.http import HttpResponse
from django.db.models import Prefetch, Q
import csv

from faq_api.models import Message, FAQ, ClusterRun, ClusterResult
from faq_api.serializers import (
    MessageSerializer,
    FAQSerializer,
    ClusterRunSerializer,
    ClusterResultSerializer,
)
from faq_api.utils.gpt import GPTFAQAnalyzer
from faq_api.utils.sentiment import SentimentAnalyzer
from faq_api.utils.clustering import extract_keywords
from faq_api.tasks import async_download_and_process


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Message.objects.all().select_related("matched_faq")
    serializer_class = MessageSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["text", "author_name", "channel"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]


class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["question", "answer"]


class ClusterRunViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ClusterRun.objects.all()
    serializer_class = ClusterRunSerializer
    ordering = ["-created_at"]


class ClusterResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ClusterResult.objects.select_related("matched_faq", "run")
    serializer_class = ClusterResultSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["topic_label", "summary", "sentiment"]
    ordering_fields = ["created_at", "resolution_score"]
    ordering = ["-created_at"]

    @action(detail=False, methods=["get"], url_path="export")
    def export_csv(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=cluster_results.csv"
        writer = csv.writer(response)

        writer.writerow([
            "cluster_id", "topic_label", "summary", "sentiment",
            "resolution_score", "resolution_reason", "coverage",
            "created_at"
        ])

        for cluster in self.get_queryset():
            writer.writerow([
                cluster.cluster_id,
                cluster.topic_label,
                cluster.summary,
                cluster.sentiment,
                cluster.resolution_score,
                cluster.resolution_reason,
                cluster.coverage,
                cluster.created_at.isoformat()
            ])

        return response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user_info(request):
    user = request.user
    return Response({
        "username": user.username,
        "is_admin": user.is_staff or user.is_superuser,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def trigger_pipeline(request):
    if not request.user.is_staff:
        return Response({"error": "Forbidden"}, status=403)
    async_download_and_process.delay()
    return Response({"status": "Pipeline started"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_clusters_with_messages(request):
    topic_label = request.GET.get("topic_label")
    sentiment = request.GET.get("sentiment")

    filters_q = Q()
    if topic_label:
        filters_q &= Q(topic_label__icontains=topic_label)
    if sentiment:
        filters_q &= Q(sentiment__iexact=sentiment)

    clusters = ClusterResult.objects.filter(filters_q).select_related("matched_faq", "run")

    results = []
    for cluster in clusters:
        related_messages = Message.objects.filter(
            embedding__isnull=False,
            created_at__lte=cluster.created_at
        )[:10]

        results.append({
            "cluster": ClusterResultSerializer(cluster).data,
            "messages": MessageSerializer(related_messages, many=True).data
        })

    return Response({"results": results})
