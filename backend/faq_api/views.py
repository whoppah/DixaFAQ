#backend/faq_api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from faq_api.models import Message, FAQ
from faq_api.serializers import ClusterResultSerializer
from faq_api.utils.clustering import MessageClusterer
from faq_api.utils.gpt import GPTFAQAnalyzer
from django.conf import settings
from faq_api.utils.sentiment import SentimentAnalyzer
from faq_api.utils.clustering import extract_keywords, get_cluster_map_coords
from faq_api.tasks import async_download_and_process
from django.contrib.auth.decorators import login_required


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_info(request):
    user = request.user
    return Response({
        "username": user.username,
        "is_admin": user.is_staff or user.is_superuser,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cluster_results(request):
    messages = list(
        Message.objects.exclude(embedding=None).values(
            "message_id", "text", "embedding", "created_at"
        )
    )
    faqs = list(FAQ.objects.exclude(embedding=None).values("question", "embedding"))

    clusterer = MessageClusterer(min_cluster_size=5)
    clustered, labels, vecs = clusterer.cluster_embeddings(messages)
    centroids = clusterer.compute_centroids(clustered)
    matches = clusterer.match_faqs(centroids, faqs)

    gpt = GPTFAQAnalyzer(openai_api_key=settings.OPENAI_API_KEY)
    sentiment_analyzer = SentimentAnalyzer()
    cluster_map = clusterer.get_cluster_map_coords(messages, labels, vecs)

    result_data = []
    for cluster_id, items in clustered.items():
        top_message = items[0]["text"]
        created_at = items[0].get("created_at")

        matched = matches.get(cluster_id, {})
        matched_faq = matched.get("matched_faq", "N/A")
        similarity = matched.get("similarity", 0.0)

        score_data = gpt.score_resolution(top_message, matched_faq)
        gpt_eval = f"{score_data.get('label')} — {score_data.get('reason')}"
        coverage_label = score_data.get("label", "Unknown")
        resolution_score = score_data.get("score", 0)
        resolution_reason = score_data.get("reason", "")

        faq_suggestion = None
        if coverage_label in ["Not", "Partially"]:
            faq_suggestion = gpt.suggest_faq(top_message)

        sentiment = sentiment_analyzer.analyze(top_message)
        summary = gpt.summarize_cluster(items)
        keywords = extract_keywords([msg["text"] for msg in items])
        topic_label = gpt.label_topic(items)

        result_data.append({
            "cluster_id": cluster_id,
            "message_count": len(items),
            "top_message": top_message,
            "matched_faq": matched_faq,
            "similarity": round(similarity, 4),
            "gpt_evaluation": gpt_eval,
            "sentiment": sentiment,
            "keywords": keywords,
            "summary": summary,
            "messages": [msg["text"] for msg in items],
            "coverage": coverage_label,
            "resolution_score": resolution_score,
            "resolution_reason": resolution_reason,
            "faq_suggestion": faq_suggestion,
            "created_at": created_at.isoformat() if created_at else None,
            "topic_label": topic_label,
        })

    serialized = ClusterResultSerializer(result_data, many=True)
    return Response({
        "clusters": serialized.data,
        "cluster_map": cluster_map,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def trigger_pipeline(request):
    if not request.user.is_staff:
        return Response({"error": "Forbidden"}, status=403)

    async_download_and_process.delay()
    return Response({"status": "Pipeline started"})
