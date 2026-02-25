from fastapi import FastAPI

from app.routes.ai import router

api = FastAPI(title="Chat with LLM")


prefix_path = "/api/v1"

api.include_router(router, prefix=f"{prefix_path}/chat")
