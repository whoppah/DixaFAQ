#backend/faq_api/tasks.py
import os
import json
import datetime
import tempfile
import pytz
from celery import shared_task
from faq_api.utils.dixa_downloader import DixaDownloader
from faq_api.utils.elevio_downloader import ElevioFAQDownloader
from faq_api.utils.preprocess import MessagePreprocessor
from faq_api.utils.embedding import Tokenizer
from faq_api.models import Message
from google.cloud import storage

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
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_path)
    print(f"✅ Uploaded to gs://{bucket_name}/{destination_blob_name}")
    return destination_blob_name

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

        if not all([dixa_token, elevio_key, elevio_jwt, openai_key, gcs_bucket]):
            raise Exception("❌ Missing one or more required environment variables")

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        gcs_prefix = f"faq_pipeline/{timestamp}"
        summary["timestamp"] = timestamp

        # Download Dixa
        print("📥 Downloading Dixa")
        dixa = DixaDownloader(
            api_token=dixa_token,
            start_date=datetime.datetime(2025, 5, 1),
            end_date=datetime.datetime.now()
        )
        dixa_output = "/tmp/dixa_messages.json"
        dixa.download_all_dixa_data(output_path=dixa_output)

        with open(dixa_output) as f:
            data = json.load(f)
            summary["dixa_message_count"] = len(data.get("messages", []))

        # Download Elevio
        print("📥 Downloading Elevio")
        elevio = ElevioFAQDownloader(api_key=elevio_key, jwt=elevio_jwt)
        elevio_output = "/tmp/elevio_faqs.json"
        elevio.download_all_faqs(output_path=elevio_output)

        # Preprocess
        cleaned_path = "/tmp/cleaned.json"
        processor = MessagePreprocessor()
        processor.process_file(dixa_output, cleaned_path)

        # Embed
        embeddings_path = "/tmp/embeddings.json"
        tokenizer = Tokenizer(
            messages_path=cleaned_path,
            openai_api_key=openai_key,
            output_path=embeddings_path
        )
        embeddings = tokenizer.embed_all()

        saved_count = 0
        for item in embeddings:
            Message.objects.update_or_create(
                message_id=item["id"],
                defaults={"text": item["text"], "embedding": item["embedding"]}
            )
            saved_count += 1
        summary["embedding_saved"] = saved_count

        # Upload
        print("☁️ Uploading to GCS")
        for local_path, gcs_name in [
            (dixa_output, f"{gcs_prefix}/dixa_messages.json"),
            (elevio_output, f"{gcs_prefix}/elevio_faqs.json"),
            (cleaned_path, f"{gcs_prefix}/cleaned.json"),
            (embeddings_path, f"{gcs_prefix}/embeddings.json")
        ]:
            uploaded = upload_to_gcs(gcs_bucket, local_path, gcs_name)
            summary["files_uploaded"].append(f"gs://{gcs_bucket}/{uploaded}")

        print("✅ Pipeline completed")
        print("📊 Summary:", json.dumps(summary, indent=2))
        return summary

    except Exception as e:
        print(f"❌ Error in pipeline: {e}")
        raise
