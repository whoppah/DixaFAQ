from openai import OpenAI
from django.conf import settings
import time
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception

class SentimentAnalyzer:
    def __init__(self, model="moonshotai/kimi-k2:free", api_key=None):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key or settings.KIMI_API_KEY
        )
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
