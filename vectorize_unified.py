import json
import shutil
from pathlib import Path
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings

CHUNK_DIR = Path("data/chunks")
DB_DIR = Path("./mimir_db")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def main():
    if DB_DIR.exists():
        shutil.rmtree(DB_DIR)

    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL, model_kwargs={"device": "cpu"})
    
    vector_db = Chroma(
        persist_directory=str(DB_DIR),
        embedding_function=embeddings,
        collection_name="mimir_chunks",
    )

    docs = []
    chunk_files = list(CHUNK_DIR.glob("*.json"))
    
    for cf in chunk_files:
        chunks = json.loads(cf.read_text(encoding="utf-8"))
        is_flow = "flowchart" in cf.name.lower()
        
        for text in chunks:
            docs.append(Document(
                page_content=text,
                metadata={"source": cf.stem, "type": "flowchart" if is_flow else "text"}
            ))

    vector_db.add_documents(docs)
    print(f"✅ Datenbank mit {len(docs)} Dokumenten (Text + Flowcharts) erstellt.")

if __name__ == "__main__":
    main()