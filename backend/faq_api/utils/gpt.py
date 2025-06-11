# backend/faq_api/utils/gpt.py
import openai
import json

class GPTFAQAnalyzer:
    def __init__(self, openai_api_key, model="gpt-4o"):
        openai.api_key = openai_api_key
        self.model = model

    def score_resolution(self, question, faq_answer):
        prompt = f"""
Evaluate the resolution quality of this FAQ in response to the user's message.

User message:
{question}

FAQ answer:
{faq_answer}

Provide:
- A label: Fully / Partially / Not covered
- A numeric score: 5 (excellent) to 1 (poor)
- A short explanation
Respond in JSON format like:
{{"label": "...", "score": ..., "reason": "..."}}
"""
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response['choices'][0]['message']['content']

        try:
            parsed = json.loads(content)
            # Minimal schema validation
            if isinstance(parsed, dict) and "label" in parsed and "score" in parsed:
                return parsed
        except Exception:
            pass

        # Fallback if JSON fails
        return {"label": "Unknown", "score": 0, "reason": content}

    def get_sentiment(self, text):
        prompt = f"What is the sentiment of this message? Respond with: Positive, Neutral, or Negative.\n\nMessage: {text}"
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content'].strip()

    def summarize_cluster(self, messages):
        full_text = "\n".join([m["text"] for m in messages])
        prompt = f"Summarize the key topic or issue from the following user messages:\n\n{full_text}"
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content'].strip()

    def suggest_faq(self, question):
        prompt = f"""
Suggest a better FAQ (Q&A) to address the following user message if the current FAQ is insufficient.

User message:
{question}

Respond in JSON:
{{
  "question": "...",
  "answer": "..."
}}
"""
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        try:
            return json.loads(response['choices'][0]['message']['content'])
        except Exception:
            return {"question": "", "answer": ""}
    def label_topic(self, messages):
        text = "\n".join([msg["text"] for msg in messages[:5]])
        prompt = f"""
    You are a clustering assistant.
    
    Given the following messages, label the topic in 2–4 descriptive words (e.g., "Shipping Delay", "Login Issue", "Refund Request").
    
    Messages:
    {text}
    
    Respond with just the label.
    """
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content'].strip()

