#backend/faq_api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from faq_api.models import Message, FAQ
from faq_api.serializers import ClusterResultSerializer
from faq_api.utils.clustering import MessageClusterer
from faq_api.utils.gpt import GPTFAQAnalyzer
from django.conf import settings
from faq_api.utils.sentiment import SentimentAnalyzer
from faq_api.utils.clustering import extract_keywords, get_cluster_map_coords


@api_view(['GET'])
def cluster_results(request):
    # Load embeddings from DB
    messages = list(
        Message.objects.exclude(embedding=None).values(
            "message_id", "text", "embedding", "created_at"
        )
    )
    faqs = list(FAQ.objects.exclude(embedding=None).values("question", "embedding"))

    # Cluster messages
    clusterer = MessageClusterer(min_cluster_size=5)
    clustered, labels, vecs = clusterer.cluster_embeddings(messages)
    centroids = clusterer.compute_centroids(clustered)
    matches = clusterer.match_faqs(centroids, faqs)

    # GPT and sentiment analysis
    gpt = GPTFAQAnalyzer(openai_api_key=settings.OPENAI_API_KEY)
    sentiment_analyzer = SentimentAnalyzer()

    # Cluster map
    cluster_map = get_cluster_map_coords(messages, labels, vecs)

    result_data = []
    for cluster_id, items in clustered.items():
        top_message = items[0]["text"]
        created_at = items[0].get("created_at")

        matched = matches.get(cluster_id, {})
        matched_faq = matched.get("matched_faq", "N/A")
        similarity = matched.get("similarity", 0.0)

        # GPT scoring
        score_data = gpt.score_resolution(top_message, matched_faq)
        gpt_eval = f"{score_data.get('label')} — {score_data.get('reason')}"
        coverage_label = score_data.get("label", "Unknown")
        resolution_score = score_data.get("score", 0)
        resolution_reason = score_data.get("reason", "")

        # Suggest new FAQ if needed
        faq_suggestion = None
        if coverage_label in ["Not", "Partially"]:
            faq_suggestion = gpt.suggest_faq(top_message)

        sentiment = sentiment_analyzer.analyze(top_message)
        summary = gpt.summarize_cluster(items)
        keywords = extract_keywords([msg["text"] for msg in items])

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
        })

    serialized = ClusterResultSerializer(result_data, many=True)
    return Response({
        "clusters": serialized.data,
        "clusters_map": cluster_map,
    })
