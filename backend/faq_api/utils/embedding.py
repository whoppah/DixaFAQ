#backend/faq_api/utils/embedding.py
import os
import openai
import json
import tiktoken
from datetime import datetime
from bs4 import BeautifulSoup
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

    def strip_html(self, raw_html):
        return BeautifulSoup(raw_html, "html.parser").get_text(separator=" ").strip()

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

        print(f"✅ Inserted or updated: {inserted}")
        print(f"⚠️ Skipped (missing ID or text): {skipped}")

    def embed_all(self):
        print("🔍 Starting to get the embeddings...")
        if not os.path.exists(self.messages_path):
            raise FileNotFoundError(f"Input file not found: {self.messages_path}")

        with open(self.messages_path, "r", encoding="utf-8") as f:
            messages = json.load(f)

        embeddings = []
        skipped = 0

        for msg in messages:
            msg_id = msg.get("id")
            raw_text = msg.get("text", "")

            if not isinstance(raw_text, str) or not raw_text.strip():
                print(f"⚠️ Skipping message ID {msg_id} – empty or non-string text")
                skipped += 1
                continue

            if not msg_id:
                print(f"⚠️ Skipping message with missing ID: {raw_text[:50]}")
                skipped += 1
                continue

            stripped_text = self.strip_html(raw_text)
            if not stripped_text.strip():
                print(f"⚠️ Skipping message ID {msg_id} – text empty after HTML stripping")
                skipped += 1
                continue

            clean_text = self.truncate_text(stripped_text)

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
                    print(f"❌ No embedding returned for message ID: {msg_id}")
            except Exception as e:
                print(f"❌ Error embedding message ID {msg_id}: {e}")
                continue

        if self.output_path:
            try:
                with open(self.output_path, "w", encoding="utf-8") as f:
                    json.dump(embeddings, f, indent=2)
                print(f"✅ Embeddings saved to {self.output_path}")
            except Exception as e:
                print(f"❌ Failed to save embeddings: {e}")

        print(f"\n✅ Finished embedding. Total: {len(embeddings)} | Skipped: {skipped}")
        return embeddings

    def embed_and_store_faqs(self, faq_items):
        print("📌 Starting FAQ embedding...")
    
        if not isinstance(faq_items, list):
            raise ValueError("Expected a list of FAQ dictionaries.")
    
        embedded_count = 0
        failed = []
    
        for i, faq in enumerate(faq_items, 1):
            question = faq.get("question", "").strip()
            answer = faq.get("answer", "").strip()
    
            if not question or not answer:
                print(f"⚠️ Skipping FAQ #{i} — missing question or answer")
                continue
    
            try:
                print(f"🔹 Embedding FAQ #{i}: {question[:50]}...")
                response = openai.embeddings.create(
                    input=question,
                    model=self.model
                )
    
                if not response or not response.data or not hasattr(response.data[0], "embedding"):
                    raise Exception("OpenAI returned an empty or invalid embedding")
    
                embedding = response.data[0].embedding
    
                faq_obj, created = FAQ.objects.update_or_create(
                    question=question,
                    defaults={
                        "answer": answer,
                        "embedding": embedding
                    }
                )
    
                action = "Created" if created else "Updated"
                print(f"✅ {action} FAQ #{i}: {question[:50]}")
                embedded_count += 1
    
            except Exception as e:
                print(f"❌ Error embedding FAQ #{i}: {question[:50]} | {e}")
                failed.append({"question": question, "error": str(e)})
    
        print(f"\n🎯 Finished embedding {embedded_count} FAQs")
        if failed:
            print(f"❌ Failed FAQs: {len(failed)}")
            for f in failed[:3]:
                print(f"  - Question: {f['question'][:50]} | Error: {f['error']}")
    
        return embedded_count, failed

