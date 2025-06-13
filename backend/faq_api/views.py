#backend/faq_api/views.py
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, filters
from django.conf import settings
from django.http import HttpResponse
from django.db.models import Q
from django.utils.timezone import now
from datetime import timedelta
import csv
import collections
import re

from faq_api.models import Message, FAQ, ClusterRun, ClusterResult
from faq_api.serializers import (
    MessageSerializer,
    FAQSerializer,
    ClusterRunSerializer,
    ClusterResultSerializer,
)
from faq_api.tasks import async_download_and_process
from faq_api.utils.gpt import GPTFAQAnalyzer


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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def trending_questions_leaderboard(request):
    gpt = GPTFAQAnalyzer(openai_api_key=settings.OPENAI_API_KEY)
    today = now().date()
    start_date = today - timedelta(days=14)

    # Fetch messages from the past 2 weeks
    messages = Message.objects.filter(created_at__date__gte=start_date, embedding__isnull=False)

    # Bucket messages by date
    messages_by_date = collections.defaultdict(list)
    for msg in messages:
        date = msg.created_at.date()
        messages_by_date[date].append(msg)

    # Extract keywords per day
    keyword_trends = collections.defaultdict(lambda: collections.Counter())
    sentiment_by_keyword = collections.defaultdict(lambda: collections.Counter())
    keyword_message_map = collections.defaultdict(list)

    for date, msgs in messages_by_date.items():
        try:
            keywords = gpt.extract_gpt_keywords(msgs)
            for kw in keywords:
                keyword_trends[kw][date] += 1
                for msg in msgs:
                    if re.search(rf"\b{re.escape(kw)}\b", msg.text, re.IGNORECASE):
                        keyword_message_map[kw].append(msg.text)
                        if msg.sentiment:
                            sentiment_by_keyword[kw][msg.sentiment] += 1
        except Exception:
            continue

    # Build leaderboard
    today = now().date()
    last_week = today - timedelta(days=7)

    leaderboard = []
    for kw, counts in keyword_trends.items():
        this_week_count = sum(cnt for d, cnt in counts.items() if d >= last_week)
        prev_week_count = sum(cnt for d, cnt in counts.items() if start_date <= d < last_week)

        trend = [{"date": str(d), "value": counts[d]} for d in sorted(counts.keys())]
        sentiment_counts = sentiment_by_keyword[kw]
        sentiment_score = sentiment_counts["Positive"] - sentiment_counts["Negative"]

        leaderboard.append({
            "keyword": kw,
            "count": this_week_count,
            "previous_count": prev_week_count,
            "change": this_week_count - prev_week_count,
            "trend": trend,
            "sentiment": {
                "positive": sentiment_counts["Positive"],
                "neutral": sentiment_counts["Neutral"],
                "negative": sentiment_counts["Negative"],
                "score": sentiment_score
            },
            "messages": keyword_message_map[kw][:10]   
        })

    leaderboard = sorted(leaderboard, key=lambda x: x["count"], reverse=True)[:20]
    return Response({"leaderboard": leaderboard})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def faq_performance_trends(request):
    """
    Returns weekly resolution score and deflection metrics for each FAQ over time.
    """
    today = now().date()
    weeks_back = 6
    start_date = today - timedelta(weeks=weeks_back * 7)

    faqs = FAQ.objects.all()
    faq_data = {faq.id: {"question": faq.question, "trend": []} for faq in faqs}

    # Iterate weekly
    for i in range(weeks_back):
        week_start = today - timedelta(days=(i + 1) * 7)
        week_end = today - timedelta(days=i * 7)

        matched = Message.objects.filter(
            matched_faq__isnull=False,
            created_at__date__gte=week_start,
            created_at__date__lt=week_end
        )

        scores_by_faq = collections.defaultdict(list)
        total_by_faq = collections.Counter()

        for msg in matched:
            faq_id = msg.matched_faq_id
            if faq_id:
                total_by_faq[faq_id] += 1
                if msg.gpt_score:
                    scores_by_faq[faq_id].append(msg.gpt_score)

        for faq_id in faq_data.keys():
            count = total_by_faq.get(faq_id, 0)
            avg_score = round(sum(scores_by_faq[faq_id]) / len(scores_by_faq[faq_id]), 2) if scores_by_faq[faq_id] else None

            faq_data[faq_id]["trend"].append({
                "week": f"{week_start.isoformat()} to {week_end.isoformat()}",
                "deflection_count": count,
                "avg_resolution_score": avg_score
            })

    # Sort by most recent deflection count
    sorted_faqs = sorted(faq_data.values(), key=lambda x: sum(d["deflection_count"] for d in x["trend"]), reverse=True)

    return Response({"faq_performance": sorted_faqs})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def top_process_gaps(request):
    gpt = GPTFAQAnalyzer(openai_api_key=settings.OPENAI_API_KEY)

    # Filter clusters where FAQ was NOT covered and a suggestion exists
    clusters = ClusterResult.objects.filter(
        coverage="Not",
        faq_suggestion__isnull=False
    ).select_related("matched_faq")[:100]  # limit for performance

    # Prepare raw suggestions
    suggestion_texts = [c.faq_suggestion["question"] for c in clusters if c.faq_suggestion.get("question")]

    # Ask GPT to group them into thematic labels
    prompt = f"""
You are a support documentation assistant.

Given the following user questions, group them into 5–10 top-level topics and list common phrasings.

Return JSON like:
[
  {{
    "topic": "Account Access",
    "examples": ["How do I reset my password?", "Can't log in", ...],
    "count": 8
  }},
  ...
]

Questions:
{json.dumps(suggestion_texts[:50])}
"""

    try:
        response = openai.ChatCompletion.create(
            model=gpt.model,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response['choices'][0]['message']['content']
        result = json.loads(content)
        return Response({"process_gaps": result})
    except Exception as e:
        return Response({"error": "GPT failed", "details": str(e)}, status=500)



