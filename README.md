# FastAPI Chat Session Tracker
A simple backend on **FastAPI** for communicating with AI, storing chat history, counting tokens and request/response costs via Postgresql + SQLAlchemy (async).

## 📦 Project structure
py-open-ai/
+ openai-work.py # FastAPI endpoints
+ models.py # SQLAlchemy models
+ database.py # Async DB sessions
+ tokenizer.py # token counting
+ schemas.py # pydantic models
+ alembic/ # Alembic migrations
+ settings.py # Environment variables
+ requirements.txt
+ README.md
+ .env # Environment variables (hidden)
+ .gitignore # not visible on GitHub

```bash
git clone https://github.com/flatchers/py-open-ai.git

python -m venv .venv
source .venv/bin/activate   # Linux / Mac
.venv\Scripts\activate      # Windows

pip install -r requirements.txt

alembic upgrade head

uvicorn openai-work:app
