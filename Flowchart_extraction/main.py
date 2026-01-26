import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI(title="Medical Flowchart API")

# Configure Gemini
API_KEY = "YOUR_GEMINI_API_KEY"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Load the "Knowledge Base" (the JSON you extracted in your notebook)
def load_knowledge_base():
    with open("structured_boxes.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    # Convert to a text representation for the prompt context
    kb_text = "\n".join([f"- {item['text']} (Type: {item['type']})" for item in data])
    return kb_text

KNOWLEDGE_BASE = load_knowledge_base()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    prompt = f"""
    DU BIST EIN MEDIZINISCHER ASSISTENT. ANTWORT NUR BASIEREND AUF DER WISSENSBASIS.
    
    WISSENSBASIS:
    {KNOWLEDGE_BASE}

    ANWEISUNG:
    1. Suche den Startpunkt ("Patient beatmet?").
    2. Folge den Pfaden (Falls JA / Falls NEIN).
    3. Wenn die Antwort NICHT in der Wissensbasis steht, sag: "Dazu enthält das Flussdiagramm keine Informationen."
    4. Antworte kurz, präzise und professionell auf Deutsch.

    NUTZERFRAGE: {request.message}
    """
    try:
        response = model.generate_content(prompt)
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)