import { useEffect, useState, useRef } from 'react';
import { api } from '../api';

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function Documents() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const fileInputRef = useRef(null);

  const loadDocuments = () => {
    setLoading(true);
    api.getDocuments()
      .then(setDocuments)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const handleUpload = async (files) => {
    if (!files?.length) return;
    setUploading(true);
    setError('');
    setSuccess('');

    try {
      for (const file of files) {
        await api.uploadDocument(file);
      }
      setSuccess(`${files.length} document(s) uploaded and processed successfully`);
      loadDocuments();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this document and all its chunks?')) return;
    try {
      await api.deleteDocument(id);
      loadDocuments();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
    handleUpload(e.dataTransfer.files);
  };

  return (
    <div>
      <div className="page-header">
        <h2>Documents</h2>
        <p>Upload and manage your documents for Q&A</p>
      </div>

      <div
        className="upload-zone"
        onClick={() => fileInputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); e.currentTarget.classList.add('dragover'); }}
        onDragLeave={(e) => e.currentTarget.classList.remove('dragover')}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt,.docx"
          multiple
          onChange={(e) => handleUpload(e.target.files)}
        />
        <p style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>
          {uploading ? 'Processing document...' : 'Drop files here or click to upload'}
        </p>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
          Supported: PDF, TXT, DOCX (max 10 MB)
        </p>
      </div>

      {error && <p className="error">{error}</p>}
      {success && <p className="success">{success}</p>}

      {loading ? (
        <p className="empty-state">Loading documents...</p>
      ) : documents.length === 0 ? (
        <p className="empty-state">No documents uploaded yet.</p>
      ) : (
        <div className="doc-grid">
          {documents.map((doc) => (
            <div key={doc.id} className="doc-item">
              <div className="doc-info">
                <h3>{doc.original_filename}</h3>
                <p className="doc-meta">
                  {formatSize(doc.file_size)} · {doc.total_pages} pages · {doc.total_chunks} chunks ·{' '}
                  <span className={`badge badge-${doc.status}`}>{doc.status}</span>
                </p>
              </div>
              <div className="doc-actions">
                <button className="btn-danger" onClick={() => handleDelete(doc.id)}>
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
