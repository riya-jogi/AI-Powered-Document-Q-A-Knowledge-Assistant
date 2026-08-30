import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';

export default function Dashboard() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getDocuments()
      .then(setDocuments)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const readyDocuments = documents.filter((d) => d.status === 'completed' && (Number(d.total_chunks) || 0) > 0);
  const pendingDocuments = documents.filter((d) => !['completed', 'failed'].includes(d.status));

  return (
    <div>
      <div className="page-header">
        <h2>Dashboard</h2>
        <p>Overview of your document knowledge base</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <div className="card">
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Total Documents</p>
          <p style={{ fontSize: '2rem', fontWeight: 700 }}>{documents.length}</p>
        </div>
        <div className="card">
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Ready for Q&A</p>
          <p style={{ fontSize: '2rem', fontWeight: 700 }}>{readyDocuments.length}</p>
        </div>
        <div className="card">
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Total Chunks</p>
          <p style={{ fontSize: '2rem', fontWeight: 700 }}>
            {documents.reduce((sum, d) => sum + (d.total_chunks || 0), 0)}
          </p>
        </div>
      </div>

      <div className="card">
        <h3 style={{ marginBottom: '1rem' }}>Quick Actions</h3>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <Link to="/documents"><button className="btn-primary">Upload Document</button></Link>
          <Link to="/chat"><button className="btn-secondary" disabled={readyDocuments.length === 0}>Ask a Question</button></Link>
        </div>
        {pendingDocuments.length > 0 && (
          <p style={{ marginTop: '0.75rem', color: 'var(--text-muted)' }}>
            {pendingDocuments.length} document(s) are still processing. Q&A will unlock once indexing finishes.
          </p>
        )}
      </div>

      {loading ? (
        <p className="empty-state">Loading...</p>
      ) : documents.length === 0 ? (
        <p className="empty-state">No documents yet. Upload your first document to get started.</p>
      ) : (
        <div style={{ marginTop: '2rem' }}>
          <h3 style={{ marginBottom: '1rem' }}>Recent Documents</h3>
          <div className="doc-grid">
            {documents.slice(0, 5).map((doc) => (
              <div key={doc.id} className="doc-item">
                <div className="doc-info">
                  <h3>{doc.original_filename}</h3>
                  <p className="doc-meta">
                    {doc.total_pages} pages · {doc.total_chunks} chunks ·{' '}
                    <span className={`badge badge-${doc.status}`}>{doc.status}</span>
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
