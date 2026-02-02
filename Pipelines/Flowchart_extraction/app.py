# Web app framework for building the UI
import streamlit as st
import requests

# Configure the page (browser tab title + emoji icon)
st.set_page_config(page_title="Flowchart Bot", page_icon="🏥")

# Main title shown at the top of the app
st.title("🏥 MIMIR - Medizinisches Entscheidungs Tool")

# Streamlit reruns the script on every interaction, so we store messages in session_state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Loop through stored messages so the chat history stays visible
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("z.B. Was tun wenn RASS-Score >= -3?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
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

with st.sidebar:
    st.header("Über dieses Tool")
    st.info("Dieser Bot nutzt extrahierte Daten aus PDF-Flussdiagrammen, um klinische Entscheidungswege zu visualisieren.")
    if st.button("Verlauf löschen"):
        st.session_state.messages = []
        st.rerun()
