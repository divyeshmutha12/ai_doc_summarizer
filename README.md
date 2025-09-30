# 📄 AI Multi-Document Summarizer

An AI-powered full-stack application that enables users to upload and process multiple documents, then generates concise summaries or context-aware answers to queries using OpenAI’s LLMs.

The system integrates FastAPI on the backend, React on the frontend for a seamless user experience, and FAISS for efficient vector search—ensuring accurate retrieval and scalable performance even with large document collections.

---

## 🚀 Features

* 📂 **Multi-format Uploads** – Supports PDF, DOCX, and TXT files
* 🧩 **Chunking & Embeddings** – Splits documents into chunks and embeds them using OpenAI models
* ⚡ **FAISS Vector Search** – Fast similarity search across document chunks
* 🤖 **AI Summarization & Q&A** – Generate summaries and answer user questions with context
* 🌐 **Frontend + Backend** – Modern React-based frontend powered by **FastAPI**
* 💾 **Persistent Storage** – Save FAISS indices and re-use across sessions
* 📑 **Export Results** – Summaries and Q&A can be saved as JSON or PDF

---

## 🏗️ Project Structure

```
ai_doc_summarizer/
│
├─ app/                     # Backend (FastAPI)
│   ├─ main.py               # FastAPI entry point
│   ├─ models/
│   │   ├─ embeddings.py     # FAISS embedding and indexing
│   │   └─ llm.py            # LLM summarization/Q&A
│   ├─ core/
│   │   └─ utils.py          # Text extraction, chunking
│   └─ static/uploads/       # Uploaded documents
│
├─ frontend/                 # Frontend (React app)
│   ├─ src/
│   │   ├─ components/       # Upload UI, Results display
│   │   ├─ pages/            # Summarizer, Q&A pages
│   │   └─ App.js            # Main React app
│   └─ package.json
│
├─ faiss_index/              # Saved FAISS indices
├─ outputs/                  # JSON / PDF results
├─ requirements.txt          # Backend dependencies
├─ package.json              # Frontend dependencies
└─ README.md

```

---

## ⚙️ Tech Stack / Tools

* **Backend:** FastAPI (Python)
* **Frontend:** React 18 + Vite, Custom CSS
* **LLM Provider:** OpenAI GPT models (for summarization & Q&A)
* **Vector Database:** FAISS
* **Utilities:**

  * PyMuPDF / PyPDF2 → PDF extraction
  * docx2txt → Word file parsing
  * dotenv → API key management
  * pickle → Metadata persistence

---

## 🔄 Workflow

1. **Upload Documents** – User uploads PDFs/DOCX/TXT through the frontend.
2. **Text Extraction** – Backend extracts text and converts to chunks.
3. **Embeddings & Indexing** – Each chunk is embedded using OpenAI embeddings and stored in a FAISS index.
4. **Vector Search** – On summarization or Q&A request, FAISS retrieves top relevant chunks.
5. **LLM Summarization / Q&A** – OpenAI GPT generates summary or answers based on retrieved context.
6. **Output Delivery** – Results are shown on frontend and stored in `/outputs` as JSON/PDF.

---

## ⚡ Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/divyeshmutha12/ai_doc_summarizer.git
cd ai-doc-summarizer
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set API Key

Create a `.env` file in the root directory:

```
OPENAI_API_KEY=your_openai_api_key
```

### 5. Run the Application

```bash
uvicorn app.main:app --reload
```

Navigate to: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 📝 Example Use Cases

* Generate executive summaries for multiple research papers
* Answer questions based on uploaded compliance/legal docs
* Summarize meeting notes from multiple files
* Knowledge extraction from large document collections

---

## 🔮 Future Scope

* ✅ Support for audio/video transcription (via Whisper)
* ✅ Multi-language summarization
* ✅ Fine-tuned LLM integration for domain-specific tasks

---

## 🤝 Contributing

Contributions are welcome! Please fork the repo and create a pull request.

---

## 📜 License

MIT License – Free to use and modify.

---
