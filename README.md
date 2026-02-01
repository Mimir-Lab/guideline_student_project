# MIMIR: Medical Guideline RAG System

MIMIR is a Retrieval-Augmented Generation (RAG) system specifically designed for processing and querying medical guideline documents. It utilizes a sophisticated pipeline to convert PDFs into searchable logic paths.

## Key Features
* **PDF-to-Markdown:** Uses Docling for high-fidelity conversion.
* **Intelligent Chunking:** Sentence-safe chunking (≥1000 tokens) for better context retention.
* **Flowchart Extraction:** Uses `PyMuPDF` to extract text blocks based on their spatial coordinates within the document. And then identifies conditional keywords (e.g., "JA", "NEIN", "Falls") to link extracted text boxes into a logical sequence. 
* **Flexible Backend:** Supports OpenAI (GPT-3.5 Turbo) and other evaluation modes.

## Tech Stack
* **UI:** Streamlit
* **Orchestration:** LangChain
* **Vector Store:** Chroma DB
* **Embeddings:** HuggingFace (`all-MiniLM-L6-v2`)

## Setup
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Add your credentials to `.streamlit/secrets.toml`:
   ```toml
   OPENAI_API_KEY = "your_key_here"
