# backend/faq_api/utils/gpt.py
import json
from openai import OpenAI

class GPTFAQAnalyzer:
    def __init__(self, openai_api_key, model="gpt-4o"):
        self.client = OpenAI(api_key=openai_api_key)
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
    
    Respond in JSON format. Do NOT include any markdown formatting, code blocks, or triple backticks.
    Format:
    {{"label": "...", "score": ..., "reason": "..."}}
    """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ GPT API call failed: {e}")
            return {"label": "Unknown", "score": 0, "reason": "API error"}
    
        #Strip markdown code block formatting if present
        if content.startswith("```") and content.endswith("```"):
            content = content.strip("` \n")
            if content.startswith("json"):
                content = content[4:].strip()
    
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict) and "label" in parsed and "score" in parsed:
                return parsed
        except Exception as e:
            print(f"⚠️ Failed to parse GPT score response: {e}")
            print(f"⚠️ Raw content from GPT:\n{content}")
    
        return {"label": "Unknown", "score": 0, "reason": content}



    def get_sentiment(self, text):
        prompt = f"What is the sentiment of this message? Respond with: Positive, Neutral, or Negative.\n\nMessage: {text}"
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

    def summarize_cluster(self, messages):
        full_text = "\n".join([m["text"] for m in messages])
        prompt = f"Summarize the key topic or issue from the following user messages:\n\n{full_text}"
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ GPT API call failed during suggest_faq: {e}")
            return {"question": "", "answer": ""}
    
        #Strip markdown-style code blocks if present
        if content.startswith("```") and content.endswith("```"):
            content = content.strip("` \n")
            if content.startswith("json"):
                content = content[4:].strip()
    
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict) and "question" in parsed and "answer" in parsed:
                return parsed
        except Exception as e:
            print(f"⚠️ Failed to parse GPT FAQ suggestion: {e}")
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
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            if isinstance(parsed, list):
                return parsed
            return []
        except Exception as e:
            print(f"❌ GPT keyword extraction failed: {e}")
            return []
