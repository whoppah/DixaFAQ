#backend/faq_api/utils/sentiment.py
from groq import Groq, RateLimitError
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type,
)

class SentimentAnalyzer:
    def __init__(self, groq_api_key, model="llama-3.3-70b-versatile"):
        self.client = Groq(api_key=groq_api_key)
        self.model = model

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        wait=wait_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(5),
    )
    def _chat(self, **kwargs):
        """Wrapper around Groq chat completion with retry on rate limits."""
        return self.client.chat.completions.create(**kwargs)

    def analyze(self, text):
        prompt = (
            "You are a sentiment analysis expert. Classify the following message "
            "as one of the following: Positive, Neutral, or Negative.\n\n"
            f"Message: \"{text}\"\n"
            "Respond with one word only."
        )
        messages = [
            {"role": "system", "content": "You analyze customer support sentiment."},
            {"role": "user",   "content": prompt}
        ]

        try:
            response = self._chat(model=self.model, messages=messages, temperature=0)
            sentiment = response.choices[0].message.content.strip().lower()
            if "positive" in sentiment:
                return "positive"
            elif "negative" in sentiment:
                return "negative"
            else:
                return "neutral"

        except RateLimitError as e:
            print(f"⚠️ Rate‐limited on sentiment analysis: {e}")
            return "unknown"
        except Exception as e:
            print(f"⚠️ Sentiment analysis failed: {e}")
            return "unknown"

