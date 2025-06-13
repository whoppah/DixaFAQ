#backend/faq_api/tasks.py
import os
import json
import datetime
import tempfile
from celery import shared_task
from google.cloud import storage

from faq_api.utils.dixa_downloader import DixaDownloader
from faq_api.utils.elevio_downloader import ElevioFAQDownloader
from faq_api.utils.preprocess import MessagePreprocessor
from faq_api.utils.embedding import Tokenizer
from faq_api.utils.sentiment import SentimentAnalyzer
from faq_api.utils.gpt import GPTFAQAnalyzer
from faq_api.utils.faq_matcher import find_top_faqs, rerank_with_gpt
from faq_api.models import Message, FAQ
from faq_api.utils.pipeline_runner import process_clusters_and_save


def setup_google_credentials_from_env():
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
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_path)
        print(f"✅ Uploaded to gs://{bucket_name}/{destination_blob_name}")
        return destination_blob_name
    except Exception as e:
        print(f"⚠️ Failed to upload {source_file_path} to GCS: {e}")
        return f"FAILED: {destination_blob_name}"


@shared_task(name="download_and_process")
def async_download_and_process():
    print("🚀 Starting async Dixa + Elevio + Embedding pipeline")

    summary = {
        "dixa_message_count": 0,
        "embedding_saved": 0,
        "files_uploaded": [],
        "timestamp": None
    }

    try:
        setup_google_credentials_from_env()

        dixa_token = os.getenv("DIXA_API_TOKEN")
        elevio_key = os.getenv("ELEVIO_API_KEY")
        elevio_jwt = os.getenv("ELEVIO_JWT")
        openai_key = os.getenv("OPENAI_API_KEY")
        gcs_bucket = os.getenv("GCS_BUCKET_NAME")

        env_vars = {
            "DIXA_API_TOKEN": dixa_token,
            "ELEVIO_API_KEY": elevio_key,
            "ELEVIO_JWT": elevio_jwt,
            "OPENAI_API_KEY": openai_key,
            "GCS_BUCKET_NAME": gcs_bucket
        }

        missing = [k for k, v in env_vars.items() if not v]
        if missing:
            raise Exception(f"❌ Missing environment variables: {', '.join(missing)}")

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        gcs_prefix = f"faq_pipeline/{timestamp}"
        summary["timestamp"] = timestamp

        gpt = GPTFAQAnalyzer(openai_api_key=openai_key)
        sentiment_analyzer = SentimentAnalyzer(api_key=openai_key)

        dixa = DixaDownloader(
            api_token=dixa_token,
            start_date=datetime.datetime(2025, 5, 1),
            end_date=datetime.datetime.now()
        )
        all_messages, _ = dixa.download_all_dixa_data()
        dixa_output = "/tmp/dixa_messages.json"
        with open(dixa_output, "w", encoding="utf-8") as f:
            json.dump({"messages": all_messages}, f, indent=2)
        summary["dixa_message_count"] = len(all_messages)

        elevio = ElevioFAQDownloader(api_key=elevio_key, jwt=elevio_jwt)
        faq_items = elevio.download_all_faqs()
        tokenizer = Tokenizer(messages_path=None, openai_api_key=openai_key)
        tokenizer.embed_and_store_faqs(faq_items)

        cleaned_path = "/tmp/cleaned.json"
        processor = MessagePreprocessor()
        processor.process_file(dixa_output, cleaned_path)

        embeddings_path = "/tmp/embeddings.json"
        tokenizer = Tokenizer(
            messages_path=cleaned_path,
            openai_api_key=openai_key,
            output_path=embeddings_path
        )
        dixa_embeddings = tokenizer.embed_all()

        if not dixa_embeddings:
            raise Exception("❌ No embeddings generated. Aborting clustering.")

        saved_count = 0
        for item in dixa_embeddings:
            msg_id = item.get("id")
            text = item.get("text")
            embedding = item.get("embedding")

            if not msg_id or not text or not embedding:
                continue

            sentiment = sentiment_analyzer.analyze(text)

            try:
                top_faqs = find_top_faqs(embedding, top_n=5)
                matched_faq = rerank_with_gpt(text, top_faqs, openai_api_key=openai_key)
                gpt_eval = gpt.score_resolution(text, matched_faq.answer)
            except Exception as e:
                print(f"⚠️ Matching/Scoring failed for {msg_id}: {e}")
                matched_faq = None
                gpt_eval = {"label": "unknown", "score": 0, "reason": "N/A"}

            Message.objects.update_or_create(
                message_id=msg_id,
                defaults={
                    "text": text,
                    "embedding": embedding,
                    "sentiment": sentiment,
                    "gpt_label": gpt_eval.get("label"),
                    "gpt_score": gpt_eval.get("score"),
                    "gpt_reason": gpt_eval.get("reason"),
                    "matched_faq": matched_faq
                }
            )
            saved_count += 1

        summary["embedding_saved"] = saved_count

        for local_path, gcs_name in [
            (dixa_output, f"{gcs_prefix}/dixa_messages.json"),
            (cleaned_path, f"{gcs_prefix}/cleaned.json"),
            (embeddings_path, f"{gcs_prefix}/embeddings.json")
        ]:
            uploaded = upload_to_gcs(gcs_bucket, local_path, gcs_name)
            summary["files_uploaded"].append(
                f"gs://{gcs_bucket}/{gcs_name}" if not uploaded.startswith("FAILED") else uploaded
            )

        print("🧠 Running clustering + GPT analysis...")
        process_clusters_and_save()

        print("✅ Pipeline completed")
        print("📊 Summary:", json.dumps(summary, indent=2))
        return summary

    except Exception as e:
        print(f"❌ Error in pipeline: {e}")
        raise
