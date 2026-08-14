import os
from openai import OpenAI


def get_client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
    )


def get_model() -> str:
    return os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3.5-lightning:free")


def generate_response(
    system_prompt: str,
    user_query: str,
    conversation_history: list[dict] | None = None,
) -> str:
    client = get_client()
    model = get_model()

    messages = [{"role": "system", "content": system_prompt}]

    if conversation_history:
        messages.extend(conversation_history[-6:])

    messages.append({"role": "user", "content": user_query})

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content
    except Exception as e:
        msg = str(e)
        if "429" in msg or "rate" in msg.lower():
            return "MediGuide: The AI is busy right now. Please wait a moment and try again."
        return f"An error occurred: {e}"
