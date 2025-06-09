#backend/faq_api/task.py
import os
from datetime import datetime
import json
import pytz
from celery import shared_task
from faq_api.utils.dixa_downloader import DixaDownloader
from faq_api.utils.elevio_downloader import ElevioFAQDownloader
from faq_api.utils.preprocess import MessagePreprocessor
from faq_api.utils.embedding import Tokenizer
from faq_api.models import Message

@shared_task
def log_timezone_debug():
    now_utc = datetime.utcnow()
    now_local = datetime.now()
    now_amsterdam = datetime.now(pytz.timezone("Europe/Amsterdam"))
    print(f"[UTC]            {now_utc}")
    print(f"[Local naive]    {now_local}")
    print(f"[Europe/Amsterdam] {now_amsterdam}")

@shared_task
def async_download_and_process():
    print("🚀 Starting async Dixa + Elevio + Embedding pipeline")

    # Step 1: Download data
    dixa_token = os.getenv("DIXA_API_TOKEN")
    elevio_key = os.getenv("ELEVIO_API_KEY")
    elevio_jwt = os.getenv("ELEVIO_JWT")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not all([dixa_token, elevio_key, elevio_jwt, openai_key]):
        print("❌ Missing one or more required API keys")
        return
    print("Downloading Dixa data")
    dixa = DixaDownloader(
        api_token=dixa_token,
        start_date=datetime.datetime(2025, 5, 1),
        end_date=datetime.datetime.now()
    )
    dixa_output = "/tmp/dixa_messages.json"
    dixa.download_all_dixa_data(output_path=dixa_output)
    print(f"Dixa data saved at {dixa_output}")
    
    print("Download FAQs data")
    elevio = ElevioFAQDownloader(api_key=elevio_key, jwt=elevio_jwt)
    elevio_output = "/tmp/elevio_faqs.json"
    elevio.download_all_faqs(output_path=elevio_output)
    print(f"FAQs data saved at {elevio_output}")

    # Step 2: Preprocess and embed
    cleaned_path = "/tmp/cleaned.json"
    embeddings_path = "/tmp/embeddings.json"

    print("starting preprocessing messages")
    processor = MessagePreprocessor()
    processor.process_file(dixa_output, cleaned_path)

    print("Starting tokenizer")
    tokenizer = Tokenizer(
        messages_path=cleaned_path,
        openai_api_key=openai_key,
        output_path=embeddings_path
    )
    embeddings = tokenizer.embed_all()

    for item in embeddings:
        Message.objects.update_or_create(
            message_id=item["id"],
            defaults={"text": item["text"], "embedding": item["embedding"]}
        )

    print("✅ Async pipeline complete")
