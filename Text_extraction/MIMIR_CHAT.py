import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.chains import RetrievalQA

# 1. SETUP API KEY
os.environ["GOOGLE_API_KEY"] = "AIzaSyCPpzz8OxHpvtORDJoBiqFfgCSVRrHmh0E"

# 2. LOAD THE BRAIN (The folder you created in Step 3)
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
vector_db = Chroma(persist_directory="./mimir_db", embedding_function=embeddings)

# 3. SETUP THE AI
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

# 4. SETUP THE RETRIEVAL SYSTEM
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_db.as_retriever(search_kwargs={"k": 3}), # Looks at top 3 medical chunks
    return_source_documents=True
)

def chat_with_mimir(query):
    print(f"\nSearching medical guidelines for: {query}...")
    result = qa_chain.invoke({"query": query})
    
    answer = result["result"]
    print(f"\nMimir says: {answer}")
    
    # Optional: Print where the info came from
    if result["source_documents"]:
        source = result["source_documents"][0].metadata
        print(f"\n[Source Cited]: {source.get('Header 1', 'Medical Guideline')}")

# 5. START CHATTING
if __name__ == "__main__":
    user_input = input("Ask Mimir a medical question: ")
    chat_with_mimir(user_input)