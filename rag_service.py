import os
import time
from uuid import uuid4

import faiss
from dotenv import load_dotenv
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from google import genai
from google.genai import errors


# ==========================================
# 1. LOAD GEMINI API KEY
# ==========================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found. "
        "Please add it to your .env file."
    )

client = genai.Client(api_key=api_key)


# ==========================================
# 2. LOAD EMBEDDING MODEL
# ==========================================

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ==========================================
# 3. TEMPORARY DOCUMENT STORAGE
# ==========================================

documents = {}


# ==========================================
# 4. EXTRACT TEXT FROM PDF
# ==========================================

def extract_pages_from_pdf(file):

    reader = PdfReader(file)

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        page_text = page.extract_text()

        if page_text and page_text.strip():

            pages.append({
                "page": page_number,
                "text": page_text
            })

    return pages


# ==========================================
# 5. CREATE TEXT CHUNKS
# ==========================================

def create_chunks(pages, chunk_size=800, overlap=100):
    chunks = []

    for page_data in pages:
        text = page_data["text"].strip()
        page_number = page_data["page"]

        # Split text into sentences
        sentences = text.replace("\n", " ").split(". ")

        current_chunk = ""

        for sentence in sentences:
            sentence = sentence.strip()

            if not sentence:
                continue

            # Add the period back if it was removed by split
            if not sentence.endswith("."):
                sentence += "."

            # Check whether adding the next sentence exceeds the chunk size
            if (
                len(current_chunk) + len(sentence) + 1
                <= chunk_size
            ):
                current_chunk += (
                    sentence + " "
                )

            else:
                if current_chunk.strip():
                    chunks.append({
                        "text": current_chunk.strip(),
                        "page": page_number
                    })

                # Start a new chunk
                current_chunk = sentence + " "

        # Add remaining text
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "page": page_number
            })

    return chunks

# ==========================================
# 6. CREATE FAISS VECTOR INDEX
# ==========================================

def create_vector_database(chunks):

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = embedding_model.encode(
        texts,
        convert_to_numpy=True
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    return index


# ==========================================
# 7. PROCESS PDF
# ==========================================

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

    index = create_vector_database(chunks)

    document_id = str(uuid4())

    documents[document_id] = {
        "filename": filename,
        "chunks": chunks,
        "index": index
    }

    return {
        "document_id": document_id,
        "filename": filename,
        "chunk_count": len(chunks)
    }


# ==========================================
# 8. RETRIEVE RELEVANT CHUNKS
# ==========================================

def retrieve_chunks(
    question,
    chunks,
    index,
    top_k=3
):

    question_embedding = embedding_model.encode(
        [question],
        convert_to_numpy=True
    )

    distances, indices = index.search(
        question_embedding,
        min(top_k, len(chunks))
    )

    retrieved_chunks = []

    for index_number in indices[0]:

        if index_number >= 0:

            retrieved_chunks.append(
                chunks[index_number]
            )

    return retrieved_chunks


# ==========================================
# 9. GENERATE ANSWER USING GEMINI
# ==========================================

def generate_answer(
    question,
    retrieved_chunks
):

    context = "\n\n".join(
        chunk["text"]
        for chunk in retrieved_chunks
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


# ==========================================
# 10. ASK QUESTION ABOUT DOCUMENT
# ==========================================

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

    chunks = document["chunks"]
    index = document["index"]

    retrieved_chunks = retrieve_chunks(
        question,
        chunks,
        index,
        top_k
    )

    answer = generate_answer(
        question,
        retrieved_chunks
    )

    sources = []

    for chunk in retrieved_chunks:

        sources.append({
            "page": chunk["page"],
            "text": chunk["text"]
        })

    return {
        "answer": answer,
        "sources": sources
    }