# backend/faq_api/utils/embedding.py
import os
import json
import requests
import tiktoken
from datetime import datetime
from bs4 import BeautifulSoup
from faq_api.models import FAQ, Message

class Tokenizer:
    def __init__(
        self,
        messages_path,
        jina_api_key,
        model="jina-embeddings-v4",
        task="text-matching",
        max_tokens=256,
        tokenizer=None,
        output_path=None,
    ):
        self.messages_path = messages_path
        self.jina_api_key = jina_api_key
        self.model = model
        self.task = task
        self.max_tokens = max_tokens
        # default to GPT-style tokenizer if none provided
        self.tokenizer = tokenizer or tiktoken.get_encoding("cl100k_base")
        self.output_path = output_path

        self.jina_url = "https://api.jina.ai/v1/embeddings"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.jina_api_key}"
        }

        # Track the first embedding length we see, to enforce uniform dims
        self.expected_dim = None

    def test_embedding(self):
        """Quick smoke test against Jina endpoint."""
        payload = {
            "model": self.model,
            "task": self.task,
            "input": [{"text": "Hello, world!"}]
        }
        try:
            resp = requests.post(self.jina_url, headers=self.headers, json=payload)
            resp.raise_for_status()
            data = resp.json().get("data", [])
            print("Embedding retrieved:", data[0]["embedding"][:5])
        except Exception as e:
            print("❌", e)

    def truncate_text(self, text):
        tokens = self.tokenizer.encode(text)
        if len(tokens) > self.max_tokens:
            return self.tokenizer.decode(tokens[: self.max_tokens])
        return text

    def strip_html(self, raw_html):
        return BeautifulSoup(raw_html, "html.parser").get_text(separator=" ").strip()

    def insert_messages_into_db(self):
        print("📥 Loading and inserting messages...")
        if not os.path.exists(self.messages_path):
            raise FileNotFoundError(f"Input file not found: {self.messages_path}")

        with open(self.messages_path, "r", encoding="utf-8") as f:
            messages = json.load(f)

        inserted = skipped = 0
        for msg in messages:
            msg_id = msg.get("id")
            text = msg.get("text")
            if not msg_id or not text:
                skipped += 1
                continue

            created_at_ms = msg.get("created_at")
            created_at = (
                datetime.fromtimestamp(created_at_ms / 1000.0)
                if created_at_ms
                else None
            )

            Message.objects.update_or_create(
                message_id=msg_id,
                defaults={
                    "csid": msg.get("csid") or None,
                    "created_at": created_at,
                    "initial_channel": msg.get("initial_channel") or None,
                    "author_name": msg.get("author_name") or None,
                    "author_email": msg.get("author_email") or None,
                    "direction": msg.get("direction") or None,
                    "text": text,
                    "from_phone_number": msg.get("from_phone_number") or None,
                    "to_phone_number": msg.get("to_phone_number") or None,
                    "duration": msg.get("duration") or None,
                    "to": msg.get("to") if isinstance(msg.get("to"), list) else [],
                    "from_field": msg.get("from") or None,
                    "cc": msg.get("cc") if isinstance(msg.get("cc"), list) else [],
                    "bcc": msg.get("bcc") if isinstance(msg.get("bcc"), list) else [],
                    "is_automated_message": msg.get("is_automated_message") or False,
                    "voicemail_url": msg.get("voicemail_url") or None,
                    "recording_url": msg.get("recording_url") or None,
                    "attached_files": msg.get("attached_files")
                    if isinstance(msg.get("attached_files"), list)
                    else [],
                    "chat_input_question": msg.get("chat_input_question") or None,
                    "chat_input_answer": msg.get("chat_input_answer") or None,
                    "chat_menu_text": msg.get("chat_menu_text") or None,
                    "form_submission": msg.get("formSubmission") or None,
                },
            )
            inserted += 1

        print(f"✅ Inserted or updated: {inserted}")
        print(f"⚠️ Skipped (missing ID or text): {skipped}")

    def embed_all(self):
        print("🔍 Starting DB-based embedding for messages without embeddings...")
        embeddings = []
        skipped = 0

        messages = Message.objects.filter(embedding__isnull=True)
        if not messages.exists():
            print("⚠️ No messages found without embeddings.")
            return []

        for msg in messages:
            msg_id = msg.message_id
            raw_text = msg.text or ""
            if not isinstance(raw_text, str) or not raw_text.strip():
                print(f"⚠️ Skipping message ID {msg_id} – empty or non-string text")
                skipped += 1
                continue

            stripped_text = self.strip_html(raw_text)
            if not stripped_text:
                print(f"⚠️ Skipping message ID {msg_id} – empty after HTML stripping")
                skipped += 1
                continue

            clean_text = self.truncate_text(stripped_text)

            payload = {
                "model": self.model,
                "task": self.task,
                "input": [{"text": clean_text}],
            }

            try:
                resp = requests.post(self.jina_url, headers=self.headers, json=payload)
                resp.raise_for_status()
                data = resp.json().get("data", [])
                if not data:
                    print(f"❌ No embedding returned for message ID: {msg_id}")
                    continue

                embedding = data[0]["embedding"]
                # enforce consistent embedding dimension
                if self.expected_dim is None:
                    self.expected_dim = len(embedding)
                    print(f"ℹ️ Expecting embedding dim = {self.expected_dim}")
                elif len(embedding) != self.expected_dim:
                    print(f"⚠️ Skipping message ID {msg_id}: dim {len(embedding)} ≠ {self.expected_dim}")
                    skipped += 1
                    continue

                msg.embedding = embedding
                msg.save(update_fields=["embedding"])

                embeddings.append(
                    {"message_id": msg_id, "embedding": embedding, "text": clean_text}
                )
                print(f"✅ Embedded message ID: {msg_id}")

            except Exception as e:
                print(f"❌ Error embedding message ID {msg_id}: {e}")
                skipped += 1
                continue

        if self.output_path:
            try:
                with open(self.output_path, "w", encoding="utf-8") as f:
                    json.dump(embeddings, f, indent=2)
                print(f"💾 Embeddings also saved to file: {self.output_path}")
            except Exception as e:
                print(f"❌ Failed to save embeddings file: {e}")

        print(f"\n🎯 Embedding complete — Total: {len(embeddings)} | Skipped: {skipped}")
        return embeddings

        def embed_and_store_faqs(self, faq_items):
            print("📌 Starting FAQ embedding...")
            if not isinstance(faq_items, list):
                raise ValueError("Expected a list of FAQ dictionaries.")
    
            embedded_count = 0
            skipped = 0
            failed = []
    
            for i, faq in enumerate(faq_items, 1):
                question = (faq.get("question") or "").strip()
                answer   = (faq.get("answer")   or "").strip()
                if not question or not answer:
                    print(f"⚠️ Skipping FAQ #{i} — missing question or answer")
                    skipped += 1
                    continue
    
                payload = {"model": self.model, "task": self.task, "input": [{"text": question}]}
                try:
                    resp = requests.post(self.jina_url, headers=self.headers, json=payload)
                    resp.raise_for_status()
                    data = resp.json().get("data", [])
                    if not data:
                        raise Exception("No embedding returned")
    
                    embedding = data[0]["embedding"]
                    # enforce consistent embedding dimension
                    if self.expected_dim is None:
                        self.expected_dim = len(embedding)
                        print(f"ℹ️ Expecting embedding dim = {self.expected_dim}")
                    elif len(embedding) != self.expected_dim:
                        print(f"⚠️ Skipping FAQ #{i} — dim {len(embedding)} ≠ expected {self.expected_dim}")
                        skipped += 1
                        continue
    
                    faq_obj, created = FAQ.objects.update_or_create(
                        question=question,
                        defaults={"answer": answer, "embedding": embedding},
                    )
                    action = "Created" if created else "Updated"
                    print(f"✅ {action} FAQ #{i}: {question[:50]}")
                    embedded_count += 1
    
                except Exception as e:
                    print(f"❌ Error embedding FAQ #{i}: {question[:50]} | {e}")
                    failed.append({"question": question, "error": str(e)})
    
            print(f"\n🎯 Finished embedding {embedded_count} FAQs (skipped {skipped}, failed {len(failed)})")
            if failed:
                print(f"❌ Failed FAQs: {len(failed)}")
                for f in failed[:3]:
                    print(f"  - Question: {f['question'][:50]} | Error: {f['error']}")
            return embedded_count, failed

