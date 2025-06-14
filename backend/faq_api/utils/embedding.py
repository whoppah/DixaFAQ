#backend/faq_api/utils/embedding.py
import os
import openai
import json
import tiktoken
from datetime import datetime
from faq_api.models import FAQ, Message


class Tokenizer:
    def __init__(self, messages_path, openai_api_key, model="text-embedding-3-small",
                 max_tokens=256, tokenizer=tiktoken.get_encoding("cl100k_base"), output_path=None):
        self.messages_path = messages_path
        self.openai_api_key = openai_api_key
        self.tokenizer = tokenizer
        self.max_tokens = max_tokens
        self.model = model
        self.output_path = output_path
        openai.api_key = openai_api_key

    def test_embedding(self):
        try:
            response = openai.embeddings.create(
                input="Hello, world!",
                model=self.model
            )
            print("Embedding retrieved:", response.data[0].embedding[:5])
        except Exception as e:
            print("❌", e)

    def truncate_text(self, text):
        tokens = self.tokenizer.encode(text)
        return self.tokenizer.decode(tokens[:self.max_tokens]) if len(tokens) > self.max_tokens else text

    def insert_messages_into_db(self):
        print("📥 Loading and inserting messages...")
        if not os.path.exists(self.messages_path):
            raise FileNotFoundError(f"Input file not found: {self.messages_path}")

        with open(self.messages_path, "r", encoding="utf-8") as f:
            messages = json.load(f)

        inserted = 0
        skipped = 0

        for msg in messages:
            msg_id = msg.get("id")
            text = msg.get("text")

            if not msg_id or not text:
                skipped += 1
                continue

            created_at_ms = msg.get("created_at")
            created_at = datetime.fromtimestamp(created_at_ms / 1000.0) if created_at_ms else None

            Message.objects.update_or_create(
                message_id=msg_id,
                defaults={
                    "csid": msg.get("csid"),
                    "created_at": created_at,
                    "initial_channel": msg.get("initial_channel"),
                    "author_name": msg.get("author_name"),
                    "author_email": msg.get("author_email"),
                    "direction": msg.get("direction"),
                    "text": text,
                    "from_phone_number": msg.get("from_phone_number"),
                    "to_phone_number": msg.get("to_phone_number"),
                    "duration": msg.get("duration"),
                    "to": msg.get("to"),
                    "from_field": msg.get("from"),  # Make sure your model uses `from_field`
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

        print(f"✅ Inserted or updated: {inserted}")
        print(f"⚠️ Skipped (missing ID or text): {skipped}")

    def embed_all(self):
        print("Starting to get the embeddings...")
        if not os.path.exists(self.messages_path):
            raise FileNotFoundError(f"Input file not found: {self.messages_path}")

        with open(self.messages_path, "r", encoding="utf-8") as f:
            messages = json.load(f)

        embeddings = []
        for msg in messages:
            text = msg.get("text", "")
            msg_id = msg.get("id", None)

            if not isinstance(text, str) or not text.strip() or not msg_id:
                continue

            clean_text = self.truncate_text(text)
            try:
                response = openai.embeddings.create(
                    input=clean_text,
                    model=self.model
                )
                embedding_data = response.data
                if embedding_data:
                    embedding = embedding_data[0].embedding
                    embeddings.append({
                        "id": msg_id,
                        "embedding": embedding,
                        "text": clean_text
                    })

                    updated = Message.objects.filter(message_id=msg_id).update(embedding=embedding)
                    if updated:
                        print(f"✅ Stored embedding for message ID: {msg_id}")
                    else:
                        print(f"⚠️ No matching Message record for ID: {msg_id}")
                else:
                    print(f"No embedding returned for message ID: {msg_id}")
            except Exception as e:
                print(f"Error embedding message ID {msg_id}: {e}")
                continue

        if self.output_path:
            try:
                with open(self.output_path, "w", encoding="utf-8") as f:
                    json.dump(embeddings, f, indent=2)
                print(f"✅ Embeddings saved to {self.output_path}")
            except Exception as e:
                print(f"❌ Failed to save embeddings: {e}")

        return embeddings

    def embed_and_store_faqs(self, faq_items):
        if not isinstance(faq_items, list):
            raise ValueError("Expected a list of FAQ dictionaries.")

        embedded_count = 0
        failed = []

        for i, faq in enumerate(faq_items, 1):
            question = faq.get("question", "").strip()
            answer = faq.get("answer", "").strip()

            if not question or not answer:
                print(f"⚠️ Skipping FAQ #{i} due to missing text")
                continue

            try:
                response = openai.embeddings.create(
                    input=question,
                    model=self.model
                )
                embedding = response.data[0].embedding

                FAQ.objects.update_or_create(
                    question=question,
                    defaults={"answer": answer, "embedding": embedding}
                )
                embedded_count += 1
                print(f"✅ Embedded FAQ #{i}: {question[:60]}")

            except Exception as e:
                print(f"❌ Error embedding FAQ #{i}: {e}")
                failed.append({"question": question, "error": str(e)})

        print(f"\n✅ Finished embedding. Total saved: {embedded_count}")
        if failed:
            print(f"❌ Failed: {len(failed)}")
        return embedded_count, failed
