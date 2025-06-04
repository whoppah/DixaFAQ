import os
import json
from django.core.management.base import BaseCommand
from faq_api.utils.preprocess import MessagePreprocessor
from faq_api.utils.embedding import Tokenizer
from faq_api.models import Message

class Command(BaseCommand):
    help = 'Preprocess and embed messages, then save to the database'

    def add_arguments(self, parser):
        parser.add_argument('--input', type=str, required=True, help='Path to input JSON file with raw messages')
        parser.add_argument('--output', type=str, required=True, help='Path to save anonymized JSON output')
        parser.add_argument('--embedding_output', type=str, required=True, help='Path to save embeddings JSON')
        parser.add_argument('--openai_key', type=str, required=True, help='OpenAI API Key')

    def handle(self, *args, **options):
        input_path = options['input']
        output_path = options['output']
        embedding_output_path = options['embedding_output']
        openai_key = options['openai_key']

        print("🧹 Preprocessing messages...")
        processor = MessagePreprocessor()
        processor.process_file(input_path, output_path)

        print("🔐 Embedding messages...")
        tokenizer = Tokenizer(
            messages_path=output_path,
            openai_api_key=openai_key,
            output_path=embedding_output_path
        )
        embeddings = tokenizer.embed_all()

        print("💾 Saving to database...")
        for item in embeddings:
            Message.objects.update_or_create(
                message_id=item["id"],
                defaults={
                    "text": item["text"],
                    "embedding": item["embedding"]
                }
            )

        print("✅ Preprocessing, embedding, and saving complete.")
