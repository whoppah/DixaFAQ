#backend/utils/gpt.py
import openai

class GPTFAQAnalyzer:
    def __init__(self, openai_api_key, model="gpt-4o"):
        openai.api_key = openai_api_key
        self.model = model

    def evaluate_coverage(self, question, faq_answer):
        prompt = f"""
You are an FAQ evaluator.

User question:
{question}

FAQ Answer:
{faq_answer}

Does the FAQ fully and clearly answer the user's question? Answer with one of the following:
- Fully covered
- Partially covered
- Not covered

Then explain why.
"""
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that evaluates FAQ coverage."},
                {"role": "user", "content": prompt}
            ]
        )
        result = response['choices'][0]['message']['content']
        return result
        
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
        import json
        try:
            parsed = json.loads(content)
            return parsed
        except Exception:
            return {"label": "Unknown", "score": 0, "reason": content}


