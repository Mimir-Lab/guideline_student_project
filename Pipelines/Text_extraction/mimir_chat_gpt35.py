import os
import json
import requests
from pathlib import Path
from typing import List, Dict

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings



# Local embeddings (FREE)
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Vector DB
DB_DIR = Path("./mimir_db")
COLLECTION_NAME = "mimir_chunks"

# Document-level context
DOC_CONTEXT_FILE = Path("data/doc_context.json")

# Retrieval
TOP_K = 4  # keep small to control token usage

# OpenAI (GPT-3.5-Turbo)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "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")
OPENAI_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENAI_MODEL = "openai/gpt-3.5-turbo"


# =========================================


def load_vectordb():
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs={"device": "cpu"},
    )

    return Chroma(
        persist_directory=str(DB_DIR),
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
    )


def load_doc_contexts():
    if DOC_CONTEXT_FILE.exists():
        return json.loads(DOC_CONTEXT_FILE.read_text(encoding="utf-8"))
    return {}


def format_context(docs, doc_contexts):
    # Unique sources
    sources = []
    for d in docs:
        s = d.metadata.get("source", "unknown")
        if s not in sources:
            sources.append(s)

    # Document-level context
    doc_ctx = "\n\n".join(
        f"[DOCUMENT CONTEXT: {s}]\n{doc_contexts.get(s, '')}"
        for s in sources
    )

    # Chunk-level context
    chunk_ctx = "\n\n---\n\n".join(
        f"[SOURCE: {d.metadata['source']} | chunk_{d.metadata['chunk_id']}]\n{d.page_content}"
        for d in docs
    )

    return doc_ctx + "\n\n---\n\n" + chunk_ctx


def call_openai(messages):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "MIMIR-RAG",
    }

    payload = {
        "model": OPENAI_MODEL,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 400,
    }

    r = requests.post(OPENAI_CHAT_URL, headers=headers, json=payload, timeout=120)

    if r.status_code != 200:
        raise RuntimeError(f"OpenRouter error {r.status_code}: {r.text}")

    return r.json()["choices"][0]["message"]["content"]



def main():
    if not DB_DIR.exists():
        raise FileNotFoundError(
            f"Vector DB not found at {DB_DIR.resolve()}. "
            "Run vectorize_local.py first."
        )

    vectordb = load_vectordb()
    doc_contexts = load_doc_contexts()

    print("\nMIMIR — GPT-3.5-Turbo (RAG, terminal)")
    print(f"DB: {DB_DIR.resolve()}")
    print(f"Model: {OPENAI_MODEL}")
    print("Type 'exit' to quit\n")

    while True:
        question = input("You: ").strip()
        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break

        # Retrieve
        docs = vectordb.similarity_search(question, k=TOP_K)

        # Build context
        context = format_context(docs, doc_contexts)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are MIMIR, a medical guideline assistant. "
                    "Use ONLY the provided context to answer. "
                    "If the answer is not present, say: "
                    "'I cannot find this in the provided documents.' "
                    "Do not invent information."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"CONTEXT:\n{context}\n\n"
                    f"QUESTION:\n{question}\n\n"
                    "Answer briefly, then list sources."
                ),
            },
        ]

        try:
            answer = call_openai(messages)
        except Exception as e:
            print("\n❌ Generation failed:")
            print(e, "\n")
            continue

        print("\nMIMIR:\n" + answer.strip() + "\n")


if __name__ == "__main__":
    main()
