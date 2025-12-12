# routes/chat_stream.py
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from utils.prompt import build_agent_prompt
from llm.cohere_chat import cohere_chat
import asyncio

chat_stream_router = APIRouter()


async def stream_response(user_query: str):
    agent_prompt = "You are a helpful AI Agentic Medical Assistant"
    user_query_with_prompt = f"{build_agent_prompt()}\n\n{user_query}"
    messages = [
        {"role": "system", "content": agent_prompt},
        {"role": "user", "content": user_query_with_prompt}
    ]
    print("[LLM INPUT]", messages)
    response = cohere_chat(messages)
    # Stream response word by word
    for word in response.split():
        yield word + " "
        await asyncio.sleep(0.3)


@chat_stream_router.get("/chat-stream")
async def chat_stream(prompt: str):
    return StreamingResponse(stream_response(prompt), media_type="text/plain")
