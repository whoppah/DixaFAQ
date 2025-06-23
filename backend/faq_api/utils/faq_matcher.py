# backend/faq_api/utils/faq_matcher.py
import numpy as np
from openai import OpenAI
from scipy.spatial.distance import cosine
from faq_api.models import FAQ

def cosine_similarity(vec1, vec2):
    return 1 - cosine(vec1, vec2)

def find_top_faqs(message_embedding, top_n=5):
    faqs = FAQ.objects.exclude(embedding=None)
    similarities = []

    for faq in faqs:
        try:
            sim = cosine_similarity(message_embedding, faq.embedding)
            similarities.append({"faq_id": faq.id, "similarity": sim, "faq": faq})
        except Exception as e:
            print(f"⚠️ Skipping FAQ ID {faq.id} due to error: {e}")

    similarities.sort(key=lambda x: x["similarity"], reverse=True)
    return similarities[:top_n]
def rerank_with_gpt(message_text, faq_candidates, openai_api_key):
    client = OpenAI(api_key=openai_api_key)

    prompt = (
        f"You are an AI assistant. Your job is to find the most relevant FAQ from the list below "
        f"that answers the user's message. Reply with only the number (1 to {len(faq_candidates)}), "
        f"no punctuation or explanation.\n\n"
        f"User message:\n{message_text}\n\n"
        f"FAQ options:\n"
    )

    for i, item in enumerate(faq_candidates, 1):
        faq = item["faq"]
        prompt += f"{i}. Q: {faq.question}\n   A: {faq.answer}\n"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        content = response.choices[0].message.content.strip()
        index = int(content.strip().replace(".", ""))  
        if not (1 <= index <= len(faq_candidates)):
            raise ValueError(f"Index out of range: {index}")

        return faq_candidates[index - 1]["faq"].id
    except Exception as e:
        print(f"❌ GPT rerank failed: {e} — fallback to top FAQ candidate")
        return faq_candidates[0]["faq"].id
