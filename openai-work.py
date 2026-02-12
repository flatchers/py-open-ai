import os
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()


OPENAI_SECRET_KEY = os.getenv("OPENAI_SECRET_KEY")

client = OpenAI(api_key=OPENAI_SECRET_KEY)

while True:

    user_input = input("You: ")
    if user_input.lower() in {"exit", "quit"}:
        break

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_input}]
    )

    print("ChatGPT:", response.choices[0].message.content)
