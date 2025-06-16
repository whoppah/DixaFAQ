#backend/faq_api/tasks.py
import os
import json
import datetime
import tempfile
from celery import shared_task, chain
from google.cloud import storage

from faq_api.utils.dixa_downloader import DixaDownloader
from faq_api.utils.elevio_downloader import ElevioFAQDownloader
from faq_api.utils.embedding import Tokenizer
from faq_api.utils.sentiment import SentimentAnalyzer
from faq_api.utils.preprocess import MessagePreprocessor
from faq_api.utils.gpt import GPTFAQAnalyzer
from faq_api.utils.faq_matcher import find_top_faqs, rerank_with_gpt
from faq_api.utils.pipeline_runner import process_clusters_and_save
from faq_api.models import Message, FAQ


def setup_google_credentials_from_env():
    print("🔐 Setting up Google credentials...")
    raw = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not raw:
        raise Exception("Missing GOOGLE_CREDENTIALS_JSON env variable")
    creds = json.loads(raw)
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    temp.write(json.dumps(creds).encode())
    temp.flush()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp.name
    return temp.name


def upload_to_gcs(bucket_name, source_file_path, destination_blob_name):
    print(f"☁️ Uploading {source_file_path} to GCS...")
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_path)
        print(f"✅ Uploaded to gs://{bucket_name}/{destination_blob_name}")
        return destination_blob_name
    except Exception as e:
        print(f"❌ Failed to upload {source_file_path} to GCS: {e}")
        return f"FAILED: {destination_blob_name}"


@shared_task
def download_dixa_task():
    print("🔽 Task: download_dixa_task")
    try:
        dixa_token = os.getenv("DIXA_API_TOKEN")
        if not dixa_token:
            raise Exception("❌ Missing DIXA_API_TOKEN environment variable")

        print("ℹ️ Starting Dixa download process...")
        print(f"📂 Current working directory: {os.getcwd()}")

        # Initialize downloader
        dixa = DixaDownloader(
            api_token=dixa_token,
            start_date=datetime.datetime(2025, 5, 1),
            end_date=datetime.datetime.now()
        )

        # Download all data
        messages, _ = dixa.download_all_dixa_data()
        print(f"📥 Downloaded total messages: {len(messages)}")

        # Save messages to temp file
        dixa_path = "/tmp/dixa_messages.json"
        with open(dixa_path, "w", encoding="utf-8") as f:
            json.dump({"messages": messages}, f, indent=2)

        print(f"✅ Dixa messages saved to: {dixa_path}")
        print("✅ download_dixa_task completed successfully.")
        return {"dixa_path": dixa_path, "message_count": len(messages)}

    except Exception as e:
        print(f"❌ Exception in download_dixa_task: {e}")
        import traceback
        traceback.print_exc()
        raise



@shared_task
def download_elevio_task(prev):
    print("🔽 Task: download_elevio_task")
    try:
        elevio_key = os.getenv("ELEVIO_API_KEY")
        elevio_jwt = os.getenv("ELEVIO_JWT")
        openai_key = os.getenv("OPENAI_API_KEY")
        if not elevio_key or not elevio_jwt or not openai_key:
            raise Exception("Missing Elevio or OpenAI credentials")

        elevio = ElevioFAQDownloader(api_key=elevio_key, jwt=elevio_jwt)
        faq_items = elevio.download_all_faqs()
        print(f"📦 Fetched {len(faq_items)} FAQs")

        tokenizer = Tokenizer(messages_path=None, openai_api_key=openai_key)
        tokenizer.embed_and_store_faqs(faq_items)

        return {**prev, "faq_count": len(faq_items)}
    except Exception as e:
        print(f"❌ Error in download_elevio_task: {e}")
        raise


@shared_task
def preprocess_messages_task(prev):
    print("🔽 Task: preprocess_messages_task")
    try:
        cleaned_path = "/tmp/cleaned.json"
        processor = MessagePreprocessor()
        processor.process_file(prev["dixa_path"], cleaned_path)
        print(f"✅ Cleaned messages saved to: {cleaned_path}")
        return {**prev, "cleaned_path": cleaned_path}
    except Exception as e:
        print(f"❌ Error in preprocess_messages_task: {e}")
        raise


@shared_task
def embed_messages_task(prev):
    print("🔽 Task: embed_messages_task")
    try:
        openai_key = os.getenv("OPENAI_API_KEY")
        embeddings_path = "/tmp/embeddings.json"
        tokenizer = Tokenizer(
            messages_path=prev["cleaned_path"],
            openai_api_key=openai_key,
            output_path=embeddings_path
        )
        embeddings = tokenizer.embed_all()
        if not embeddings:
            raise Exception("❌ No embeddings generated. Aborting.")

        print(f"✅ Embeddings saved to: {embeddings_path}")
        return {**prev, "embeddings_path": embeddings_path, "embeddings": embeddings}
    except Exception as e:
        print(f"❌ Error in embed_messages_task: {e}")
        raise


