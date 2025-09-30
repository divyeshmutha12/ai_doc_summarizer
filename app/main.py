from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from pathlib import Path
import shutil
import uuid
import json
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

from app.models.embeddings import EmbeddingModel
from app.models.llm import LLMModel
from app.core.utils import extract_text, chunk_text

UPLOAD_DIR = Path("app/static/uploads")
FAISS_DIR = Path("faiss_index")
OUTPUT_DIR = Path("outputs")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
FAISS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

app = FastAPI(title="AI Document Summarizer")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

embedding_model = EmbeddingModel(index_path=str(FAISS_DIR / "docs.index"))
llm_model = LLMModel()


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not supported. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    file_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Validate file size
        if file_path.stat().st_size > MAX_FILE_SIZE:
            file_path.unlink()
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

        # Extract text based on file type
        text = extract_text(str(file_path))

        if not text or len(text.strip()) < 10:
            file_path.unlink()
            raise HTTPException(status_code=400, detail="Could not extract meaningful text from file")

        chunks = chunk_text(text)
        embedding_model.add_documents(chunks, metadata={"filename": file.filename, "file_id": file_id})

        return {"message": "File uploaded and indexed", "file_id": file_id, "filename": file.filename}

    except ValueError as e:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.post("/api/query")
async def query_document(query: str = Form(...)):
    docs = embedding_model.search(query, top_k=5)
    if not docs:
        return JSONResponse(
            {"query": query, "answer": "No documents have been uploaded yet. Please upload documents first.", "context": []},
            status_code=200
        )
    answer = llm_model.answer_query(query, docs)
    return JSONResponse({"query": query, "answer": answer, "context": docs})


@app.post("/api/summarize")
async def summarize_document(query: str = Form("Summarize the document")):
    docs = embedding_model.get_all_documents()
    if not docs:
        return JSONResponse(
            {"summary": "No documents have been uploaded yet. Please upload documents first."},
            status_code=200
        )
    summary = llm_model.answer_query(query, docs)
    return JSONResponse({"summary": summary})


@app.post("/api/download/json")
async def download_json(query: str = Form(...), answer: str = Form(...), context: str = Form("[]")):
    """Download query results as JSON file"""
    try:
        context_data = json.loads(context)
    except:
        context_data = []

    data = {
        "query": query,
        "answer": answer,
        "context": context_data,
        "timestamp": datetime.now().isoformat()
    }

    json_str = json.dumps(data, indent=2)

    return StreamingResponse(
        io.BytesIO(json_str.encode()),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"}
    )


@app.post("/api/download/pdf")
async def download_pdf(content: str = Form(...), title: str = Form("Document Summary")):
    """Download summary or query result as PDF file"""
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='#1a1a1a',
        spaceAfter=12
    )
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.2 * inch))

    # Timestamp
    timestamp = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    story.append(Paragraph(timestamp, styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))

    # Content
    content_paragraphs = content.split('\n')
    for para in content_paragraphs:
        if para.strip():
            story.append(Paragraph(para, styles['BodyText']))
            story.append(Spacer(1, 0.1 * inch))

    doc.build(story)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"}
    )


@app.get("/")
async def root():
    return {"message": "AI Multi-Document Summarizer API", "status": "running"}
