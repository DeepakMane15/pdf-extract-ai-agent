import { useCallback, useEffect, useState, type FormEvent } from 'react';

import { apiFetch, ApiError, downloadPdfDocument } from '../api/client';
import type { HealthResponse, PdfDocumentListItem } from '../api/types';
import { useAuth } from '../context/AuthContext';

export function DashboardPage() {
  const { user, refreshMe } = useAuth();
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthErr, setHealthErr] = useState<string | null>(null);

  const [docs, setDocs] = useState<PdfDocumentListItem[]>([]);
  const [docsErr, setDocsErr] = useState<string | null>(null);
  const [docsLoading, setDocsLoading] = useState(false);
  const [docDlErr, setDocDlErr] = useState<string | null>(null);

  const [apiKeyInput, setApiKeyInput] = useState('');
  const [keyMsg, setKeyMsg] = useState<{ type: 'ok' | 'err'; text: string } | null>(null);
  const [savingKey, setSavingKey] = useState(false);
  const [clearingKey, setClearingKey] = useState(false);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const h = await apiFetch<HealthResponse>('/health');
        if (!cancelled) {
          setHealth(h);
          setHealthErr(null);
        }
      } catch (e) {
        if (!cancelled) {
          setHealthErr(e instanceof ApiError ? e.message : 'Health check failed');
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const loadMyDocuments = useCallback(async () => {
    setDocsLoading(true);
    setDocsErr(null);
    try {
      const list = await apiFetch<PdfDocumentListItem[]>('/pdf/documents');
      setDocs(list);
    } catch (e) {
      setDocsErr(e instanceof ApiError ? e.message : 'Could not load documents');
      setDocs([]);
    } finally {
      setDocsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (user) void loadMyDocuments();
  }, [user, loadMyDocuments]);

  async function onSaveKey(e: FormEvent) {
    e.preventDefault();
    setKeyMsg(null);
    setSavingKey(true);
    try {
      await apiFetch('/users/me/openai-key', {
        method: 'PUT',
        json: { api_key: apiKeyInput.trim() },
      });
      setApiKeyInput('');
      setKeyMsg({ type: 'ok', text: 'API key saved (encrypted at rest on the server).' });
      await refreshMe();
      void loadMyDocuments();
    } catch (err) {
      setKeyMsg({
        type: 'err',
        text: err instanceof ApiError ? err.message : 'Could not save key.',
      });
    } finally {
      setSavingKey(false);
    }
  }

  async function onClearKey() {
    setKeyMsg(null);
    setClearingKey(true);
    try {
      await apiFetch('/users/me/openai-key', { method: 'DELETE' });
      setKeyMsg({ type: 'ok', text: 'Personal API key removed. The server default will be used if configured.' });
      await refreshMe();
    } catch (err) {
      setKeyMsg({
        type: 'err',
        text: err instanceof ApiError ? err.message : 'Could not remove key.',
      });
    } finally {
      setClearingKey(false);
    }
  }

  return (
    <div className="page">
      <h1 className="page-title">Overview</h1>
      <p className="page-desc">Service status, OpenAI usage for your account, and API key settings.</p>

      <div className="card">
        <h3>API health</h3>
        {healthErr ? <div className="alert alert-error">{healthErr}</div> : null}
        {health ? (
          <p>
            Status: <span className="badge badge-accent">{health.status}</span>
          </p>
        ) : !healthErr ? (
          <p className="page-desc" style={{ margin: 0 }}>
            Checking…
          </p>
        ) : null}
      </div>

      <div className="card">
        <h3>Account</h3>
        {user ? (
          <dl style={{ margin: '0 0 1rem', display: 'grid', gap: '0.35rem', fontSize: '0.9rem' }}>
            <div>
              <dt style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Email</dt>
              <dd style={{ margin: 0 }}>{user.email}</dd>
            </div>
            <div>
              <dt style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Role</dt>
              <dd style={{ margin: 0 }}>
                <span className="badge badge-accent">{user.role}</span>
              </dd>
            </div>
            <div>
              <dt style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Active</dt>
              <dd style={{ margin: 0 }}>{user.is_active ? 'Yes' : 'No'}</dd>
            </div>
          </dl>
        ) : (
          <p className="page-desc" style={{ margin: 0 }}>
            Loading profile…
          </p>
        )}
      </div>

      {user ? (
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap' }}>
            <h3 style={{ margin: 0 }}>Your uploaded PDFs</h3>
            <button type="button" className="btn btn-secondary" disabled={docsLoading} onClick={() => void loadMyDocuments()}>
              {docsLoading ? 'Refreshing…' : 'Refresh'}
            </button>
          </div>
          <p className="page-desc" style={{ marginTop: '0.35rem' }}>
            Files you ingested while signed in (admin or auditor uploads are attributed to your account).
          </p>
          {docDlErr ? <div className="alert alert-error">{docDlErr}</div> : null}
          {docsErr ? <div className="alert alert-error">{docsErr}</div> : null}
          {docsLoading && docs.length === 0 ? (
            <p className="page-desc" style={{ margin: 0 }}>
              Loading…
            </p>
          ) : docs.length === 0 ? (
            <p className="page-desc" style={{ margin: 0 }}>
              No PDFs yet. Use PDF ingest to upload.
            </p>
          ) : (
            <div className="table-wrap">
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
                          <div className="alert alert-warn" style={{ margin: '0.35rem 0 0', padding: '0.35rem 0.5rem', fontSize: '0.8rem' }}>
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
                            setDocDlErr(null);
                            void downloadPdfDocument(d.id, d.original_filename).catch((err) => {
                              setDocDlErr(err instanceof ApiError ? err.message : 'Download failed');
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
      ) : null}

      {user ? (
        <div className="card">
          <h3>OpenAI token usage (your account)</h3>
          <p className="page-desc" style={{ marginTop: 0 }}>
            Totals are updated from embedding and chat API responses (search, chat, PDF ingest, and tool calls).
          </p>
          <div className="stats-grid">
            <div className="stat-tile">
              <div className="label">Embedding tokens</div>
              <div className="value">{user.openai_embed_prompt_tokens_total.toLocaleString()}</div>
            </div>
            <div className="stat-tile">
              <div className="label">Chat prompt</div>
              <div className="value">{user.openai_chat_prompt_tokens_total.toLocaleString()}</div>
            </div>
            <div className="stat-tile">
              <div className="label">Chat completion</div>
              <div className="value">{user.openai_chat_completion_tokens_total.toLocaleString()}</div>
            </div>
            <div className="stat-tile">
              <div className="label">Grand total</div>
              <div className="value">{user.openai_tokens_grand_total.toLocaleString()}</div>
            </div>
          </div>
        </div>
      ) : null}

      {user ? (
        <div className="card">
          <h3>OpenAI API key</h3>
          <p className="page-desc" style={{ marginTop: 0 }}>
            Your key is stored encrypted on the server (Fernet symmetric encryption) so it can be used for API calls.
            One-way hashing cannot be used here because the service must send the real key to OpenAI. You can instead
            rely on the server <code style={{ fontSize: '0.85em' }}>OPENAI_API_KEY</code> when it is set.
          </p>
          <ul style={{ margin: '0 0 1rem', paddingLeft: '1.2rem', fontSize: '0.88rem', color: 'var(--text-muted)' }}>
            <li>
              Personal key: {user.openai_key_configured ? (
                <>
                  <span className="badge badge-accent">configured</span>
                  {user.openai_key_hint ? (
                    <span style={{ marginLeft: 8, fontFamily: 'var(--mono)' }}>{user.openai_key_hint}</span>
                  ) : null}
                </>
              ) : (
                <span className="badge">not set</span>
              )}
            </li>
            <li>
              Server fallback:{' '}
              {user.server_openai_configured ? (
                <span className="badge badge-accent">available</span>
              ) : (
                <span className="badge">not configured</span>
              )}
            </li>
          </ul>
          {keyMsg ? (
            <div className={keyMsg.type === 'ok' ? 'alert alert-success' : 'alert alert-error'}>{keyMsg.text}</div>
          ) : null}
          <form onSubmit={onSaveKey}>
            <div className="field">
              <label htmlFor="openai-key">Set or replace personal key</label>
              <input
                id="openai-key"
                className="input"
                type="password"
                autoComplete="off"
                value={apiKeyInput}
                onChange={(e) => setApiKeyInput(e.target.value)}
                placeholder="sk-…"
              />
            </div>
            <div className="stack" style={{ flexDirection: 'row', flexWrap: 'wrap', gap: '0.5rem' }}>
              <button type="submit" className="btn btn-primary" disabled={savingKey || !apiKeyInput.trim()}>
                {savingKey ? 'Saving…' : 'Save encrypted key'}
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                disabled={clearingKey || !user.openai_key_configured}
                onClick={() => void onClearKey()}
              >
                {clearingKey ? 'Removing…' : 'Remove personal key'}
              </button>
            </div>
          </form>
        </div>
      ) : null}
    </div>
  );
}
