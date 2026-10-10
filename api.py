from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from rag_service import process_document, ask_question


app = FastAPI(
    title="College Knowledge Assistant API",
    description="RAG-based PDF question answering backend",
    version="1.0.0"
)


# ==========================================
# 1. HOME
# ==========================================

@app.get("/")
def home():

    return {
        "message": "College Knowledge Assistant API is running"
    }


# ==========================================
# 2. HEALTH CHECK
# ==========================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ==========================================
# 3. UPLOAD PDF
# ==========================================

@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    try:

        result = process_document(
            file.file,
            file.filename
        )

        return result

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ==========================================
# 4. QUESTION REQUEST
# ==========================================

class ChatRequest(BaseModel):

    document_id: str
    question: str
    top_k: int = 3


# ==========================================
# 5. ASK QUESTION
# ==========================================

@app.post("/chat")
def chat(request: ChatRequest):

    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:

        result = ask_question(
            request.document_id,
            request.question,
            request.top_k
        )

        return result

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )