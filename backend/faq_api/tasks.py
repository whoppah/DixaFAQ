#backend/faq_api/tasks.py
import os
import json
import time
import datetime
import tempfile
from celery import shared_task, chain
from django.utils.timezone import make_aware, now
from django.core.cache import cache
from faq_api.models import Message, FAQ, ClusterResult, ClusterRun
from faq_api.utils.dixa_downloader import DixaDownloader
from faq_api.utils.elevio_downloader import ElevioFAQDownloader
from faq_api.utils.embedding import Tokenizer
from faq_api.utils.sentiment import SentimentAnalyzer
from faq_api.utils.gpt import GPTFAQAnalyzer
from faq_api.utils.faq_matcher import find_top_faqs, rerank_with_gpt
from faq_api.utils.preprocess import MessagePreprocessor
from faq_api.utils.clustering_pipeline import run_clustering_and_save
from faq_api.serializers import ClusterResultSerializer
from datetime import timedelta
import collections
import json
import re


def setup_google_credentials_from_env():
    raw = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not raw:
        raise Exception("Missing GOOGLE_CREDENTIALS_JSON")
    creds = json.loads(raw)
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    temp.write(json.dumps(creds).encode())
    temp.flush()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp.name
    return temp.name


@shared_task
def download_dixa_task():
    print("🚀 Starting task: download_dixa_task")
    start = time.time()

    dixa_token = os.getenv("DIXA_API_TOKEN")
    if not dixa_token:
        raise Exception("Missing DIXA_API_TOKEN")
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=7) #Downloading 7 days of Dixa messages

    dixa = DixaDownloader(
        api_token=dixa_token,
        start_date=start_date,
        end_date=end_date
    )
    messages, _ = dixa.download_all_dixa_data()
    inserted = 0

    for msg in messages:
        msg_id = msg.get("id")
        text = msg.get("text")
        if not msg_id or not text:
            continue
        created_at = make_aware(datetime.datetime.fromtimestamp(msg["created_at"] / 1000)) if msg.get("created_at") else None

        try:
            Message.objects.update_or_create(
                message_id=msg_id,
                defaults={
                    "csid": msg.get("csid"),
                    "created_at": created_at,
                    "author_name": msg.get("author_name"),
                    "author_email": msg.get("author_email"),
                    "direction": msg.get("direction"),
                    "text": text,
                    "from_phone_number": msg.get("from_phone_number"),
                    "to_phone_number": msg.get("to_phone_number"),
                    "duration": msg.get("duration"),
                    "to": msg.get("to"),
                    "from_field": msg.get("from"),
                    "cc": msg.get("cc"),
                    "bcc": msg.get("bcc"),
                    "is_automated_message": msg.get("is_automated_message"),
                    "voicemail_url": msg.get("voicemail_url"),
                    "recording_url": msg.get("recording_url"),
                    "attached_files": msg.get("attached_files"),
                    "chat_input_question": msg.get("chat_input_question"),
                    "chat_input_answer": msg.get("chat_input_answer"),
                    "chat_menu_text": msg.get("chat_menu_text"),
                    "form_submission": msg.get("formSubmission"),
                }
            )
            inserted += 1
        except Exception as e:
            print(f"❌ Failed to insert message {msg_id}: {e}")

    duration = round(time.time() - start, 2)
    print(f"✅ Finished task: download_dixa_task in {duration}s | Inserted: {inserted}")
    return {"message_count": inserted}


@shared_task
def download_elevio_task(prev):
    print("🚀 Starting task: download_elevio_task")
    start = time.time()

    elevio_key = os.getenv("ELEVIO_API_KEY")
    elevio_jwt = os.getenv("ELEVIO_JWT")
    jina_key   = os.getenv("JINA_API_KEY")
    if not elevio_key or not elevio_jwt or not jina_key:
        raise Exception("Missing Elevio or JINA credentials")

    elevio = ElevioFAQDownloader(api_key=elevio_key, jwt=elevio_jwt)
    faq_items = elevio.download_all_faqs()

    tokenizer = Tokenizer(
        messages_path=None,     
        jina_api_key=jina_key,  
        model="jina-embeddings-v4",
        task="text-matching",
        max_tokens=256,
        output_path=None
    )

    tokenizer.embed_and_store_faqs(faq_items)
    duration = round(time.time() - start, 2)
    print(f"✅ Finished task: download_elevio_task in {duration}s | Count: {len(faq_items)}")
    return {**prev, "faq_count": len(faq_items)}