@shared_task
def match_messages_task(prev):
    print("🔽 Task: match_messages_task")
    try:
        openai_key = os.getenv("OPENAI_API_KEY")
        gpt = GPTFAQAnalyzer(openai_api_key=openai_key)
        sentiment_analyzer = SentimentAnalyzer(api_key=openai_key)

        with open(prev["dixa_path"], "r", encoding="utf-8") as f:
            original = json.load(f).get("messages", [])

        saved = 0
        for item in prev["embeddings"]:
            msg_id, text, embedding = item["id"], item["text"], item["embedding"]
            if not msg_id or not text or not embedding:
                continue

            orig = next((m for m in original if m.get("id") == msg_id), {})
            created_at = datetime.datetime.fromtimestamp(orig.get("created_at", 0) / 1000) if orig.get("created_at") else None

            message_obj, _ = Message.objects.update_or_create(
                message_id=msg_id,
                defaults={
                    "text": text,
                    "embedding": embedding,
                    "csid": orig.get("csid"),
                    "created_at": created_at,
                    "author_name": orig.get("author_name"),
                    "author_email": orig.get("author_email"),
                    "channel": orig.get("initial_channel"),
                    "direction": orig.get("direction"),
                    "from_phone_number": orig.get("from_phone_number"),
                    "to_phone_number": orig.get("to_phone_number"),
                    "duration": orig.get("duration"),
                    "to": orig.get("to"),
                    "from_field": orig.get("from"),
                    "cc": orig.get("cc"),
                    "bcc": orig.get("bcc"),
                    "is_automated_message": orig.get("is_automated_message"),
                    "voicemail_url": orig.get("voicemail_url"),
                    "recording_url": orig.get("recording_url"),
                    "attached_files": orig.get("attached_files"),
                    "chat_input_question": orig.get("chat_input_question"),
                    "chat_input_answer": orig.get("chat_input_answer"),
                    "chat_menu_text": orig.get("chat_menu_text"),
                    "form_submission": orig.get("formSubmission"),
                }
            )

            try:
                sentiment = sentiment_analyzer.analyze(text)
            except Exception as e:
                print(f"⚠️ Sentiment failed for {msg_id}: {e}")
                sentiment = None

            try:
                top_faqs = find_top_faqs(embedding, top_n=5)
                matched_faq = rerank_with_gpt(text, top_faqs, openai_api_key=openai_key)
                gpt_eval = gpt.score_resolution(text, matched_faq.answer)
            except Exception as e:
                print(f"⚠️ GPT failed for {msg_id}: {e}")
                matched_faq = None
                gpt_eval = {"label": "unknown", "score": 0, "reason": "N/A"}

            Message.objects.filter(message_id=msg_id).update(
                sentiment=sentiment,
                gpt_label=gpt_eval["label"],
                gpt_score=gpt_eval["score"],
                gpt_reason=gpt_eval["reason"],
                matched_faq=matched_faq
            )
            saved += 1

        print(f"✅ GPT matching complete: {saved} messages processed")
        return {**prev, "saved_messages": saved}
    except Exception as e:
        print(f"❌ Error in match_messages_task: {e}")
        raise


@shared_task
def upload_artifacts_task(prev):
    print("🔽 Task: upload_artifacts_task")
    try:
        setup_google_credentials_from_env()
        gcs_bucket = os.getenv("GCS_BUCKET_NAME")
        if not gcs_bucket:
            raise Exception("Missing GCS_BUCKET_NAME")

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        gcs_prefix = f"faq_pipeline/{timestamp}"
        files = {
            "dixa": prev["dixa_path"],
            "cleaned": prev["cleaned_path"],
            "embeddings": prev["embeddings_path"],
        }
        uploaded = []
        for label, path in files.items():
            dest = f"{gcs_prefix}/{label}.json"
            result = upload_to_gcs(gcs_bucket, path, dest)
            uploaded.append(result)

        print(f"✅ Uploaded all files: {uploaded}")
        return {**prev, "uploaded_files": uploaded}
    except Exception as e:
        print(f"❌ Error in upload_artifacts_task: {e}")
        raise


@shared_task
def cluster_and_summarize_task(prev):
    print("🔽 Task: cluster_and_summarize_task")
    try:
        process_clusters_and_save()
        print("✅ Clustering and summarization complete.")
        return {"status": "pipeline_complete", **prev}
    except Exception as e:
        print(f"❌ Error in cluster_and_summarize_task: {e}")
        raise


@shared_task(name="faq_api.tasks.start_pipeline")
def start_pipeline():
    print("🚀 Starting full FAQ pipeline...")
    return chain(
        download_dixa_task.s(),
        download_elevio_task.s(),
        preprocess_messages_task.s(),
        embed_messages_task.s(),
        match_messages_task.s(),
        upload_artifacts_task.s(),
        cluster_and_summarize_task.s()
    ).apply_async()
