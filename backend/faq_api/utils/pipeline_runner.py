#backend/faq_api/utils/pipeline_runner.py
from django.conf import settings
from faq_api.models import Message, FAQ, ClusterResult, ClusterRun
from faq_api.utils.clustering import MessageClusterer
from faq_api.utils.gpt import GPTFAQAnalyzer
from faq_api.utils.sentiment import SentimentAnalyzer
from datetime import datetime

def process_clusters_and_save():
    
    ClusterRun.objects.all().delete()
    run = ClusterRun.objects.create(notes="Automated weekly pipeline")
    messages = list(
        Message.objects.exclude(embedding=None).values("message_id", "text", "embedding", "created_at")
    )
    faqs = list(FAQ.objects.exclude(embedding=None).values("question", "embedding"))

    # Cluster messages
    clusterer = MessageClusterer(min_cluster_size=5)
    clustered, labels, vecs = clusterer.cluster_embeddings(messages)
    centroids = clusterer.compute_centroids(clustered)
    matches = clusterer.match_faqs(centroids, faqs)

    # Generate and store cluster map
    cluster_map = clusterer.get_cluster_map_coords(messages, labels, vecs)
    run.cluster_map = cluster_map
    run.save()

    # Initialize analyzers
    gpt = GPTFAQAnalyzer(openai_api_key=settings.OPENAI_API_KEY)
    sentiment_analyzer = SentimentAnalyzer()

    # Process each cluster
    for cluster_id, items in clustered.items():
        top_message = items[0]["text"]
        created_at = items[0].get("created_at") or datetime.utcnow()

        matched = matches.get(cluster_id, {})
        matched_faq = matched.get("matched_faq", "N/A")
        similarity = matched.get("similarity", 0.0)

        # GPT evaluation
        score_data = gpt.score_resolution(top_message, matched_faq)
        gpt_eval = f"{score_data.get('label')} — {score_data.get('reason')}"
        coverage_label = score_data.get("label", "Unknown")
        resolution_score = score_data.get("score", 0)
        resolution_reason = score_data.get("reason", "")

        # Suggest FAQ if needed
        faq_suggestion = None
        if coverage_label in ["Not", "Partially"]:
            faq_suggestion = gpt.suggest_faq(top_message)

        # Sentiment, summary, and keywords
        sentiment = sentiment_analyzer.analyze(top_message)
        summary = gpt.summarize_cluster(items)
        keywords = clusterer.extract_keywords([msg["text"] for msg in items])
        topic_label = gpt.label_topic(items)

        # Save result
        ClusterResult.objects.create(
            run=run,
            cluster_id=cluster_id,
            message_count=len(items),
            top_message=top_message,
            matched_faq=matched_faq,
            similarity=similarity,
            gpt_evaluation=gpt_eval,
            sentiment=sentiment,
            keywords=keywords,
            summary=summary,
            created_at=created_at,
            coverage=coverage_label,
            resolution_score=resolution_score,
            resolution_reason=resolution_reason,
            faq_suggestion=faq_suggestion,
            topic_label=topic_label
        )
