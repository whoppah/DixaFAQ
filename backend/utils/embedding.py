#backend/utils/embedding.py
import os
import openai
import json
import tiktoken

class Tokenizer:
    def __init__(self, messages_path, openai_api_key,model="text-embedding-3-small",max_tokens=256,tokenizer=tiktoken.get_encoding("cl100k_base"), output_path=None):
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
                model= self.model
            )
            print("Embedding retrieved:", response.data[0].embedding[:5])
        except Exception as e:
            print("❌", e)

    def truncate_text(self, text):
        tokens = self.tokenizer.encode(text)
        return self.tokenizer.decode(tokens[:self.max_tokens]) if len(tokens) > self.max_tokens else text

    def embed_all(self):
        print("Starting to get the embeddings...")
        if not os.path.exists(self.messages_path):
            raise FileNotFoundError(f"Input file not found: {self.messages_path}")

        with open(self.messages_path, "r", encoding="utf-8") as f:
            messages = json.load(f)

        embeddings = []
        for msg in messages:
            text = msg.get("text", "")
            if not isinstance(text, str) or not text.strip():
                continue

            clean_text = self.truncate_text(text)
            try:
                response = openai.embeddings.create(
                    input=clean_text,
                    model=self.model
                )
                embedding_data = response.data
                if embedding_data:
                    embeddings.append({
                        "id": msg.get("id", None),
                        "embedding": embedding_data[0].embedding,
                        "text": clean_text
                    })
                else:
                    print(f"No embedding returned for message ID: {msg.get('id')}")
            except Exception as e:
                print(f"Error embedding message ID {msg.get('id')}: {e}")
                continue

        if self.output_path:
            try:
                with open(self.output_path, "w", encoding="utf-8") as f:
                    json.dump(embeddings, f, indent=2)
                print(f"✅ Embeddings saved to {self.output_path}")
            except Exception as e:
                print(f"❌ Failed to save embeddings: {e}")

        return embeddings
