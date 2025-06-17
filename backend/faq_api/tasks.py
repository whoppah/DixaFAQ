#backend/faq_api/tasks.py
import os
import json
import time
import datetime
import tempfile
from celery import shared_task, chain
from django.utils.timezone import make_aware
from faq_api.models import Message, FAQ
from faq_api.utils.dixa_downloader import DixaDownloader
from faq_api.utils.elevio_downloader import ElevioFAQDownloader
from faq_api.utils.embedding import Tokenizer
from faq_api.utils.sentiment import SentimentAnalyzer
from faq_api.utils.gpt import GPTFAQAnalyzer
from faq_api.utils.faq_matcher import find_top_faqs, rerank_with_gpt
from faq_api.utils.preprocess import MessagePreprocessor
from faq_api.utils.clustering_pipeline import run_clustering_and_save

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

    dixa = DixaDownloader(
        api_token=dixa_token,
        start_date=datetime.datetime(2025, 5, 1),
        end_date=datetime.datetime.now()
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
    openai_key = os.getenv("OPENAI_API_KEY")
    if not elevio_key or not elevio_jwt or not openai_key:
        raise Exception("Missing Elevio or OpenAI credentials")

    elevio = ElevioFAQDownloader(api_key=elevio_key, jwt=elevio_jwt)
    faq_items = elevio.download_all_faqs()
    tokenizer = Tokenizer(messages_path=None, openai_api_key=openai_key)
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

    openai_key = os.getenv("OPENAI_API_KEY")
    tokenizer = Tokenizer(messages_path=None, openai_api_key=openai_key)

    count = Message.objects.filter(embedding__isnull=True).count()
    print(f"🔍 Messages to embed: {count}")

    embeddings = tokenizer.embed_all()

    duration = round(time.time() - start, 2)
    print(f"✅ Finished task: embed_messages_task in {duration}s | Count: {len(embeddings)}")
    return {**prev, "embedded_count": len(embeddings)}



@shared_task
def match_messages_task(prev):
    print("🚀 Starting task: match_messages_task")
    start = time.time()

    openai_key = os.getenv("OPENAI_API_KEY")
    gpt = GPTFAQAnalyzer(openai_api_key=openai_key)
    sentiment_analyzer = SentimentAnalyzer(api_key=openai_key)

    saved = 0
    messages = Message.objects.filter(embedding__isnull=False)

    for msg in messages:
        try:
            sentiment = sentiment_analyzer.analyze(msg.text)
        except Exception as e:
            print(f"⚠️ Sentiment failed for {msg.message_id}: {e}")
            sentiment = None

        try:
            top_faqs = find_top_faqs(msg.embedding, top_n=5)
            matched_faq = rerank_with_gpt(msg.text, top_faqs, openai_api_key=openai_key)
            gpt_eval = gpt.score_resolution(msg.text, matched_faq.answer)
        except Exception as e:
            print(f"⚠️ GPT match failed for {msg.message_id}: {e}")
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

    clusters_created = run_clustering_and_save()

    duration = round(time.time() - start, 2)
    print(f"✅ Finished task: cluster_and_summarize_task in {duration}s | Clusters: {clusters_created}")
    return {
        "status": "pipeline_complete",
        "clusters_created": clusters_created,
        **prev
    }


@shared_task(name="faq_api.tasks.start_pipeline")
def start_pipeline():
    print("🚀 Starting pipeline: start_pipeline")
    return chain(
        download_dixa_task.s(),
        download_elevio_task.s(),
        preprocess_messages_task.s(),
        embed_messages_task.s(),
        match_messages_task.s(),
        cluster_and_summarize_task.s()
    ).apply_async()
