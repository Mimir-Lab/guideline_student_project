import json
import shutil
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings

CHUNK_DIR = Path("data/chunks")
DB_DIR = Path("./mimir_db")

# Choose ONE and keep it forever for this DB:
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# EMBED_MODEL = "BAAI/bge-base-en-v1.5"

REBUILD_DB = True  # set False later when you want incremental updates


def wipe_db():
    if DB_DIR.exists():
        shutil.rmtree(DB_DIR)


def get_embedding_dim(emb):
    return len(emb.embed_query("dimension check"))


def main():
    if REBUILD_DB:
        wipe_db()

    chunk_files = sorted(CHUNK_DIR.glob("*.chunks.json"))
    if not chunk_files:
        raise FileNotFoundError(f"No chunk files found in: {CHUNK_DIR.resolve()}")

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs={"device": "cpu"},
    )

    dim = get_embedding_dim(embeddings)
    print(f"Using LOCAL embeddings: {EMBED_MODEL} (dim={dim})")

    vector_db = Chroma(
        persist_directory=str(DB_DIR),
        embedding_function=embeddings,
        collection_name="mimir_chunks",
    )

    docs = []
    ids = []

    for cf in chunk_files:
        source_name = cf.stem.replace(".chunks", "")
        chunks = json.loads(cf.read_text(encoding="utf-8"))

        for i, text in enumerate(chunks):
            docs.append(
                Document(
                    page_content=text,
                    metadata={"source": source_name, "chunk_id": i},
                )
            )
            ids.append(f"{source_name}::chunk_{i}")

    print(f"Adding {len(docs)} chunks to Chroma...")
    vector_db.add_documents(documents=docs, ids=ids)

    print(f"✅ Done. DB saved at: {DB_DIR.resolve()}")


if __name__ == "__main__":
    main()
