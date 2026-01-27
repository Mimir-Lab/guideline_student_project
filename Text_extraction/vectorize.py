import os
import json
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

os.environ["GOOGLE_API_KEY"] = "AIzaSyCPpzz8OxHpvtORDJoBiqFfgCSVRrHmh0E"

try:
    with open("mimir_chunks.json", "r", encoding="utf-8") as f:
        chunk_texts = json.load(f)
except FileNotFoundError:
    print("Error: 'mimir_chunks.json' not found. Run chunking.py first!")
    exit()

documents = [Document(page_content=text, metadata={"source": "S3_Guideline_SJS_TEN"}) for text in chunk_texts]

embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

print("Starting vectorization... This may take a minute.")
vector_db = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    persist_directory="./mimir_db" 
)

print("Step 3 Complete: Your medical database is saved in the 'mimir_db' folder!")