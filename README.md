# 📚 College Knowledge Assistant

A web-based PDF question-answering application built using **Retrieval-Augmented Generation (RAG)**. Users can upload a PDF, ask questions about its contents, receive answers grounded in the document, and inspect the source text and page numbers.

## 🚀 Live Demo

**Live Application:** [College Knowledge Assistant](https://college-knowledge-assistant-1-74hg.onrender.com)

## ✨ Features

- **PDF Upload:** Upload PDF documents through a Streamlit interface.
- **Text Extraction:** Extract readable text from PDF pages using PyPDF.
- **Text Chunking:** Split document text into overlapping chunks using LangChain text splitters.
- **Gemini Embeddings:** Generate document and query embeddings using Google's `gemini-embedding-001` model.
- **Semantic Search:** Use FAISS to retrieve text chunks relevant to a user's question.
- **AI-Powered Answers:** Generate context-based responses using Google's Gemini model.
- **Source References:** Display retrieved text and corresponding PDF page numbers.
- **Unsupported Question Handling:** Instruct the model to indicate when the answer cannot be found in the provided PDF.
- **Separate Frontend and Backend:** Use Streamlit for the interface and FastAPI for document processing and question answering.

## 🛠️ Tech Stack

| Technology             | Purpose                                                        |
| ---------------------- | -------------------------------------------------------------- |
| Python                 | Application logic                                              |
| Streamlit              | Web frontend                                                   |
| FastAPI                | Backend API                                                    |
| Google Gemini API      | Embeddings and answer generation                               |
| gemini-embedding-001  | Semantic embeddings                                            |
| FAISS                  | Vector similarity search                                       |
| LangChain              | Document objects, text splitting, and vector-store integration |
| PyPDF                  | PDF text extraction                                            |
| Requests               | Frontend-to-backend HTTP communication                         |
| Render                 | Application deployment                                         |
| Git and GitHub         | Version control and source hosting                             |

## 🏗️ Architecture

text
                  User
                   |
                   v
          Streamlit Frontend
                   |
                   | HTTP requests
                   v
             FastAPI Backend
                   |
          +--------+---------+
          |                  |
          v                  v
     PDF Extraction     User Question
       (PyPDF)                |
          |                  v
          v          Gemini Query Embedding
     Text Chunking             |
          |                    |
          v                    |
 Gemini Document Embeddings    |
          |                    |
          v                    |
       FAISS Vector Store <----+
          |
          v
    Relevant Text Chunks
          |
          v
    Gemini Answer Generation
          |
          v
   Answer + Source References
          |
          v
     Streamlit Frontend


## 🔄 How It Works

1. The user uploads a PDF through the Streamlit frontend.
2. The FastAPI backend extracts readable text and preserves page metadata.
3. LangChain splits the extracted text into chunks with overlap.
4. Gemini generates embeddings for the document chunks.
5. FAISS stores the embeddings and supports similarity-based retrieval.
6. When the user asks a question, Gemini generates a query embedding and FAISS retrieves relevant chunks.
7. The retrieved context is passed to Gemini for answer generation.
8. The application displays the answer and retrieved source text with page numbers.

## 📁 Project Structure


college-knowledge-assistant/
├── app.py              # Streamlit frontend
├── api.py              # FastAPI backend and API endpoints
├── rag_service.py      # PDF processing, embeddings, retrieval, and answers
├── requirements.txt    # Python dependencies
├── .gitignore          # Files excluded from Git
└── README.md           # Project documentation


The `.env` file is created locally and is not committed to GitHub.

## ⚙️ Local Setup

### Prerequisites

- Python 3.10 or a compatible version supported by your dependencies
- A Google Gemini API key
- Git

### 1. Clone the repository


git clone https://github.com/snofa1/college-knowledge-assistant.git
cd college-knowledge-assistant


### 2. Create and activate a virtual environment

Windows PowerShell:


python -m venv venv
.\venv\Scripts\Activate.ps1


### 3. Install dependencies


pip install -r requirements.txt


### 4. Configure the Gemini API key

Create a `.env` file in the project root:


GEMINI_API_KEY=your_gemini_api_key


Replace the placeholder with your own key. Never commit `.env` or share your API key publicly.

### 5. Start the FastAPI backend


uvicorn api:app --reload


The backend runs locally at:

http://127.0.0.1:8000

Open the interactive API documentation:

http://127.0.0.1:8000/docs

### 6. Start the Streamlit frontend

In a second terminal, activate the virtual environment and run:


streamlit run app.py


The frontend is usually available at:

http://localhost:8501

**Note:** The current `app.py` is configured to call the deployed Render backend. To use a local backend instead, change `API_URL` to `http://127.0.0.1:8000`.

## 🔌 API Endpoints

The deployed backend exposes these application endpoints:

| Endpoint            | Method | Purpose                               |
| ------------------- | ------ | ------------------------------------- |
| /                   | GET    | Check API status                      |
| /documents/upload   | POST   | Upload and process a PDF              |
| /chat               | POST   | Ask a question about an uploaded PDF  |
| /docs               | GET    | Interactive Swagger API documentation |

Use the live [API documentation](https://college-knowledge-assistant-g4hz.onrender.com/docs) to inspect request fields and response schemas.

## 🧪 Testing

The application was manually tested using a sample PDF with known content.

**Supported question example**

Question: *What is the minimum attendance required for the end-semester examination?*

Expected result: The application returns the 75% attendance requirement and displays relevant source text with its page number.

**Unsupported question example**

Question: *What is the monthly salary of the college principal?*

Expected result:

> I could not find the answer in the provided PDF.

These tests demonstrate basic document retrieval and unsupported-question handling. They do not guarantee correct answers for every PDF or question.

## 🔐 Security and Privacy

- Store the Gemini API key in an environment variable.
- Keep `.env` out of version control.
- Do not upload confidential or restricted documents to a public demo.
- The current implementation stores uploaded documents and vector stores in memory. They are not persistent and may be lost when the backend restarts.
- Anyone who can access the public demo may be able to use its exposed functionality. Avoid uploading sensitive information.

## ⚠️ Current Limitations

- Scanned PDFs may require OCR, which is not currently implemented.
- Retrieval quality depends on PDF text extraction, chunking, embeddings, and similarity search.
- The current embedding implementation makes individual API calls for document chunks, which can increase processing time and encounter API rate limits on larger PDFs.
- Documents are held in backend memory rather than persistent storage.
- Free hosting instances may sleep when inactive, causing delays on the first request.
- Unsupported-question handling relies on the retrieved context and model instructions; it is not a formal guarantee against hallucinations.
- Gemini API availability, quotas, and usage costs depend on the configured account and model access.

## 🔮 Future Improvements

- Add persistent document and vector storage.
- Batch embedding requests to improve document-processing efficiency.
- Add OCR support for scanned PDFs.
- Improve retrieval confidence checks and evaluation.
- Add authentication and per-user document isolation.
- Add automated tests and structured logging.
- Improve handling of API timeouts, rate limits, and service failures.


