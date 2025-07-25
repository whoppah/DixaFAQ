# backend/faq_api/utils/gpt.py
import json
from groq import Groq, RateLimitError
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type,
)

class GPTFAQAnalyzer:
    def __init__(self, groq_api_key, model="llama3-70b-8192"):
        self.client = Groq(api_key=groq_api_key)
        self.model = model

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        wait=wait_exponential(multiplier=1, min=1, max=30),
        stop=stop_after_attempt(5),
    )
    def _chat(self, **kwargs):
        """Wrapper around Groq chat completion with retry on rate limits."""
        return self.client.chat.completions.create(**kwargs)

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

Respond in JSON format. Do NOT include any markdown formatting, code blocks, or triple backticks.
Format:
{{"label": "...", "score": ..., "reason": "..."}}
"""
        try:
            response = self._chat(model=self.model, messages=[{"role": "user", "content": prompt}])
            content = response.choices[0].message.content.strip()
        except RateLimitError as e:
            print(f"⚠️ Rate‐limited on score_resolution: {e}")
            return {"label": "Unknown", "score": 0, "reason": "rate‐limited"}
        except Exception as e:
            print(f"❌ GROQ API call failed: {e}")
            return {"label": "Unknown", "score": 0, "reason": "API error"}

        # Strip markdown code block formatting
        if content.startswith("```") and content.endswith("```"):
            content = content.strip("` \n")
            if content.startswith("json"):
                content = content[4:].strip()

        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict) and "label" in parsed and "score" in parsed:
                return parsed
        except Exception as e:
            print(f"⚠️ Failed to parse score_resolution response: {e}")
            print(f"⚠️ Raw content:\n{content}")

        return {"label": "Unknown", "score": 0, "reason": content}

    def get_sentiment(self, text):
        prompt = (
            "You are a sentiment analysis expert. Classify the following message "
            "as one of: Positive, Neutral, or Negative.\n\n"
            f"Message: \"{text}\""
        )
        try:
            response = self._chat(model=self.model, messages=[{"role": "user", "content": prompt}])
            return response.choices[0].message.content.strip()
        except RateLimitError as e:
            print(f"⚠️ Rate‐limited on get_sentiment: {e}")
            return "unknown"
        except Exception as e:
            print(f"❌ get_sentiment failed: {e}")
            return "unknown"

    def summarize_cluster(self, messages):
        full_text = "\n".join([m["text"] for m in messages])
        prompt = f"Summarize the key topic or issue from the following user messages:\n\n{full_text}"
        try:
            response = self._chat(model=self.model, messages=[{"role": "user", "content": prompt}])
            return response.choices[0].message.content.strip()
        except RateLimitError as e:
            print(f"⚠️ Rate‐limited on summarize_cluster: {e}")
            return ""
        except Exception as e:
            print(f"❌ summarize_cluster failed: {e}")
            return ""

    def suggest_faq(self, question):
        prompt = f"""
Suggest a better FAQ (Q&A) to address the following user message if the current FAQ is insufficient.

User message:
{question}

Respond ONLY with a raw JSON object. Do NOT include any markdown formatting, triple backticks, or explanation.

Format:
{{
  "question": "...",
  "answer": "..."
}}
"""
        try:
            response = self._chat(model=self.model, messages=[{"role": "user", "content": prompt}])
            content = response.choices[0].message.content.strip()
        except RateLimitError as e:
            print(f"⚠️ Rate‐limited on suggest_faq: {e}")
            return {"question": "", "answer": ""}
        except Exception as e:
            print(f"❌ suggest_faq failed: {e}")
            return {"question": "", "answer": ""}

        # Strip markdown-style code blocks
        if content.startswith("```") and content.endswith("```"):
            content = content.strip("` \n")
            if content.startswith("json"):
                content = content[4:].strip()

        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict) and "question" in parsed and "answer" in parsed:
                return parsed
        except Exception as e:
            print(f"⚠️ Failed to parse suggest_faq response: {e}")
            print(f"⚠️ Raw content:\n{content}")

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
        try:
            response = self._chat(model=self.model, messages=[{"role": "user", "content": prompt}])
            return response.choices[0].message.content.strip()
        except RateLimitError as e:
            print(f"⚠️ Rate‐limited on label_topic: {e}")
            return ""
        except Exception as e:
            print(f"❌ label_topic failed: {e}")
            return ""

    def extract_gpt_keywords(self, messages, label=""):
        texts = [m.text for m in messages if m.text]
        if not texts:
            return []

        sample = "\n".join(f"- {t}" for t in texts[:50])
        prompt = f"""
You are an expert at analyzing customer support messages.

Given the following user messages related to {label or 'various topics'}, extract the top 10 recurring questions or topic keywords that appear across them.

Respond ONLY as a JSON list of strings.

Messages:
{sample}
"""
        try:
            response = self._chat(model=self.model, messages=[{"role": "user", "content": prompt}])
            content = response.choices[0].message.content
            parsed = json.loads(content)
            return parsed if isinstance(parsed, list) else []
        except RateLimitError as e:
            print(f"⚠️ Rate‐limited on extract_gpt_keywords: {e}")
            return []
        except Exception as e:
            print(f"❌ extract_gpt_keywords failed: {e}")
            return []
