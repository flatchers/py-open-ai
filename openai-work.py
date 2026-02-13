import json
import os
from decimal import getcontext, Decimal

from fastapi import FastAPI, Depends
from openai import AsyncOpenAI

from dotenv import load_dotenv
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database import get_db
from models import StorageModel, ChatSessionModel
from schemas import ChatSchema
from tokenizer import num_tokens_from_string

app = FastAPI()


load_dotenv()

OPENAI_SECRET_KEY = os.getenv("OPENAI_SECRET_KEY")

client = AsyncOpenAI(api_key=OPENAI_SECRET_KEY)


@app.post("/chat/start")
async def start_chat_session(async_db: AsyncSession = Depends(get_db)):
    new_chat = ChatSessionModel()
    async_db.add(new_chat)
    await async_db.commit()
    await async_db.refresh(new_chat)
    return new_chat


@app.post("/chat/prompt")
async def main_prompt(
        data: ChatSchema,
        async_db: AsyncSession = Depends(get_db)
):

    if data.request.lower() in {"exit", "quit"}:
        return {"message": "Session ended."}

    messages = [
        {
            "role": "system",
            "content": (
                "You are a strict assistant. Return **only valid JSON**. with key 'response'"
                "Return only STRING format "
                "Do not include any explanations, notes, headings, or Markdown blocks. "
                "The JSON must contain exactly what the user requests, no extra fields."
                "Example 1: {The Earth's rotation is gradually slowing down, "
                "resulting in the length of a day increasing by approximately 1.7 milliseconds per century.}"
                "Example 2: {name: Alice, age: 30}, {name: Bob, age: 25}, {name: Charlie, age: 35}]"
            )},
        {
            "role": "user",
            "content": data.request
        }
    ]

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    answer = response.choices[0].message.content
    try:
        new_data = json.loads(answer)
        new_storage = StorageModel(
            chat_session_id=data.session_id,
            request=data.request,
            response=str(new_data["response"])
        )
        async_db.add(new_storage)
        await async_db.commit()

        print("DATABASE STORAGE:", new_storage.chat_session_id, new_storage.request, new_storage.response)
        print("TOKEN LEN: ", num_tokens_from_string(new_storage.request) + num_tokens_from_string(new_storage.response))
        return {"ChatGPT": new_data}
    except json.JSONDecodeError:
        return {"error": "Response is not valid JSON", "raw_text": answer}


@app.post("/chat/history/{session_id}")
async def show_session_history(session_id: int, async_db: AsyncSession = Depends(get_db)):
    stmt = select(ChatSessionModel).options(joinedload(ChatSessionModel.storages)).where(ChatSessionModel.id == session_id)
    result = await async_db.execute(stmt)
    session = result.scalars().first()

    if session is None:
        return {"error": "Chat session not found"}
    request_price = 0.15
    response_price = 0.60
    getcontext().prec = 12
    price_for_a_request_token = Decimal(str(request_price / 1000000))
    price_for_a_response_token = Decimal(str(response_price / 100000))

    return {
        "requests": [storage.request for storage in session.storages],
        "response": [storage.response for storage in session.storages],
        "token_usage": sum(
            [num_tokens_from_string(storage.request) for storage in session.storages] +
            [num_tokens_from_string(storage.response) for storage in session.storages]
        ),
        "price": "$" + str(sum(
            [price_for_a_request_token * Decimal(num_tokens_from_string(storage.request)) for storage in session.storages] +
            [price_for_a_response_token * Decimal(num_tokens_from_string(storage.response)) for storage in session.storages]
        ))
    }
