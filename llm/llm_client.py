from groq import Groq
from config import GROQ_API_KEY


# Initialize client once
client = Groq(api_key=GROQ_API_KEY)

MODEL_NAME = "llama-3.3-70b-versatile"
TEMPERATURE = 0.1


def call_llm(prompt: str) -> str:
    """
    Sends prompt to Groq LLM and returns raw response text.
    No validation done here.
    """

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=TEMPERATURE,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"⚠ LLM call failed: {e}")
        return ""