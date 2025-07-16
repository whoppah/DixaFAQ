#backend/faq_api/utils/sentiment.py
from openai import OpenAI
from django.conf import settings

class SentimentAnalyzer:
    def __init__(self, model="moonshotai/kimi-k2:free", api_key=None):
        self.client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key or settings.KIMI_API_KEY)
        self.model = model

    def analyze(self, text):
        prompt = (
            "You are a sentiment analysis expert. Classify the following message "
            "as one of the following: Positive, Neutral, or Negative.\n\n"
            f"Message: \"{text}\"\n"
            "Respond with one word only."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You analyze customer support sentiment."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
            )
            sentiment = response.choices[0].message.content.strip().lower()

            if "positive" in sentiment:
                return "positive"
            elif "negative" in sentiment:
                return "negative"
            return "neutral"
        except Exception as e:
            print(f"⚠️ Sentiment analysis failed: {e}")
            return "unknown"
