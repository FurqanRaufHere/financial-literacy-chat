# src/api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.prompts import get_system_prompt, list_personas
from src.llm_client import LLMClient
from src.utils import start_history, append_user, append_assistant

# FastAPI creates the app object — think of it like Flask's app = Flask(__name__)
app = FastAPI(title="Personal Finance Chatbot API")

# Pydantic model = a data shape FastAPI validates automatically
# If a request is missing "message", FastAPI returns a 422 error automatically
class ChatRequest(BaseModel):
    persona: str = "professional"   # default persona
    message: str

class ChatResponse(BaseModel):
    reply: str
    persona: str

# LLMClient is initialized once when the server starts (not on every request)
client = LLMClient()

@app.get("/")
def root():
    return {"status": "ok", "personas": list_personas()}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # Validate persona exists — get_system_prompt raises ValueError if not
    try:
        system_prompt = get_system_prompt(req.persona)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Build message history and call the LLM
    history = start_history(system_prompt)
    append_user(history, req.message)
    reply = client.chat(history)

    return ChatResponse(reply=reply, persona=req.persona)