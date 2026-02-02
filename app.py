import streamlit as st
import requests
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# --- CONFIGORATION ---
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DB_DIR = "./mimir_db"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

st.set_page_config(page_title="MIMIR AI", page_icon="🏥")
st.title("🏥 MIMIR: Unified Medical Assistant")


API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")

@st.cache_resource
def get_db():
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    return Chroma(persist_directory=DB_DIR, embedding_function=embeddings, collection_name="mimir_chunks")

# Initializing database
try:
    db = get_db()
except Exception as e:
    st.error(f"Database could not be loaded. Did you run 'vectorize_unified.py'? Error: {e}")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# View chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Frage zu Leitlinien oder Flowcharts..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)


    results = db.similarity_search(prompt, k=5)
    
    context = ""
    for d in results:
        type_label = "🚨 DECISION-MAKING ALGORITHM" if d.metadata.get('type') == 'flowchart' else "📄 TEXT"
        context += f"\n--- {type_label} ---\n{d.page_content}\n"

    system_prompt = (
        "Du bist ein medizinischer Assistent. Antworte STRENG nur nach den bereitgestellten Informationen. "
        "Wenn ein 'ENTSCHEIDUNGS-ALGORITHMUS' vorhanden ist, folge seinen Schritten exakt."
    )

    # API Call
    with st.chat_message("assistant"):
        try:
            res = requests.post(
                OPENROUTER_URL,
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={
                    "model": "openai/gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": f"{system_prompt}\n\nKONTEXT:\n{context}"},
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            ans = res.json()['choices'][0]['message']['content']
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
        except Exception as e:
            st.error(f"API query error: {e}")