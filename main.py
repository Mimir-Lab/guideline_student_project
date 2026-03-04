from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os
import json
import re
from typing import List

app = FastAPI()

# ✅ Load flowchart data safely
try:
    with open("structured_boxes.json", "r", encoding="utf-8") as f:
        FLOWCHART_DATA = json.load(f)
    print(f"✅ Loaded {len(FLOWCHART_DATA)} flowchart nodes")
except FileNotFoundError:
    print("⚠️ structured_boxes.json not found - using empty data")
    FLOWCHART_DATA = []
except Exception as e:
    print(f"❌ JSON error: {e}")
    FLOWCHART_DATA = []

# ✅ Get API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("⚠️ GROQ_API_KEY not set — /chat will return an error until configured.")

client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")


class ChatRequest(BaseModel):
    message: str


# 🧠 RAG Search - Find relevant flowchart content
def find_relevant_flowchart(query: str) -> List[str]:
    if not FLOWCHART_DATA:
        return ["Keine Flussdiagramm-Daten verfügbar."]
    
    query_words = [w for w in re.findall(r'\w+', query.lower()) if len(w) > 2]
    results = []

    for item in FLOWCHART_DATA:
        text_lower = item.get('text', '').lower()
        score = sum(word in text_lower for word in query_words)
        if score > 0:
            results.append((score, item['text']))

    results.sort(key=lambda x: x[0], reverse=True)
    return [text for _, text in results[:5]] or ["Keine direkte Übereinstimmung gefunden."]


@app.get("/")
async def root():
    return {
        "message": "✅ MIMIR Medical Backend + Flowchart RAG Running!",
        "nodes": len(FLOWCHART_DATA)
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "groq_key_set": bool(GROQ_API_KEY),
        "nodes": len(FLOWCHART_DATA)
    }


@app.post("/chat")
async def chat(request: ChatRequest):
    if not GROQ_API_KEY:
        return {"error": "Set GROQ_API_KEY environment variable"}
    
    # 🧩 STEP 1: RAG - Find contextual nodes
    context = find_relevant_flowchart(request.message)
    context_text = "\n".join(context) if context else "Keine direkte Übereinstimmung gefunden."
    
    # 🧠 STEP 2: Build AI prompt
    full_prompt = f"""
Du bist MIMIR, ein medizinisches Entscheidungstool basierend auf ICU-Flussdiagrammen.

**FLOWSCHART KONTEXT (relevant zu '{request.message}'):**
{context_text}

**USER FRAGE:** {request.message}

Antworte präzise basierend auf dem Flussdiagramm. Wenn kein direkter Kontext, sage: 
"Keine spezifische Empfehlung im Flowchart gefunden".
Antworte auf Deutsch, mit medizinischer Fachsprache.
"""

    # 🧠 STEP 3: Query the LLM
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Du bist MIMIR - präzise medizinische Entscheidungshilfe für Intensivmedizin."},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.1  # Deterministic medical answers
    )

    return {"reply": response.choices[0].message.content}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
