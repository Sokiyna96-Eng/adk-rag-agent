import streamlit as st
import requests
from typing import List
import datetime

# ----------------------- CONFIG ----------------------- #
API_URL = "http://rag_api_backend:8000"
UPLOAD_ENDPOINT = f"{API_URL}/upload_pdf"
QUERY_ENDPOINT = f"{API_URL}/query"

# --------------------- PAGE SETUP --------------------- #
st.set_page_config(
    page_title="RAG Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("RAG PDF Assistant")
st.markdown("Ask questions about your uploaded documents.")

# ------------------ SESSION STATE INIT ---------------- #
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

# --------------------- SIDEBAR ------------------------ #
st.sidebar.header("📎 Upload PDFs")

uploaded_files = st.sidebar.file_uploader(
    "Upload PDFs (multiple supported)",
    type=["pdf"],
    accept_multiple_files=True
)

if st.sidebar.button("Upload to Corpus") and uploaded_files:
    with st.spinner("Uploading files to backend..."):
        for file in uploaded_files:
            files = {"file": file}
            data = {"corpus_name": "earthwork"}
            res = requests.post(UPLOAD_ENDPOINT, files=files, data=data)
            if res.status_code == 200:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.uploaded_files.append({
                    "name": file.name,
                    "status": "Uploaded",
                    "timestamp": timestamp
                })
            else:
                st.session_state.uploaded_files.append({
                    "name": file.name,
                    "status": "Failed",
                    "timestamp": "--"
                })

# Display uploaded file summary
if st.session_state.uploaded_files:
    st.sidebar.subheader("Upload Summary")
    for file in st.session_state.uploaded_files:
        st.sidebar.markdown(f"**{file['name']}** — {file['status']} ({file['timestamp']})")

# Clear chat
if st.sidebar.button("🧹 Clear Chat History"):
    st.session_state.messages.clear()
    st.success("Chat history cleared.")

# ------------------ CHAT DISPLAY ---------------------- #
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander("📎 Sources", expanded=False):
                for src in msg["sources"]:
                    gcs_url = f"https://console.cloud.google.com/storage/browser/{src['source_uri'].replace('gs://', '').split('/')[0]}"
                    score = round(src.get("score", 0), 3)
                    st.markdown(f"- 📎 `{src['source_name']}` (score: {score}) — [View in GCS]({gcs_url})")

# --------------------- CHAT INPUT --------------------- #
if prompt := st.chat_input("Ask something about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                res = requests.post(QUERY_ENDPOINT, data={"query": prompt, "corpus_name": "earthwork"})
                if res.status_code == 200:
                    result = res.json()
                    sources: List[dict] = result.get("results", [])
                    answer = result.get("answer") or sources[0].get("text", "No answer.") if sources else "No answer found."

                    feedback = "" if sources else "\n\n *No strong match found — try rephrasing?*"
                    answer += feedback

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                    st.markdown(answer)
                else:
                    st.error("Query failed")
            except Exception as e:
                st.error(f"Error: {e}")
