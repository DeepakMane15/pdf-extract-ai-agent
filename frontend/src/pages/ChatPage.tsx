import { useState, type FormEvent } from 'react';

import { apiFetch, ApiError } from '../api/client';
import type { ChatAskResponse } from '../api/types';

export function ChatPage() {
  const [question, setQuestion] = useState('');
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<ChatAskResponse | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    setData(null);
    try {
      const res = await apiFetch<ChatAskResponse>('/chat/ask', {
        method: 'POST',
        json: { question: question.trim(), top_k: topK },
      });
      setData(res);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Chat failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <h1 className="page-title">RAG chat</h1>
      <p className="page-desc">Ask a question; the model answers using retrieved chunks as context.</p>

      <div className="card">
        <form onSubmit={onSubmit}>
          <div className="field">
            <label htmlFor="question">Question</label>
            <textarea
              id="question"
              className="textarea"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask about your documents…"
              required
              rows={4}
            />
          </div>
          <div className="grid-2">
            <div className="field" style={{ marginBottom: 0 }}>
              <label htmlFor="ctopk">Chunks for context</label>
              <input
                id="ctopk"
                className="input"
                type="number"
                min={1}
                max={20}
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Thinking…' : 'Ask'}
            </button>
          </div>
        </form>
      </div>

      {error ? <div className="alert alert-error">{error}</div> : null}

      {data ? (
        <>
          <div className="card">
            <h3>Answer</h3>
            <div style={{ fontSize: '0.95rem', lineHeight: 1.65, whiteSpace: 'pre-wrap' }}>{data.answer}</div>
            {data.cited_chunk_ids.length > 0 ? (
              <p style={{ margin: '1rem 0 0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Cited chunk ids: {data.cited_chunk_ids.join(', ')}
              </p>
            ) : null}
          </div>
          <div className="card">
            <h3>Sources ({data.sources.length})</h3>
            <div className="hits-list">
              {data.sources.map((s) => (
                <div key={s.chunk_id} className="hit-item">
                  <div className="hit-meta">
                    #{s.chunk_id} · doc #{s.document_id}
                    {s.page_number != null ? ` · p.${s.page_number}` : ''}
                  </div>
                  <div style={{ fontSize: '0.85rem' }}>{s.excerpt}</div>
                </div>
              ))}
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}
