import os
import time
from uuid import uuid4

from dotenv import load_dotenv
from pypdf import PdfReader
from google import genai
from google.genai import errors

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.embeddings import Embeddings
from google.genai import types
from langchain_community.vectorstores import FAISS


load_dotenv()

# -----------------------------
# Gemini Configuration
# -----------------------------

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found. "
        "Please add it to your .env file."
    )

client = genai.Client(api_key=api_key)

# -----------------------------
# Embedding Model
# -----------------------------

class GeminiEmbeddings(Embeddings):

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors = []

        for text in texts:
            response = client.models.embed_content(
                model="gemini-embedding-001",
                contents=text,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT"
                )
            )

            vectors.append(response.embeddings[0].values)

        return vectors

    def embed_query(self, text: str) -> list[float]:
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY"
            )
        )

        return response.embeddings[0].values


# Initialize Gemini embeddings
embedding_model = GeminiEmbeddings()


def get_embedding_model():
    return embedding_model

# -----------------------------
# Document Storage
# -----------------------------

documents = {}


# -----------------------------
# PDF Extraction
# -----------------------------

def extract_pages_from_pdf(file):
    reader = PdfReader(file)

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):
        page_text = page.extract_text()

        if page_text and page_text.strip():
            pages.append(
                Document(
                    page_content=page_text.strip(),
                    metadata={
                        "page": page_number
                    }
                )
            )

    return pages


# -----------------------------
# LangChain Text Splitting
# -----------------------------

def create_chunks(pages):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    chunks = text_splitter.split_documents(pages)

    return chunks


# -----------------------------
# Create FAISS Vector Store
# -----------------------------

def create_vector_database(chunks):
    vector_store = FAISS.from_documents(
        chunks,
        get_embedding_model()
    )

    return vector_store


# -----------------------------
# Process PDF
# -----------------------------

def process_document(file, filename):

    pages = extract_pages_from_pdf(file)

    if not pages:
        raise ValueError(
            "No readable text was found in this PDF."
        )

    chunks = create_chunks(pages)

    if not chunks:
        raise ValueError(
            "Could not create text chunks from this PDF."
        )

    vector_store = create_vector_database(chunks)

    document_id = str(uuid4())

    documents[document_id] = {
        "filename": filename,
        "chunks": chunks,
        "vector_store": vector_store
    }

    return {
        "document_id": document_id,
        "filename": filename,
        "chunk_count": len(chunks)
    }


# -----------------------------
# Retrieve Relevant Chunks
# -----------------------------

def retrieve_chunks(
    question,
    vector_store,
    top_k=3
):

    retrieved_documents = vector_store.similarity_search(
        question,
        k=top_k
    )

    return retrieved_documents


# -----------------------------
# Gemini Answer Generation
# -----------------------------

def generate_answer(
    question,
    retrieved_chunks
):

    context = "\n\n".join(
        document.page_content
        for document in retrieved_chunks
    )

    prompt = f"""
Answer the question using ONLY the context below.

If the answer is not present in the context, say:

"I could not find the answer in the provided PDF."

Context:
{context}

Question:
{question}
"""

    max_attempts = 3

    for attempt in range(max_attempts):

        try:

            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt
            )

            return response.text

        except errors.ServerError:

            if attempt < max_attempts - 1:

                wait_time = 2 ** attempt

                time.sleep(wait_time)

            else:

                return (
                    "Gemini is temporarily unavailable. "
                    "Please try again in a few seconds."
                )


# -----------------------------
# Question Answering
# -----------------------------

def ask_question(
    document_id,
    question,
    top_k=3
):

    if document_id not in documents:

        raise ValueError(
            "Document not found."
        )

    document = documents[document_id]

    vector_store = document["vector_store"]

    retrieved_chunks = retrieve_chunks(
        question,
        vector_store,
        top_k
    )

    answer = generate_answer(
        question,
        retrieved_chunks
    )

    sources = []

    for chunk in retrieved_chunks:

        sources.append(
            {
                "page": chunk.metadata.get(
                    "page",
                    "Unknown"
                ),
                "text": chunk.page_content
            }
        )

    return {
        "answer": answer,
        "sources": sources
    }