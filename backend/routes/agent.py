from fastapi import APIRouter
from llm.get_response import get_response
from .chat_stream import chat_stream_router
from .ocr import ocr_router

agent_router = APIRouter()

@agent_router.get("/agent")
def agent_endpoint(prompt: str):
    return {"response": get_response(prompt)}

agent_router.include_router(chat_stream_router)
agent_router.include_router(ocr_router)
