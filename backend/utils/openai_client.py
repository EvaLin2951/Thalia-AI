"""
OpenAI Client Module
"""
import os
import openai
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY") or "your-api-key-here"

def call_model_with_prompt(prompt: str) -> Optional[str]:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            presence_penalty=0.5,
            max_tokens=600
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI model: {e}")
        return None