# MIMIR: Medical Guideline RAG System 

MIMIR is a specialized Retrieval-Augmented Generation (RAG) system engineered to transform complex medical guideline PDFs into navigable, queryable intelligence. By combining high-fidelity markdown conversion with spatial coordinate-based flowchart extraction, MIMIR allows clinicians to interact with both prose text and clinical decision trees.

---

##  Key Features

* **Hybrid Extraction Pipeline:**
    * **Prose:** High-fidelity PDF-to-Markdown conversion using **Docling**.
    * **Flowcharts:** Advanced spatial extraction using **PyMuPDF (`fitz`)**. The system identifies logical nodes and conditional anchors (e.g., "JA", "NEIN", "Falls") based on their $(x, y)$ coordinates to reconstruct clinical decision paths.
* **Intelligent Chunking:** Implements sentence-safe, large-token chunking (≥1000 tokens) to ensure the LLM retains sufficient medical context for accurate reasoning.
* **Cost-Optimized Backend:** Configured to use **GPT-3.5 Turbo** (via OpenRouter/OpenAI) to provide a high-performance, cost-effective solution for medical institutions.
* **User Interface:** A clean, chat-based frontend built with **Streamlit** for real-time clinician interaction.

---

##  Tech Stack

* **Frontend:** Streamlit
* **Orchestration:** LangChain
* **Vector Database:** Chroma DB (Persistent)
* **Embeddings:** HuggingFace `all-MiniLM-L6-v2` (Running locally)
* **Primary LLM:** OpenAI GPT-3.5 Turbo

---

##  Contributors & Project History

> **Note on Repository History:** Due to a critical restructuring of the file system and the resolution of broken submodule links (mode 160000), the commit history was re-initialized during the final push. The old extraction logic was pushed by the following team members:

* **Tania:** : **Flowchart Extraction**. 
* **Vishnu:** : **Text Extraction**. 


---

##  Roadmap & Backlog

The following features are currently in the backlog for future development:
* **Enhanced Image Extraction:** Specialized extraction of medical diagrams with or without automated labeling.
* **Multimodal Logic:** Integration of Vision-LLMs to directly interpret complex flowchart images without textual flattening.

---

##  Setup & Installation

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/Mimir-Lab/guideline_student_project.git](https://github.com/Mimir-Lab/guideline_student_project.git)
    cd guideline_student_project
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Secrets:**
    Create a `.streamlit/secrets.toml` file in the root directory:
    ```toml
    OPENROUTER_API_KEY = "your_openai_or_openrouter_key_here"
    ```

4.  **Run the Pipeline:**
    To build the medical brain, you must run the processing scripts in this exact order:
    ```bash
    # Step 1: Extract Markdown and raw Flowchart data from PDFs
    python pdf_processor.py

    # Step 2: Process text into large (1000+ token) medical chunks
    python chunking_big.py

    # Step 3: Convert spatial flowchart coordinates into readable logic paths
    python flow_to_chunks.py

    # Step 4: Vectorize all prepared data into the Chroma DB
    python vectorize_unified.py
    ```

5.  **Launch the Assistant:**
    ```bash
    streamlit run app.py
    ```

---
*Disclaimer: MIMIR is an AI-assisted tool. All medical decisions should be verified against official clinical guidelines.*
