#backend/faq_api/utils/clustering_pipeline.py
import logging
from django.conf import settings
from faq_api.models import Message, FAQ, ClusterResult, ClusterRun
from faq_api.utils.clustering import MessageClusterer
from faq_api.utils.gpt import GPTFAQAnalyzer
from faq_api.utils.sentiment import SentimentAnalyzer
from datetime import datetime

logger = logging.getLogger(__name__)

def run_clustering_and_save():
    logger.info("Starting clustering pipeline...")

    ClusterRun.objects.all().delete()
    run = ClusterRun.objects.create(notes="Automated weekly pipeline")
    logger.info(f"📌 Created new ClusterRun: {run.id}")

    messages = list(
        Message.objects.exclude(embedding=None).values("message_id", "text", "embedding", "created_at")
    )
    faqs = list(FAQ.objects.exclude(embedding=None).values("id", "question", "embedding"))

    logger.info(f"🗂️ Loaded {len(messages)} messages with embeddings")
    logger.info(f"📚 Loaded {len(faqs)} FAQs with embeddings")

    if not messages:
        logger.warning("❌ No messages to process. Exiting pipeline.")
        return

    if not faqs:
        logger.warning("❌ No FAQs available for matching. Exiting pipeline.")
        return

    # Pre-cache FAQs by question text
    faq_map = {faq["question"]: FAQ.objects.get(id=faq["id"]) for faq in faqs}

    clusterer = MessageClusterer(min_cluster_size=5)
    clustered, labels, vecs = clusterer.cluster_embeddings(messages)

    logger.info(f"🔍 Found {len(clustered)} clusters")
    noise = sum(1 for l in labels if l == -1)
    logger.info(f"🌪️ Noise points: {noise}")

    if not clustered:
        logger.warning("❌ No valid clusters formed. Exiting pipeline.")
        return

    centroids = clusterer.compute_centroids(clustered)
    logger.info(f"📍 Computed {len(centroids)} cluster centroids")

    try:
        matches = clusterer.match_faqs(centroids, faqs)
    except ValueError as e:
        logger.exception(f"❌ FAQ matching failed: {e}")
        return

    try:
        cluster_map = clusterer.get_cluster_map_coords(messages, labels, vecs)
        run.cluster_map = cluster_map
        run.save()
        logger.info("🗺️ Cluster map saved to run object.")
    except Exception as e:
        logger.warning(f"⚠️ Failed to generate cluster map: {e}")

    gpt = GPTFAQAnalyzer(openai_api_key=settings.OPENAI_API_KEY)
    sentiment_analyzer = SentimentAnalyzer()

    for cluster_id, items in clustered.items():
        try:
            top_message = items[0]["text"]
            created_at = items[0].get("created_at") or datetime.utcnow()

            matched = matches.get(cluster_id, {})
            matched_faq_question = matched.get("matched_faq", "")
            similarity = matched.get("similarity", 0.0)

            matched_faq = faq_map.get(matched_faq_question)
            if not matched_faq:
                logger.warning(f"⚠️ FAQ match failed for cluster {cluster_id} — question not found: {matched_faq_question}")
                continue 


            score_data = gpt.score_resolution(top_message, matched_faq_question)
            gpt_eval = f"{score_data.get('label')} — {score_data.get('reason')}"
            coverage_label = score_data.get("label", "Unknown")
            resolution_score = score_data.get("score", 0)
            resolution_reason = score_data.get("reason", "")

            faq_suggestion = None
            if coverage_label in ["Not", "Partially"]:
                faq_suggestion = gpt.suggest_faq(top_message)

            sentiment = sentiment_analyzer.analyze(top_message)
            summary = gpt.summarize_cluster(items)
            keywords = clusterer.extract_keywords([msg["text"] for msg in items])
            topic_label = gpt.label_topic(items)

            result = ClusterResult.objects.create(
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

            # Attach messages
            message_ids = [msg["message_id"] for msg in items]
            linked_messages = Message.objects.filter(message_id__in=message_ids)
            result.messages.set(linked_messages)
            logger.info(f"✅ Saved cluster result for cluster_id={cluster_id} ({len(items)} messages)")
        except Exception as e:
            logger.exception(f"❌ Failed processing cluster {cluster_id}: {e}")

    logger.info("Clustering pipeline processing completed successfully.")
