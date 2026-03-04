import streamlit as st
import requests
import time

# Page config FIRST
st.set_page_config(page_title="🏥 MIMIR", page_icon="🩺", layout="wide")

# 🆕 COMPLETE FIXED CSS - PERFECT MIMIR UI
st.markdown("""
<style>
/* TEXT VISIBILITY - CRITICAL */
.stMarkdownContainer, div[data-testid="stMarkdownContainer"] {color: #1f2937 !important;}
.stMarkdownContainer p, .stMarkdownContainer li {color: #1f2937 !important;}

/* MEDICAL GRADIENT BACKGROUND */
.main {background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #00d4aa 100%);}

/* CHAT BUBBLES - BEAUTIFUL */
.stChatMessage {padding: 1.5rem !important; border-radius: 20px !important; margin: 1rem 0 !important;}

/* USER MESSAGES (RIGHT - PURPLE GRADIENT) */
div.stChatMessage:has(div[data-testid="stMarkdownContainer"] strong) {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    margin-left: 20% !important;
}

/* SIDEBAR GREEN SUCCESS BOX - WHITE TEXT */
section[data-testid="stSidebar"] .stSuccess {
    background-color: #16a34a22 !important;
    border: 1px solid #16a34a !important;
}
section[data-testid="stSidebar"] .stSuccess p {
    color: white !important;
    font-weight: 500 !important;
}

/* ASSISTANT MESSAGES (LEFT - WHITE CARD) */
div.stChatMessage:not(:has(div[data-testid="stMarkdownContainer"] strong)) {
    background: rgba(255,255,255,0.98) !important;
    border: 2px solid #00d4aa !important;
    color: #1f2937 !important;
}

/* INPUT + TITLES */
.stChatInput input {border-radius: 25px !important; border: 2px solid #00d4aa !important;}
h1 {color: white !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.3) !important;}

/* 🗑️ TRASH BUTTON - GREY WITH WHITE TEXT */
section[data-testid="stSidebar"] .stButton > button {
    color: white !important;
    background: linear-gradient(135deg, #ef4444, #dc2626) !important;
    border: 2px solid white !important;
    border-radius: 12px !important;
    padding: 0.8rem 1.2rem !important;
    font-weight: 700 !important;
    font-size: 16px !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg, #dc2626, #b91c1c) !important;
}
section[data-testid="stSidebar"] .stButton > button span {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# MAIN TITLE
st.title("🏥 **MIMIR - Medizinisches Entscheidungs Tool**")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "👋 MIMIR bereit! Frage nach RASS-Score, Beatmung etc."}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("z.B. 'Was tun bei RASS-Score >= -3?'"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): 
        st.markdown(prompt)
    
    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("🧠 Analysiere Flowchart..."):
            try:
                response = requests.post("http://localhost:8001/chat", json={"message": prompt}, timeout=30)
                if response.status_code == 200:
                    answer = response.json().get("reply") or str(response.json())
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"❌ Backend Fehler: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Backend nicht erreichbar: {e}")

# SIDEBAR
with st.sidebar:
    # White header
    st.markdown("🩺 **<span style='color: white; font-size: 1.4em; font-weight: 700;'>MIMIR Info</span>**", unsafe_allow_html=True)
    
    # Green success box
    st.success("• RASS-Score Entscheidungen\n• PDF-Flussdiagramm Logik")
    
    # Clear chat button
    if st.button("🗑️ **Chat löschen**"): 
        st.session_state.messages = []
        st.rerun()
