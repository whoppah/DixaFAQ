#backend/faq_api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from faq_api.models import Message, FAQ
from faq_api.serializers import ClusterResultSerializer
from faq_api.utils.clustering import MessageClusterer
from faq_api.utils.gpt import GPTFAQAnalyzer
from django.conf import settings
from faq_api.utils.sentiment import SentimentAnalyzer

@api_view(['GET'])
def cluster_results(request):
    # Load embeddings from DB
    messages = list(Message.objects.exclude(embedding=None).values("message_id", "text", "embedding"))
    faqs = list(FAQ.objects.exclude(embedding=None).values("question", "embedding"))

    # Cluster messages
    clusterer = MessageClusterer(min_cluster_size=5)
    clustered = clusterer.cluster_embeddings(messages)
    centroids = clusterer.compute_centroids(clustered)
    matches = clusterer.match_faqs(centroids, faqs)

    # GPT evaluation and sentiment analysis
    gpt = GPTFAQAnalyzer(openai_api_key=settings.OPENAI_API_KEY)
    sentiment_analyzer = SentimentAnalyzer()

    result_data = []
    for cluster_id, items in clustered.items():
        top_message = items[0]["text"]
        matched = matches.get(cluster_id, {})
        matched_faq = matched.get("matched_faq", "N/A")
        similarity = matched.get("similarity", 0.0)
        gpt_eval = gpt.evaluate_coverage(top_message, matched_faq)
        entiment = sentiment_analyzer.analyze(top_message)
        summary = gpt.summarize_cluster(items)
        
        result_data.append({
            "cluster_id": cluster_id,
            "message_count": len(items),
            "top_message": top_message,
            "matched_faq": matched_faq,
            "similarity": round(similarity, 4),
            "gpt_evaluation": gpt_eval,
            "sentiment": sentiment,
            "summary": summary
        })

    serialized = ClusterResultSerializer(result_data, many=True)
    return Response(serialized.data)
