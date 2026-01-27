import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.chains import RetrievalQA


os.environ["GOOGLE_API_KEY"] = "" #Enter API key

embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
vector_db = Chroma(persist_directory="./mimir_db", embedding_function=embeddings)

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_db.as_retriever(search_kwargs={"k": 3}), 
    return_source_documents=True
)

def chat_with_mimir(query):
    print(f"\nSearching medical guidelines for: {query}...")
    result = qa_chain.invoke({"query": query})
    
    answer = result["result"]
    print(f"\nMimir says: {answer}")
    

    if result["source_documents"]:
        source = result["source_documents"][0].metadata
        print(f"\n[Source Cited]: {source.get('Header 1', 'Medical Guideline')}")

if __name__ == "__main__":
    user_input = input("Ask Mimir a medical question: ")
    chat_with_mimir(user_input)