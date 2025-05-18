# Logic for interfacing with OpenAI API

import os
import httpx
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file if available

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions"


async def generate_code_review(code: str):
    prompt = (
        "You are a code review assistant. Please review the following code and provide detailed feedback "
        "including any issues related to best practices, potential bugs, and security vulnerabilities:\n\n"
        f"{code}"
    )
    payload = {
        "model": "gpt-3.5-turbo",  # Can change the AI model here
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(OPENAI_ENDPOINT, json=payload, headers=headers)
        print(f"***response***: {response.json()}")
        response.raise_for_status()
        data = response.json()

    # Extract the AI's review from the response
    review_text = data["choices"][0]["message"]["content"]
    return review_text
