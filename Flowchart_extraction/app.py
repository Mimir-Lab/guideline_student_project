import streamlit as st
import requests

st.set_page_config(page_title="Flowchart Bot", page_icon="🏥")

st.title("🏥 Medizinisches Entscheidungs-Tool")
st.markdown("Interaktiver Assistent basierend auf dem Kommunikations-Algorithmus.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("z.B. Was tun wenn RASS-Score >= -3?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call FastAPI Backend
    with st.chat_message("assistant"):
        try:
            # Note: Ensure the backend is running on port 8000
            response = requests.post(
                "http://localhost:8000/chat", 
                json={"message": prompt}
            )
            if response.status_code == 200:
                answer = response.json()["response"]
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error("Fehler bei der Kommunikation mit dem Server.")
        except Exception as e:
            st.error(f"Verbindungsfehler: {e}")

# Sidebar for Context
with st.sidebar:
    st.header("Über dieses Tool")
    st.info("Dieser Bot nutzt extrahierte Daten aus PDF-Flussdiagrammen, um klinische Entscheidungswege zu visualisieren.")
    if st.button("Verlauf löschen"):
        st.session_state.messages = []
        st.rerun()