@shared_task
def preprocess_messages_task(prev):
    print("🚀 Starting task: preprocess_messages_task")
    start = time.time()

    preprocessor = MessagePreprocessor()
    messages = Message.objects.all()
    cleaned = 0

    for msg in messages:
        if not msg.text:
            continue
        cleaned_text = preprocessor.anonymize_text(msg.text)
        if cleaned_text != msg.text:
            msg.text = cleaned_text
            msg.save(update_fields=["text"])
            cleaned += 1

    duration = round(time.time() - start, 2)
    print(f"✅ Finished task: preprocess_messages_task in {duration}s | Cleaned: {cleaned}")
    return {**prev, "preprocessed": cleaned}

@shared_task
def embed_messages_task(prev):
    print("🚀 Starting task: embed_messages_task")
    start = time.time()

    jina_key = os.getenv("JINA_API_KEY")
    if not jina_key:
        raise Exception("Missing JINA_API_KEY")

    tokenizer = Tokenizer(
        messages_path=None,     
        jina_api_key=jina_key, 
        model="jina-embeddings-v4",
        task="text-matching",
        max_tokens=256,
        output_path=None
    )
    count = Message.objects.filter(embedding__isnull=True).count()
    print(f"🔍 Messages to embed: {count}")
    embeddings = tokenizer.embed_all()

    duration = round(time.time() - start, 2)
    print(f"✅ Finished task: embed_messages_task in {duration}s | Count: {len(embeddings)}")
    return {**prev, "embedded_count": len(embeddings)}

@shared_task
def match_messages_task(prev, force=False):
    print("🚀 Starting task: match_messages_task")
    start = time.time()
    
    kimi_key = os.getenv("KIMI_API_KEY")
    gpt = GPTFAQAnalyzer(kimi_api_key=kimi_key)
    sentiment_analyzer = SentimentAnalyzer(api_key=kimi_key)
    saved = 0
    
    if force:
        messages = Message.objects.filter(embedding__isnull=False)
    else:
        messages = Message.objects.filter(embedding__isnull=False, gpt_score__isnull=True)

    for msg in messages:
        try:
            sentiment = sentiment_analyzer.analyze(msg.text)
        except Exception as e:
            print(f"⚠️ Sentiment failed for {msg.message_id}: {e}")
            sentiment = None

        try:
            top_faqs = find_top_faqs(msg.embedding, top_n=5)
            faq_id = rerank_with_gpt(msg.text, top_faqs, kimi_api_key=kimi_key)
            matched_faq = FAQ.objects.filter(id=faq_id).first()

            if matched_faq:
                gpt_eval = gpt.score_resolution(msg.text, matched_faq.answer)
            else:
                raise Exception(f"FAQ not found for id={faq_id}")

        except Exception as e:
            print(f"⚠️ KIMI match failed for {msg.message_id}: {e}")
            matched_faq = None
            gpt_eval = {"label": "unknown", "score": 0, "reason": "N/A"}

        msg.sentiment = sentiment
        msg.gpt_label = gpt_eval["label"]
        msg.gpt_score = gpt_eval["score"]
        msg.gpt_reason = gpt_eval["reason"]
        msg.matched_faq = matched_faq
        msg.save(update_fields=[
            "sentiment", "gpt_label", "gpt_score", "gpt_reason", "matched_faq"
        ])
        saved += 1

    duration = round(time.time() - start, 2)
    print(f"✅ Finished task: match_messages_task in {duration}s | Matched: {saved}")
    return {**prev, "matched_messages": saved}



@shared_task
def upload_artifacts_task(prev):
    print("🚀 Starting task: upload_artifacts_task")
    setup_google_credentials_from_env()
    bucket = os.getenv("GCS_BUCKET_NAME")
    if not bucket:
        raise Exception("Missing GCS_BUCKET_NAME")

    print("✅ Skipping actual upload (not implemented)")
    return {**prev, "uploaded": "skipped"}


@shared_task
def cluster_and_summarize_task(prev):
    print("🚀 Starting task: cluster_and_summarize_task")
    start = time.time()
    
    clusters_created = run_clustering_and_save() or 0

    duration = round(time.time() - start, 2)
    print(f"✅ Finished task: cluster_and_summarize_task in {duration}s | Clusters: {clusters_created}")
    return {
        "status": "pipeline_complete",
        "clusters_created": clusters_created,
        **prev
    }


@shared_task
def cache_cluster_results():
    latest_run = ClusterRun.objects.order_by("-created_at").first()
    if not latest_run:
        return {"error": "No ClusterRun found"}

    clusters = ClusterResult.objects.filter(run=latest_run).select_related("matched_faq", "run")
    data = ClusterResultSerializer(clusters, many=True).data
    cache.set("cached_cluster_results", data, timeout=3600)
    cache.set("cached_cluster_map", latest_run.cluster_map or [], timeout=3600)
    return {"cached_clusters": len(data)}


