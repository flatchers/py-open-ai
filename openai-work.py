import json
import os

from fastapi import FastAPI
from openai import OpenAI

from dotenv import load_dotenv

app = FastAPI()


load_dotenv()

OPENAI_SECRET_KEY = os.getenv("OPENAI_SECRET_KEY")

client = OpenAI(api_key=OPENAI_SECRET_KEY)


@app.get("/")
def root(request: str):
    if request.lower() in {"exit", "quit"}:
        return {"message": "Session ended."}

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": request}]
    )
    answer = response.choices[0].message.content
    return {"ChatGPT": answer}


# while True:
#
#     user_input = input("You: ")
#     if user_input.lower() in {"exit", "quit"}:
#         break
#
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[{"role": "user", "content": user_input}]
#     )
#
#     print("ChatGPT:", response.choices[0].message.content)
