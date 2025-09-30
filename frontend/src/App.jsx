import { useState } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE = '/api'

function App() {
  const [file, setFile] = useState(null)
  const [uploadStatus, setUploadStatus] = useState('')
  const [query, setQuery] = useState('')
  const [queryResult, setQueryResult] = useState(null)
  const [summary, setSummary] = useState('')
  const [loading, setLoading] = useState(false)

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
    setUploadStatus('')
  }

  const handleUpload = async () => {
    if (!file) {
      setUploadStatus('Please select a file')
      return
    }

    const formData = new FormData()
    formData.append('file', file)

    setLoading(true)
    setUploadStatus('Uploading...')

    try {
      const response = await axios.post(`${API_BASE}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setUploadStatus(`✓ ${response.data.message}`)
    } catch (error) {
      setUploadStatus(`✗ Error: ${error.response?.data?.detail || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadJSON = async () => {
    if (!queryResult || !queryResult.answer) return

    try {
      const formData = new FormData()
      formData.append('query', queryResult.query || query)
      formData.append('answer', queryResult.answer)
      formData.append('context', JSON.stringify(queryResult.context || []))

      const response = await axios.post(`${API_BASE}/download/json`, formData, {
        responseType: 'blob'
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `query_result_${Date.now()}.json`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      alert(`Error downloading JSON: ${error.message}`)
    }
  }

  const handleDownloadPDF = async (content, title) => {
    try {
      const formData = new FormData()
      formData.append('content', content)
      formData.append('title', title)

      const response = await axios.post(`${API_BASE}/download/pdf`, formData, {
        responseType: 'blob'
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${title.replace(/\s+/g, '_')}_${Date.now()}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      alert(`Error downloading PDF: ${error.message}`)
    }
  }

  const handleQuery = async () => {
    if (!query.trim()) {
      return
    }

    setLoading(true)
    setQueryResult(null)

    try {
      const formData = new FormData()
      formData.append('query', query)

      const response = await axios.post(`${API_BASE}/query`, formData)
      setQueryResult(response.data)
    } catch (error) {
      setQueryResult({
        error: error.response?.data?.detail || error.message
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSummarize = async () => {
    setLoading(true)
    setSummary('')

    try {
      const formData = new FormData()
      formData.append('query', 'Summarize the document')

      const response = await axios.post(`${API_BASE}/summarize`, formData)
      setSummary(response.data.summary)
    } catch (error) {
      setSummary(`Error: ${error.response?.data?.detail || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="App">
      <header className="header">
        <h1>📄 AI Document Summarizer</h1>
        <p>Upload PDFs, ask questions, and get AI-powered summaries</p>
      </header>

      <div className="container">
        {/* Upload Section */}
        <section className="card">
          <h2>📤 Upload Document</h2>
          <div className="upload-area">
            <input
              type="file"
              accept=".pdf,.docx,.doc,.txt"
              onChange={handleFileChange}
              className="file-input"
              id="file-input"
            />
            <label htmlFor="file-input" className="file-label">
              {file ? file.name : 'Choose file (PDF, Word, Text)'}
            </label>
            <button
              onClick={handleUpload}
              disabled={loading || !file}
              className="btn btn-primary"
            >
              {loading ? 'Uploading...' : 'Upload & Index'}
            </button>
          </div>
          {uploadStatus && (
            <div className={`status ${uploadStatus.startsWith('✓') ? 'success' : 'error'}`}>
              {uploadStatus}
            </div>
          )}
        </section>

        {/* Query Section */}
        <section className="card">
          <h2>❓ Ask Questions</h2>
          <div className="query-area">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleQuery()}
              placeholder="What would you like to know about the documents?"
              className="text-input"
            />
            <button
              onClick={handleQuery}
              disabled={loading || !query.trim()}
              className="btn btn-secondary"
            >
              {loading ? 'Searching...' : 'Ask'}
            </button>
          </div>

          {queryResult && (
            <div className="result">
              {queryResult.error ? (
                <div className="error">{queryResult.error}</div>
              ) : (
                <>
                  <h3>Answer:</h3>
                  <p className="answer">{queryResult.answer}</p>

                  <div className="download-buttons">
                    <button
                      onClick={handleDownloadJSON}
                      className="btn btn-download"
                    >
                      📥 Download JSON
                    </button>
                    <button
                      onClick={() => handleDownloadPDF(queryResult.answer, 'Query Answer')}
                      className="btn btn-download"
                    >
                      📄 Download PDF
                    </button>
                  </div>

                  {queryResult.context && queryResult.context.length > 0 && (
                    <details className="context-details">
                      <summary>View source context ({queryResult.context.length} chunks)</summary>
                      <div className="context-list">
                        {queryResult.context.map((doc, idx) => (
                          <div key={idx} className="context-item">
                            <strong>Chunk {idx + 1}:</strong>
                            <p>{doc.text.substring(0, 200)}...</p>
                          </div>
                        ))}
                      </div>
                    </details>
                  )}
                </>
              )}
            </div>
          )}
        </section>

        {/* Summarize Section */}
        <section className="card">
          <h2>📝 Generate Summary</h2>
          <button
            onClick={handleSummarize}
            disabled={loading}
            className="btn btn-accent"
          >
            {loading ? 'Generating...' : 'Summarize All Documents'}
          </button>

          {summary && (
            <div className="result">
              <h3>Summary:</h3>
              <p className="summary">{summary}</p>

              <div className="download-buttons">
                <button
                  onClick={() => handleDownloadPDF(summary, 'Document Summary')}
                  className="btn btn-download"
                >
                  📄 Download Summary as PDF
                </button>
              </div>
            </div>
          )}
        </section>
      </div>

      <footer className="footer">
        <p>Powered by OpenAI GPT-4 & FAISS Vector Search</p>
      </footer>
    </div>
  )
}

export default App