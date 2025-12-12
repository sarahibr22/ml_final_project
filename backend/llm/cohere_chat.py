
# === OpenAI Chat API (NEW) ===
def openai_chat_stream_v2(
    messages,
    api_key: str,
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.7,
    max_tokens: int = 1024
):
    """
    Streaming OpenAI chat (yields text chunks).
    """
    import openai
    openai.api_key = api_key
    stream = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=True
    )
    for chunk in stream:
        if "choices" in chunk and chunk["choices"] and "delta" in chunk["choices"][0]:
            delta = chunk["choices"][0]["delta"]
            if "content" in delta:
                yield delta["content"]

def openai_chat_v2(
    messages,
    api_key: str,
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.7,
    max_tokens: int = 1024
):
    """
    Non-streaming OpenAI chat (returns full response).
    """
    import openai
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=False
    )
    return response["choices"][0]["message"]["content"].strip()


# llm/cohere_chat.py
import os
import cohere
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
co = cohere.Client(COHERE_API_KEY)

def cohere_chat(
    messages,
    model="command-r-plus-08-2024",
    temperature=0.7,
    max_tokens=1024
):
    """
    Call Cohere's chat endpoint using the latest Cohere v5 API.
    
    messages must be a list of dicts:
    [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi!"}
    ]
    """


    # If messages is a list, extract the last user message string
    if isinstance(messages, list):
        # Find the last user message
        user_messages = [m for m in messages if m.get("role", "").lower() == "user"]
        if user_messages:
            message = user_messages[-1].get("message") or user_messages[-1].get("content")
        else:
            message = str(messages[-1]) if messages else ""
    else:
        message = str(messages)

    resp = co.chat(
        model=model,
        message=message,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    # Cohere v5 returns text in resp.text for non-streamed chat
    return resp.text


# --------------------------------------------
# 3. Streaming version (optional)
# --------------------------------------------
def cohere_chat_stream(
    messages,
    model="command-r-plus-08-2024",
    temperature=0.7,
    max_tokens=1024
):
    """
    Streaming chat generation.
    Yields each chunk of text as it arrives.
    """


    # If messages is a list, extract the last user message string
    if isinstance(messages, list):
        user_messages = [m for m in messages if m.get("role", "").lower() == "user"]
        if user_messages:
            message = user_messages[-1].get("message") or user_messages[-1].get("content")
        else:
            message = str(messages[-1]) if messages else ""
    else:
        message = str(messages)

    stream = co.chat_stream(
        model=model,
        message=message,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    for event in stream:
        if event.event_type == "text-generation":
            yield event.text
