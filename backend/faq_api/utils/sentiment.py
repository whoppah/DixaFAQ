#backend/faq_api/utils/sentiment.py
import openai
from django.conf import settings

class SentimentAnalyzer:
    def __init__(self, model="gpt-3.5-turbo", api_key=None):
        self.model = model
        self.api_key = api_key or settings.OPENAI_API_KEY

    def analyze(self, text):
        prompt = (
            "You are a sentiment analysis expert. Classify the following message "
            "as one of the following: Positive, Neutral, or Negative.\n\n"
            f"Message: \"{text}\"\n"
            "Respond with one word only."
        )

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                api_key=self.api_key,
                messages=[
                    {"role": "system", "content": "You analyze customer support sentiment."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
            )
            sentiment = response.choices[0].message['content'].strip().lower()

            if "positive" in sentiment:
                return "positive"
            elif "negative" in sentiment:
                return "negative"
            return "neutral"
        except Exception as e:
            print(f"⚠️ Sentiment analysis failed: {e}")
            return "unknown"
