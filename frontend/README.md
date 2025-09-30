# AI Document Summarizer - Frontend

React frontend for the AI Document Summarizer application.

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start the Development Server

```bash
npm run dev
```

The app will run on `http://localhost:3000`

### 3. Make Sure Backend is Running

Ensure your FastAPI backend is running on `http://localhost:8000`:

```bash
# From the project root directory
uvicorn app.main:app --reload
```

## Features

- **Upload PDFs**: Drag and drop or select PDF files to upload and index
- **Ask Questions**: Query your documents with natural language questions
- **Generate Summaries**: Get AI-powered summaries of all uploaded documents
- **View Context**: See which document chunks were used to generate answers

## Technology Stack

- React 18
- Vite (build tool)
- Axios (HTTP client)
- Modern CSS with gradients and animations

## Build for Production

```bash
npm run build
```

The production-ready files will be in the `dist` folder.