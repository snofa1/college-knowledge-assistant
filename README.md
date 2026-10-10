# College Knowledge Assistant — RAG-Based PDF Question Answering

A Retrieval-Augmented Generation (RAG) application that allows users to ask questions about college documents in natural language and receive answers grounded in the content of uploaded PDFs.

Built using **Python, LangChain, FastAPI, Streamlit, FAISS, Sentence Transformers, and Google Gemini**.

## Overview

College documents often contain important information about attendance requirements, examinations, assignments, and institutional policies. Finding specific details in lengthy PDFs can be time-consuming.

The College Knowledge Assistant simplifies this process by extracting text from PDF documents, splitting it into smaller chunks, retrieving relevant passages using semantic similarity search, and using Google Gemini to generate context-aware answers.

## Key Features

- **PDF-based question answering:** Ask questions about uploaded PDF documents in natural language.
- **Retrieval-Augmented Generation (RAG):** Retrieve relevant document passages before generating answers.
- **LangChain integration:** Use document objects, text splitting, embedding integration, and vector store functionality.
- **Semantic search:** Generate text embeddings with Sentence Transformers and retrieve similar passages using FAISS.
- **Context-grounded responses:** Instruct the language model to answer using the retrieved document context.
- **Source references:** Display relevant source passages and page metadata alongside answers.
- **Separate frontend and backend:** Streamlit provides the user interface, while FastAPI exposes the question-answering API.
- **API key protection:** Load the Gemini API key from an environment variable rather than hardcoding it in application code.

   Architecture


             User
              |
              v
      Streamlit Frontend
           (app.py)
              |
              v
       FastAPI Backend
           (api.py)
              |
              v
        RAG Service
      (rag_service.py)
              |
      +-------+--------+
      |                |
      v                v
  PDF Extraction   Text Chunking
      |                |
      +-------+--------+
              |
              v
     Sentence Transformers
       Text Embeddings
              |
              v
       FAISS Vector Store
              |
              v
    Retrieve Relevant Chunks
              |
              v
       Google Gemini API
              |
              v
     Answer + Source Passages
              |
              v
       Streamlit Frontend

## Tech Stack

| Category             | Technologies                     |
| -------------------- | -------------------------------- |
| Language             | Python                           |
| Frontend             | Streamlit                        |
| Backend API          | FastAPI, Uvicorn                 |
| RAG Framework        | LangChain                        |
| PDF Processing       | PyPDF                            |
| Embeddings           | Sentence Transformers            |
| Vector Database      | FAISS                            |
| LLM                  | Google Gemini                    |
| Supporting Libraries | PyTorch, Requests, python-dotenv |

## How It Works

1. The user uploads a PDF document through the Streamlit interface.
2. PyPDF extracts text and page information from the document.
3. LangChain's `RecursiveCharacterTextSplitter` divides the text into manageable chunks with overlap.
4. Sentence Transformers converts the chunks into vector embeddings.
5. FAISS indexes the embeddings for similarity-based retrieval.
6. When the user asks a question, the system retrieves the most relevant chunks.
7. The retrieved context is passed to Google Gemini with instructions to answer based on the provided document content.
8. The frontend displays the generated answer and relevant source passages.

## Project Structure
## Project Structure

college-knowledge-assistant/
├── app.py              # Streamlit frontend
├── api.py              # FastAPI backend and API endpoints
├── rag_service.py      # PDF processing, retrieval, and generation
├── requirements.txt    # Python dependencies
├── .gitignore          # Excludes secrets and generated files

### Prerequisites

- Python 3.10 or a compatible version supported by your installed dependencies
- A Google Gemini API key
- Git

### 1. Clone the repository

git clone https://github.com/snofa1/college-knowledge-assistant.git
cd college-knowledge-assistant

2. Create and activate a virtual environment

Windows PowerShell:

python -m venv venv
.\venv\Scripts\Activate.ps1

 3. Install dependencies

python -m pip install --upgrade pip
pip install -r requirements.txt

 4. Configure the Gemini API key

Create a `.env` file in the project root:

GEMINI_API_KEY=your_gemini_api_key_here

Replace the placeholder with your own API key.

**Security:** Never commit `.env` or expose your API key in source code, screenshots, or public repositories.

 5. Start the FastAPI backend

Open a terminal in the project directory and run:
uvicorn api:app --reload

The backend will normally be available at:

- API base URL: `http://127.0.0.1:8000`
- Health check: `http://127.0.0.1:8000/health`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

Keep this terminal running.

 6. Start the Streamlit frontend

Open a second terminal, activate the same virtual environment, and run:

streamlit run app.py

Open the local URL printed in the terminal, usually `http://localhost:8501`.

## API Endpoints

The FastAPI backend provides endpoints for application health and question answering.

| Endpoint      | Purpose                                                         |
| ------------- | --------------------------------------------------------------- |
| GET /         | Basic API information                                           |
| GET /health   | Health check                                                    |
| POST /ask     | Submit a question and receive an answer with source information |

For the exact request fields and response schema, start the backend and visit `http://127.0.0.1:8000/docs`.

 **Testing**

The application has been manually tested with questions about information contained in a sample PDF, including attendance requirements and examination weightage.

Testing also included asking a question whose answer was absent from the document to check whether the application could respond that the information could not be found.

These are manual functional checks; a formal automated RAG evaluation suite has not yet been implemented.

## Current Limitations

- Text extraction is intended for PDFs containing selectable text; scanned documents may require OCR.
- Answer quality depends on document quality, chunking, retrieval relevance, and the language model.
- The application uses a limited number of retrieved chunks, which may omit relevant information in some cases.
- Gemini API access requires internet connectivity and a valid API key.
- The model may still produce inaccurate responses, so important information should be checked against the source document.
- Vector indexes are created during processing and are not currently configured for persistent storage across application restarts.

## Future Improvements

- Add automated evaluation for retrieval relevance, answer correctness, and groundedness.
- Improve citations with more precise source attribution.
- Add persistent vector storage and document reuse.
- Support scanned PDFs using OCR.
- Improve handling of multiple documents and larger knowledge bases.
- Deploy the application for public demonstration.

## Security and Privacy

- Store API credentials in environment variables.
- Exclude `.env`, virtual environments, and generated files using `.gitignore`.
- Do not upload private, confidential, or restricted college documents without permission.
- Review uploaded documents before using them with an external LLM service.

