import { useCallback, useEffect, useState } from 'react';

import { apiFetch, ApiError, downloadPdfDocument } from '../api/client';
import type { PdfDocumentListItem } from '../api/types';

export function PdfListingPage() {
  const [docs, setDocs] = useState<PdfDocumentListItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const loadDocuments = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const list = await apiFetch<PdfDocumentListItem[]>('/pdf/documents');
      setDocs(list);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not load documents');
      setDocs([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadDocuments();
  }, [loadDocuments]);

  return (
    <div className="page">
      <h1 className="page-title">PDF listing</h1>
      <p className="page-desc">All PDFs uploaded by your account.</p>

      <div className="card">
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '1rem',
            flexWrap: 'wrap',
          }}
        >
          <h3 style={{ margin: 0 }}>Your uploaded PDFs</h3>
          <button
            type="button"
            className="btn btn-secondary"
            disabled={loading}
            onClick={() => void loadDocuments()}
          >
            {loading ? 'Refreshing…' : 'Refresh'}
          </button>
        </div>

        {downloadError ? <div className="alert alert-error">{downloadError}</div> : null}
        {error ? <div className="alert alert-error">{error}</div> : null}

        {loading && docs.length === 0 ? (
          <p className="page-desc" style={{ marginTop: '0.75rem' }}>
            Loading…
          </p>
        ) : docs.length === 0 ? (
          <p className="page-desc" style={{ marginTop: '0.75rem' }}>
            No PDFs found for your account yet.
          </p>
        ) : (
          <div className="table-wrap" style={{ marginTop: '0.75rem' }}>
            <table className="data">
              <thead>
                <tr>
                  <th>File</th>
                  <th>Chunks</th>
                  <th>Size</th>
                  <th>Uploaded</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {docs.map((d) => (
                  <tr key={d.id}>
                    <td>
                      <div style={{ fontWeight: 500 }}>{d.original_filename || d.stored_filename}</div>
                      {d.processing_error ? (
                        <div
                          className="alert alert-warn"
                          style={{ margin: '0.35rem 0 0', padding: '0.35rem 0.5rem', fontSize: '0.8rem' }}
                        >
                          {d.processing_error}
                        </div>
                      ) : null}
                    </td>
                    <td>{d.chunk_count}</td>
                    <td>{(d.file_size_bytes / 1024).toFixed(1)} KiB</td>
                    <td style={{ whiteSpace: 'nowrap', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      {new Date(d.created_at).toLocaleString()}
                    </td>
                    <td>
                      <button
                        type="button"
                        className="btn btn-secondary"
                        style={{ padding: '0.35rem 0.65rem', fontSize: '0.8rem' }}
                        onClick={() => {
                          setDownloadError(null);
                          void downloadPdfDocument(d.id, d.original_filename).catch((err) => {
                            setDownloadError(err instanceof ApiError ? err.message : 'Download failed');
                          });
                        }}
                      >
                        Download
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
