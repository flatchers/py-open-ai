import json
import os
from decimal import Decimal

from fastapi import Depends, APIRouter, HTTPException
from openai import AsyncOpenAI

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from app.db.session import get_db
from app.models.chat import StorageModel, ChatSessionModel
from app.schemas.chat import ChatSchema
from app.core.config import settings
from app.core.tokenizer import num_tokens_from_string


load_dotenv()

client = AsyncOpenAI(api_key=settings.OPENAI_SECRET_KEY)

router = APIRouter()


@router.post("/start")
async def start_chat_session(async_db: AsyncSession = Depends(get_db)):
    new_chat = ChatSessionModel()
    async_db.add(new_chat)
    await async_db.commit()
    await async_db.refresh(new_chat)
    return new_chat


@router.post("/prompt")
async def main_prompt(
        data: ChatSchema,
        async_db: AsyncSession = Depends(get_db)
):

    """
    Send user prompt to the LLM endpoint and return the model's response.
    """

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

        stmt = (
            select(ChatSessionModel)
            .options(joinedload(ChatSessionModel.storages))
            .where(ChatSessionModel.id == data.session_id)
        )

        result = await async_db.execute(stmt)
        session = result.scalars().first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chosen session doesn't exists.",
            )

        request_price = Decimal("0.15")
        response_price = Decimal("0.60")

        for storage in session.storages:
            if data.request == storage.request:
                request_price = Decimal("0.075")
            else:
                request_price = Decimal("0.15")

        new_data = json.loads(answer)
        new_storage = StorageModel(
            chat_session_id=data.session_id,
            request=data.request,
            response=str(new_data["response"])
        )
        async_db.add(new_storage)
        await async_db.commit()

        total_tokens = num_tokens_from_string(new_storage.request) + num_tokens_from_string(new_storage.response)
        session.total_tokens += total_tokens
        await async_db.flush()

        price_for_a_request_token = Decimal(str(request_price / 1000000))
        price_for_a_response_token = Decimal(str(response_price / 100000))
        total_price = (
            (
                    price_for_a_request_token * Decimal(num_tokens_from_string(new_storage.request))
            ) +
            (
                    price_for_a_response_token * Decimal(num_tokens_from_string(new_storage.response))
            )
        )
        session.total_price += total_price
        await async_db.commit()

        return {"ChatGPT": new_data}
    except json.JSONDecodeError:
        return {"error": "Response is not valid JSON", "raw_text": answer}


@router.get("/history/{session_id}")
async def show_session_history(session_id: int, async_db: AsyncSession = Depends(get_db)):
    stmt = (
        select(ChatSessionModel)
        .options(joinedload(ChatSessionModel.storages))
        .where(ChatSessionModel.id == session_id)
    )
    result = await async_db.execute(stmt)
    session = result.scalars().first()

    if session is None:
        return {"error": "Chat session not found"}

    return {
        "requests": [storage.request for storage in session.storages],
        "response": [storage.response for storage in session.storages],
        "token_usage": session.total_tokens,
        "price_database": session.total_price
    }
