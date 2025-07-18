from groq import Groq
from django.conf import settings
import time
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception

class SentimentAnalyzer:
    def __init__(self,groq_api_key, model="llama-3.3-70b-versatile"):
        self.client = Groq(api_key=groq_api_key)
        self.model = model

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
            response = self._create_completion_with_retries(messages)
            sentiment = response.choices[0].message.content.strip().lower()

            if "positive" in sentiment:
                return "positive"
            elif "negative" in sentiment:
                return "negative"
            return "neutral"

        except Exception as e:
            print(f"⚠️ Sentiment analysis failed: {e}")
            return "unknown"

    @retry(
        retry=retry_if_exception(lambda e: getattr(e, "status_code", None) == 429),
        wait=wait_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(5)
    )
    def _create_completion_with_retries(self, messages):
        # If we hit a 429, Tenacity will back off and retry up to 5 times.
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0,
        )
        return response
