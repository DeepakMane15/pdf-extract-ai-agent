import { useState, type FormEvent } from 'react';

import { apiFetch, ApiError, downloadPdfDocument } from '../api/client';
import type { SearchResponse } from '../api/types';

export function SearchPage() {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<SearchResponse | null>(null);
  const [dlErr, setDlErr] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    setData(null);
    try {
      const res = await apiFetch<SearchResponse>('/search', {
        method: 'POST',
        json: { query: query.trim(), top_k: topK },
      });
      setData(res);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Search failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <h1 className="page-title">Semantic search</h1>
      <p className="page-desc">Embed your query and retrieve the closest document chunks (same pipeline as the API).</p>

      <div className="card">
        <form onSubmit={onSubmit}>
          <div className="field">
            <label htmlFor="q">Query</label>
            <input
              id="q"
              className="input"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="What are you looking for?"
              required
            />
          </div>
          <div className="grid-2">
            <div className="field" style={{ marginBottom: 0 }}>
              <label htmlFor="topk">Top K</label>
              <input
                id="topk"
                className="input"
                type="number"
                min={1}
                max={50}
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Searching…' : 'Search'}
            </button>
          </div>
        </form>
      </div>

      {error ? <div className="alert alert-error">{error}</div> : null}
      {dlErr ? <div className="alert alert-error">{dlErr}</div> : null}

      {data ? (
        <div className="card">
          <h3>Results ({data.results.length})</h3>
          {data.results.length === 0 ? (
            <p className="page-desc" style={{ margin: 0 }}>
              No chunks matched. Ingest PDFs first.
            </p>
          ) : (
            <div className="hits-list">
              {data.results.map((r) => (
                <div key={r.chunk_id} className="hit-item">
                  <div
                    className="hit-meta"
                    style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '0.5rem', justifyContent: 'space-between' }}
                  >
                    <span>
                      chunk #{r.chunk_id} · doc #{r.document_id}
                      {r.page_number != null ? ` · p.${r.page_number}` : ''} · distance {r.cosine_distance.toFixed(4)}
                      {r.rerank_score != null ? ` · rerank ${r.rerank_score.toFixed(4)}` : ''}
                    </span>
                    <button
                      type="button"
                      className="btn btn-secondary"
                      style={{ padding: '0.25rem 0.55rem', fontSize: '0.75rem' }}
                      onClick={() => {
                        setDlErr(null);
                        void downloadPdfDocument(r.document_id, r.document_original_filename ?? null).catch((err) => {
                          setDlErr(err instanceof ApiError ? err.message : 'Download failed');
                        });
                      }}
                    >
                      Download PDF
                    </button>
                  </div>
                  <div style={{ fontSize: '0.9rem', lineHeight: 1.5 }}>{r.chunk_text}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
}
