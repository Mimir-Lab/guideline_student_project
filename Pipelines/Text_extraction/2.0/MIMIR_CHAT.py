import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document


# Checking API
if not os.environ.get("GOOGLE_API_KEY"):
    raise EnvironmentError(
        "GOOGLE_API_KEY not set.\n"
        'Run in PowerShell:\n$env:GOOGLE_API_KEY=""' # Enter API KEY
    )


# Loading vector db
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004"
)

vector_db = Chroma(
    persist_directory="./mimir_db",
    embedding_function=embeddings,
)


# Loading LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)




# Creating manual RAG
def chat_with_mimir(question: str) -> None:
    print(f"\nSearching medical guidelines for: {question}\n")

    # 1. Retrieving documents
    docs = vector_db.similarity_search(question, k=3)

    if not docs:
        print("Mimir says:\nNo relevant guideline sections found.")
        return

    # 2. Building context manually
    context = "\n\n".join(
        f"[Source {i+1}]\n{doc.page_content}"
        for i, doc in enumerate(docs)
    )

    # 3. Building prompt
    prompt = f"""
You are Mimir, a medical guideline assistant.

Answer the question ONLY using the context below.
If the answer is not present, say:
"I could not find this in the provided guideline excerpts."

Context:
{context}

Question:
{question}

Answer:
""".strip()

    # 4. Asking the model
    response = llm.invoke(prompt)

    print("Mimir says:\n")
    print(response.content)

    # 5. Showing sources
    print("\nSources used:")
    for i, doc in enumerate(docs, start=1):
        print(f"  {i}. {doc.metadata.get('source', 'Guideline')}")


# CLI
if __name__ == "__main__":
    user_input = input("Ask Mimir a medical question: ").strip()
    if user_input:
        chat_with_mimir(user_input)
