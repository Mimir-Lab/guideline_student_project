import os
import json
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# 1. SET YOUR API KEY
os.environ["GOOGLE_API_KEY"] = "AIzaSyCPpzz8OxHpvtORDJoBiqFfgCSVRrHmh0E"

# 2. LOAD YOUR CHUNKS
try:
    with open("mimir_chunks.json", "r", encoding="utf-8") as f:
        chunk_texts = json.load(f)
except FileNotFoundError:
    print("Error: 'mimir_chunks.json' not found. Run chunking.py first!")
    exit()

# 3. CONVERT TEXT TO 'DOCUMENTS'
# The database needs a specific format called 'Document'
documents = [Document(page_content=text, metadata={"source": "S3_Guideline_SJS_TEN"}) for text in chunk_texts]

# 4. CHOOSE EMBEDDING MODEL
# We use Google's 'text-embedding-004' because it is multilingual (German/English)
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# 5. CREATE AND SAVE THE DATABASE
print("Starting vectorization... This may take a minute.")
vector_db = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    persist_directory="./mimir_db" # This creates a folder on your desktop
)

print("Step 3 Complete: Your medical database is saved in the 'mimir_db' folder!")