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
