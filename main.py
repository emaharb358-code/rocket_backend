from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Rocket Backend is running!"}

class ChildProfile(BaseModel):
    name: str
    age: int
    grade: str
    interests: List[str]

class ChatRequest(BaseModel):
    session_id: str
    message: str
    mode: Optional[str] = "Explore"
    child: ChildProfile

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    return {
        "reply": [
            {
                "type": "text",
                "text": f"أهلاً {request.child.name}! وصلتي رسالتك: {request.message} 🚀"
            }
        ]
    }
