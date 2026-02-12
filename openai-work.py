import json
import os

from fastapi import FastAPI, Depends
from openai import OpenAI

from dotenv import load_dotenv
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Storage
from schemas import ChatResponse

app = FastAPI()


load_dotenv()

OPENAI_SECRET_KEY = os.getenv("OPENAI_SECRET_KEY")

client = OpenAI(api_key=OPENAI_SECRET_KEY)


@app.post("/chat/start/", response_model=ChatResponse)
async def start_chat_session(async_db: AsyncSession = Depends(get_db)):
    new_chat = Storage(request="", response="")
    async_db.add(new_chat)
    await async_db.commit()
    await async_db.refresh(new_chat)
    return new_chat


# @app.post("chat/prompt")
# def main_prompt(prompt: Prompt):
#
#     if prompt.request.lower() in {"exit", "quit"}:
#         return {"message": "Session ended."}
#
#     messages = [
#         {
#             "role": "system",
#             "content": (
#                 "You are a strict assistant. Return **only valid JSON**. "
#                 "Do not include any explanations, notes, headings, or Markdown blocks. "
#                 "The JSON must contain exactly what the user requests, no extra fields."
#                 "Example: {ChatGPT: {The Earth's rotation is gradually slowing down, "
#                 "resulting in the length of a day increasing by approximately 1.7 milliseconds per century.}"
#             )},
#         {
#             "role": "user",
#             "content": prompt.request
#         }
#     ]
#
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=messages
#     )
#     answer = response.choices[0].message.content
#     try:
#         data = json.loads(answer)
#         return {"ChatGPT": data}
#     except json.JSONDecodeError:
#         return {"error": "Response is not valid JSON", "raw_text": answer}
