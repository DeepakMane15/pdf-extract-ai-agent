import { useState, type FormEvent } from 'react';
import { Link, Navigate } from 'react-router-dom';

import { ApiError, uploadPdf } from '../api/client';
import type { PdfUploadResponse } from '../api/types';
import { useAuth } from '../context/AuthContext';

export function PdfPage() {
  const { user } = useAuth();
  const can = user?.role === 'admin' || user?.role === 'auditor';

  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PdfUploadResponse | null>(null);

  if (!can) {
    return <Navigate to="/" replace />;
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!file) return;
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const res = await uploadPdf(file);
      setResult(res);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Upload failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <h1 className="page-title">PDF ingest</h1>
      <p className="page-desc">Upload a PDF to extract text, chunk, and embed for search and chat.</p>
      <p className="page-desc" style={{ marginTop: '-0.5rem' }}>
        Need previous uploads? <Link to="/pdf/list">Open PDF listing</Link>.
      </p>

      <div className="card">
        <form onSubmit={onSubmit}>
          <div className="field">
            <label htmlFor="pdf">PDF file</label>
            <input
              id="pdf"
              className="input"
              type="file"
              accept=".pdf,application/pdf"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              required
            />
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading || !file}>
            {loading ? 'Processing…' : 'Upload & process'}
          </button>
        </form>
      </div>

      {error ? <div className="alert alert-error">{error}</div> : null}

      {result ? (
        <div className="card">
          <h3>Result</h3>
          {result.processing_error ? (
            <div className="alert alert-warn">Processing note: {result.processing_error}</div>
          ) : (
            <div className="alert alert-success">Ingestion completed.</div>
          )}
          <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.9rem', lineHeight: 1.7 }}>
            <li>Document id: {result.document_id}</li>
            <li>Chunks: {result.chunk_count}</li>
            <li>Size: {(result.size_bytes / 1024).toFixed(1)} KiB</li>
            <li>Stored as: {result.stored_filename}</li>
          </ul>
        </div>
      ) : null}
    </div>
  );
}
