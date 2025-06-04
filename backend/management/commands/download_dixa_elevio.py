from django.core.management.base import BaseCommand
from faq_api.utils.dixa_downloader import DixaDownloader
from faq_api.utils.elevio_downloader import ElevioFAQDownloader
import os
import datetime

class Command(BaseCommand):
    help = 'Download messages from Dixa and FAQs from Elevio'

    def handle(self, *args, **kwargs):
        print("🚀 Running Dixa + Elevio downloader...")

        dixa_token = os.getenv("DIXA_API_TOKEN")
        elevio_key = os.getenv("ELEVIO_API_KEY")
        elevio_jwt = os.getenv("ELEVIO_JWT")

        if not all([dixa_token, elevio_key, elevio_jwt]):
            print("❌ Missing API credentials in environment variables.")
            return

        dixa = DixaDownloader(
            api_token=dixa_token,
            start_date=datetime.datetime(2025, 1, 1),
            end_date=datetime.datetime.now()
        )
        dixa.download_all_dixa_data()

        elevio = ElevioFAQDownloader(api_key=elevio_key, jwt=elevio_jwt)
        elevio.download_all_faqs()

        print("✅ Download complete.")
