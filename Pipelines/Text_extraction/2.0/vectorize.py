import os
import json
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

 # 1. Checking API
# if not os.environ.get("AIzaSyAWyCQYqJZ1ZIOXdsAMH5uucTfNypngf4w"):
#     raise EnvironmentError(
#         "GOOGLE_API_KEY not set. Export it before running."
#      )

# 2. LOAD CHUNKS
try:
    with open("mimir_chunks.json", "r", encoding="utf-8") as f:
        chunk_texts = json.load(f)
except FileNotFoundError:
    raise FileNotFoundError(
        "mimir_chunks.json not found. Run Chunking_main.py first."
    )

# 3. CREATE DOCUMENT OBJECTS
documents = [
    Document(
        page_content=text,
        metadata={"source": "S3_Analgesie_Sedierung_Delir"}
    )
    for text in chunk_texts
]

# 4. EMBEDDING MODEL
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004"
)

# 5. VECTOR DATABASE
print("Starting vectorization...")
vector_db = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    persist_directory="./mimir_db"
)

vector_db.persist()
print("Step 3 Complete: Vector database saved to ./mimir_db")
