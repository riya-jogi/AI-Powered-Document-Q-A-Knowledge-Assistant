import { useEffect, useState, useRef } from 'react';
import { api } from '../api';

const READY_STATUS = 'completed';
const PENDING_STATUSES = ['uploaded', 'processing'];

function isReadyDocument(doc) {
  return doc?.status === READY_STATUS && (Number(doc.total_chunks) || 0) > 0;
}

export default function Chat() {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState('');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);

  const readyDocuments = documents.filter(isReadyDocument);
  const pendingDocuments = documents.filter((doc) => PENDING_STATUSES.includes(doc.status));

  useEffect(() => {
    let cancelled = false;

    const refreshDocuments = async () => {
      try {
        const docs = await api.getDocuments();
        if (cancelled) return;

        setDocuments(docs);

        const nextReady = docs.filter(isReadyDocument);
        if (nextReady.length > 0) {
          setSelectedDoc((current) => {
            if (current && nextReady.some((doc) => String(doc.id) === current)) return current;
            return String(nextReady[0].id);
          });
        } else {
          setSelectedDoc('');
        }
      } catch (err) {
        if (!cancelled) console.error('Failed to load documents:', err);
      }
    };

    refreshDocuments();

    const interval = setInterval(() => {
      refreshDocuments();
    }, 5000);

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || !selectedDoc || loading) return;

    const question = input.trim();
    setInput('');
    setError('');
    setMessages((prev) => [...prev, { role: 'user', content: question }]);
    setLoading(true);

    try {
      const response = await api.askQuestion(question, parseInt(selectedDoc));
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response.answer, sources: response.sources },
      ]);
    } catch (err) {
      setError(err.message);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `Error: ${err.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h2>Chat</h2>
        <p>Ask questions about your uploaded documents</p>
      </div>

      <div className="select-doc">
        <label style={{ display: 'block', marginBottom: '0.4rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
          Select Document
        </label>
        <select value={selectedDoc} onChange={(e) => { setSelectedDoc(e.target.value); setMessages([]); }} disabled={readyDocuments.length === 0}>
          {readyDocuments.length === 0 ? (
            <option value="">No processed documents available</option>
          ) : (
            readyDocuments.map((doc) => (
              <option key={doc.id} value={doc.id}>{doc.original_filename}</option>
            ))
          )}
        </select>
      </div>

      {pendingDocuments.length > 0 && !selectedDoc && (
        <p className="empty-state" style={{ marginTop: '1rem', textAlign: 'left' }}>
          One or more documents are still processing. Q&A unlocks automatically once indexing finishes.
        </p>
      )}

      <div className="chat-container card" style={{ height: 'calc(100vh - 280px)' }}>
        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="empty-state">
              <p>{selectedDoc ? 'Ask a question about the selected document.' : 'No processed documents available yet.'}</p>
              <p style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}>
                {selectedDoc
                  ? 'Example: "What are the main objectives mentioned in this document?"'
                  : 'Upload a file and wait for processing to finish before asking questions.'}
              </p>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              <p>{msg.content}</p>
              {msg.sources?.length > 0 && (
                <div className="sources">
                  <h4>Sources</h4>
                  {msg.sources.map((s, j) => (
                    <div key={j} className="source-item">
                      • {s.document} — Page {s.page ?? 'N/A'} (score: {s.score.toFixed(2)})
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="message assistant">
              <p>Thinking...</p>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {error && <p className="error">{error}</p>}

        <form className="chat-input" onSubmit={handleSend}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={selectedDoc ? 'Ask a question...' : 'Processing...'}
            disabled={!selectedDoc || loading}
          />
          <button type="submit" className="btn-primary" disabled={!selectedDoc || loading || !input.trim()}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
