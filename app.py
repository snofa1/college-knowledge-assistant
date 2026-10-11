import requests
import streamlit as st

API_URL = "https://college-knowledge-assistant-g4hz.onrender.com"

st.set_page_config(
    page_title="PDF RAG Assistant",
    page_icon="📚",
    layout="centered"
)

st.title("📚 PDF RAG Assistant")
st.write("Upload a PDF and ask questions about its contents.")

# Store the current document ID
if "document_id" not in st.session_state:
    st.session_state.document_id = None

# -----------------------------
# PDF Upload
# -----------------------------

uploaded_file = st.file_uploader(
    "Upload your PDF",
    type=["pdf"]
)

if uploaded_file is not None:

    if st.button("Process PDF"):

        with st.spinner("Processing PDF..."):

            try:
                response = requests.post(
                    f"{API_URL}/documents/upload",
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf"
                        )
                    },
                    timeout=180

                )

                if response.status_code == 200:
                    data = response.json()

                    st.session_state.document_id = data["document_id"]

                    st.success(
                        f"PDF processed successfully! "
                        f"Created {data['chunk_count']} text chunks."
                    )

                else:
                    st.error(
                        f"Upload failed: {response.text}"
                    )

            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not connect to the FastAPI backend. "
                    "Make sure the FastAPI server is running."
                )

# -----------------------------
# Question Answering
# -----------------------------

if st.session_state.document_id:

    st.divider()

    question = st.text_input(
        "Ask a question about the PDF:"
    )

    if st.button("Get Answer"):

        if not question.strip():
            st.warning("Please enter a question.")

        else:

            with st.spinner("Searching and generating answer..."):

                try:
                    response = requests.post(
                        f"{API_URL}/chat",
                        json={
                            "document_id": st.session_state.document_id,
                            "question": question,
                            "top_k": 3
                        },
                        timeout=120
                    )

                    if response.status_code == 200:

                        data = response.json()

                        st.subheader("Answer")
                        st.write(data["answer"])

                        st.subheader("🔎 Sources")

                        for i, source in enumerate(
                            data["sources"],
                            start=1
                        ):
                            with st.expander(
                               f"Source {i} — Page {source['page']}"
                            ):
                               st.write(source["text"])

                    else:
                        st.error(
                            f"Request failed: {response.text}"
                        )

                except requests.exceptions.ConnectionError:
                    st.error(
                        "Could not connect to the FastAPI backend. "
                        "Make sure the FastAPI server is running."
                    )