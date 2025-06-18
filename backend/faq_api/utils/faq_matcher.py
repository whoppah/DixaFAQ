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
        sim = cosine_similarity(message_embedding, faq.embedding)
        similarities.append((faq, sim))

    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_n]

def rerank_with_gpt(message_text, faq_candidates, openai_api_key):
    client = OpenAI(api_key=openai_api_key)

    prompt = (
        f"User message:\n{message_text}\n\n"
        f"Below are 5 FAQ entries:\n"
    )
    for i, (faq, _) in enumerate(faq_candidates, 1):
        prompt += f"{i}. Q: {faq.question}\n   A: {faq.answer}\n"

    prompt += "\nWhich FAQ best matches the user's question? Reply with just the number (1–5)."

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        content = response.choices[0].message["content"].strip()
        try:
            index = int(content.strip().replace(".", "")) - 1
        except ValueError:
            print(f"❌ GPT rerank failed: invalid number '{content}'")
            return faq_candidates[0][0]
            
        return faq_candidates[index][0]
    except Exception as e:
        print(f"❌ GPT rerank failed: {e}")
        return faq_candidates[0][0]
