from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent import ask_agent

app = FastAPI()


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {"message": "Drive AI Agent Running"}


@app.post("/chat")
def chat(request: ChatRequest):

    try:
        result = ask_agent(request.message)
        return result
    except Exception as exc:
        # Avoid returning non-JSON responses that break the Streamlit client.
        raise HTTPException(status_code=500, detail=str(exc))