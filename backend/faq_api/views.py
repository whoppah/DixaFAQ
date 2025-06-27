# backend/faq_api/views.py
import csv
import collections
import json
import logging
import re
import traceback
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from django.http import HttpResponse
from django.utils.timezone import now
from rest_framework import filters, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from faq_api.models import Message, FAQ, ClusterRun, ClusterResult
from faq_api.serializers import (
    MessageSerializer,
    FAQSerializer,
    ClusterRunSerializer,
    ClusterResultSerializer,
)
from faq_api.utils.gpt import GPTFAQAnalyzer

logger = logging.getLogger(__name__)


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
        try:
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
        except Exception as e:
            logger.error("Error exporting CSV", exc_info=True)
            return Response({"error": str(e), "traceback": traceback.format_exc()}, status=500)


@api_view(["GET"])
def current_user_info(request):
    try:
        user = request.user
        return Response({
            "username": user.username,
            "is_admin": user.is_staff or user.is_superuser,
        })
    except Exception as e:
        logger.error("Error fetching user info", exc_info=True)
        return Response({"error": str(e), "traceback": traceback.format_exc()}, status=500)


@api_view(["POST"])
def trigger_pipeline(request):
    try:
        if not request.user.is_staff:
            return Response({"error": "Forbidden"}, status=403)
        return Response({"status": "Pipeline button not implemented for safety"})
    except Exception as e:
        logger.error("Error in trigger_pipeline", exc_info=True)
        return Response({"error": str(e), "traceback": traceback.format_exc()}, status=500)


@api_view(["GET"])
def dashboard_clusters_with_messages(request):
    try:
        cached = cache.get("cached_dashboard_clusters")
        if cached:
            return Response({"results": cached})

        # Fallback: fetch only 50 clusters + 5 messages
        clusters = ClusterResult.objects.select_related("matched_faq", "run")[:50]
        results = []
        for cluster in clusters:
            messages = Message.objects.filter(
                embedding__isnull=False,
                created_at__lte=cluster.created_at
            )[:5]

            results.append({
                "cluster": ClusterResultSerializer(cluster).data,
                "messages": MessageSerializer(messages, many=True).data
            })

        return Response({"results": results})
    except Exception as e:
        logger.error("Error in dashboard_clusters_with_messages", exc_info=True)
        return Response({"error": str(e), "traceback": traceback.format_exc()}, status=500)


@api_view(["GET"])
def trending_questions_leaderboard(request):
    try:
        leaderboard = cache.get("cached_trending_leaderboard")
        if leaderboard:
            return Response({"leaderboard": leaderboard})

        return Response({
            "leaderboard": [{
                "keyword": "Example",
                "count": 1,
                "previous_count": 0,
                "change": 1,
                "trend": [],
                "sentiment": {"positive": 1, "neutral": 0, "negative": 0, "score": 1},
                "messages": []
            }]
        })
    except Exception as e:
        logger.error("Error in trending_questions_leaderboard", exc_info=True)
        return Response({"error": str(e), "traceback": traceback.format_exc()}, status=500)


@api_view(["GET"])
def faq_performance_trends(request):
    try:
        cached = cache.get("cached_faq_performance")
        if cached:
            return Response({"faq_performance": cached})

        fallback_faq = FAQ.objects.first()
        if not fallback_faq:
            return Response({"faq_performance": []})

        trend = {
            "question": fallback_faq.question,
            "trend": [{
                "week": "N/A",
                "deflection_count": 0,
                "avg_resolution_score": None
            }]
        }

        return Response({"faq_performance": [trend]})
    except Exception as e:
        logger.error("Error in faq_performance_trends", exc_info=True)
        return Response({"error": str(e), "traceback": traceback.format_exc()}, status=500)


@api_view(["GET"])
def top_process_gaps(request):
    try:
        data = cache.get("cached_top_process_gaps")
        if data:
            return Response({"process_gaps": data})

        # Minimal fallback
        return Response({
            "process_gaps": [{
                "topic": "Login Problems",
                "examples": ["Can't log in", "Reset password"],
                "count": 3
            }]
        })
    except Exception as e:
        logger.error("Error in top_process_gaps", exc_info=True)
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
def cluster_results(request):
    try:
        clusters = cache.get("cached_cluster_results")
        cluster_map = cache.get("cached_cluster_map")

        if clusters is not None and cluster_map is not None:
            return Response({
                "clusters": clusters,
                "cluster_map": cluster_map
            })

        # Fallback to DB: fetch the first 10 clusters
        latest_run = ClusterRun.objects.order_by("-created_at").first()
        if not latest_run:
            return Response({"clusters": [], "cluster_map": []})

        fallback_clusters = ClusterResult.objects.filter(run=latest_run).select_related("matched_faq")[:50]
        data = ClusterResultSerializer(fallback_clusters, many=True).data

        return Response({
            "clusters": data,
            "cluster_map": latest_run.cluster_map or []
        })

    except Exception as e:
        logger.error("Error in cluster_results", exc_info=True)
        return Response({"error": str(e), "traceback": traceback.format_exc()}, status=500)