@shared_task
def cache_dashboard_clusters_with_messages():
    clusters = ClusterResult.objects.select_related("matched_faq", "run")[:20]
    results = []

    for cluster in clusters:
        messages = Message.objects.filter(
            embedding__isnull=False,
            created_at__lte=cluster.created_at
        )[:10]
        results.append({
            "cluster": ClusterResultSerializer(cluster).data,
            "messages": [m.text for m in messages]
        })

    cache.set("cached_dashboard_clusters", results, timeout=3600)
    return {"cached_clusters_with_messages": len(results)}


@shared_task
def cache_trending_questions_leaderboard():
    gpt = GPTFAQAnalyzer(kimi_api_key=os.getenv("KIMI_API_KEY"))
    today = now().date()
    start_date = today - timedelta(days=14)

    messages = Message.objects.filter(created_at__date__gte=start_date, embedding__isnull=False)

    messages_by_date = collections.defaultdict(list)
    for msg in messages:
        messages_by_date[msg.created_at.date()].append(msg)

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

    last_week = today - timedelta(days=7)
    leaderboard = []

    for kw, counts in keyword_trends.items():
        this_week = sum(c for d, c in counts.items() if d >= last_week)
        prev_week = sum(c for d, c in counts.items() if start_date <= d < last_week)
        trend = [{"date": str(d), "value": counts[d]} for d in sorted(counts)]

        sentiment_counts = sentiment_by_keyword[kw]
        sentiment_score = sentiment_counts["Positive"] - sentiment_counts["Negative"]

        leaderboard.append({
            "keyword": kw,
            "count": this_week,
            "previous_count": prev_week,
            "change": this_week - prev_week,
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
    cache.set("cached_trending_leaderboard", leaderboard, timeout=3600)
    return {"cached_keywords": len(leaderboard)}


@shared_task
def cache_faq_performance_trends():
    today = now().date()
    weeks_back = 6
    start_date = today - timedelta(weeks=weeks_back * 7)

    faqs = FAQ.objects.all()
    faq_data = {faq.id: {"question": faq.question, "trend": []} for faq in faqs}

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
            if msg.matched_faq_id:
                total_by_faq[msg.matched_faq_id] += 1
                if msg.gpt_score:
                    scores_by_faq[msg.matched_faq_id].append(msg.gpt_score)

        for faq_id in faq_data.keys():
            count = total_by_faq.get(faq_id, 0)
            scores = scores_by_faq.get(faq_id, [])
            avg_score = round(sum(scores) / len(scores), 2) if scores else None

            faq_data[faq_id]["trend"].append({
                "week": f"{week_start.isoformat()} to {week_end.isoformat()}",
                "deflection_count": count,
                "avg_resolution_score": avg_score
            })

    sorted_faqs = sorted(faq_data.values(), key=lambda x: sum(d["deflection_count"] for d in x["trend"]), reverse=True)
    cache.set("cached_faq_performance", sorted_faqs, timeout=3600)
    return {"cached_faqs": len(sorted_faqs)}


@shared_task
def cache_top_process_gaps():
    gpt = GPTFAQAnalyzer(kimi_api_key=os.getenv("KIMI_API_KEY"))
    clusters = ClusterResult.objects.filter(
        coverage="Not",
        faq_suggestion__isnull=False
    )[:100]

    questions = [
        c.faq_suggestion.get("question")
        for c in clusters
        if isinstance(c.faq_suggestion, dict) and c.faq_suggestion.get("question")
    ]
    questions = [q[:300] for q in questions[:50]]

    prompt = f"""
You are a support documentation assistant.

Given the following user questions, group them into 5–10 top-level topics and list common phrasings.

Return JSON like:
[
  {{
    "topic": "Account Access",
    "examples": ["How do I reset my password?", "Can't log in"],
    "count": 8
  }},
  ...
]

Questions:
{json.dumps(questions)}
"""

    response = gpt.client.chat.completions.create(
        model=gpt.model,
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content.strip()
    result = json.loads(content)
    cache.set("cached_top_process_gaps", result, timeout=3600)
    return {"cached_topics": len(result)}
    

@shared_task(name="faq_api.tasks.start_pipeline")
def start_pipeline():
    print("🚀 Starting pipeline: start_pipeline")
    return chain(
        download_dixa_task.s(),
        download_elevio_task.s(),
        preprocess_messages_task.s(),
        embed_messages_task.s(),
        match_messages_task.s(),
        cluster_and_summarize_task.s(),
        cache_cluster_results.s(),
        cache_dashboard_clusters_with_messages.s(),
        cache_trending_questions_leaderboard.s(),
        cache_faq_performance_trends.s(),
        cache_top_process_gaps.s()
    ).apply_async()
