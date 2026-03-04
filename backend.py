from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

# GROQ client (FREE)
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"message": "Groq FastAPI Server Running!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "groq_key_set": bool(os.getenv('GROQ_API_KEY'))}

@app.post("/chat")
async def chat(request: ChatRequest):
    if not os.getenv("GROQ_API_KEY"):
        return {"error": "Set GROQ_API_KEY environment variable"}
    
    response = client.chat.completions.create(
        model="llama3.1-8b-instant",  # FREE Groq model
        messages=[{"role": "user", "content": request.message}]
    )
    return {"reply": response.choices[0].message.content}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
