import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMModel:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"  # You can use gpt-4o or gpt-4 if available

    def answer_query(self, query, context_docs):
        # Combine context into one text
        context_text = "\n\n".join([doc["text"] for doc in context_docs])
        system_prompt = (
            "You are an AI research assistant helping users understand documents. "
            "Answer the user's question based on the provided context from their documents. "
            "Be helpful and informative. If the exact answer isn't in the context but you can provide "
            "a relevant response based on the context, do so. Only say you don't know if the context "
            "is completely unrelated to the question."
        )
        user_prompt = f"Context from documents:\n{context_text}\n\nQuestion: {query}\nAnswer:"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=500
        )
        return response.choices[0].message.content
