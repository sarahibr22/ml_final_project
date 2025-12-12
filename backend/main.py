# main.py
# Entry point for the backend React agent project


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.agent import agent_router
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# Allow all origins for development (change in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
