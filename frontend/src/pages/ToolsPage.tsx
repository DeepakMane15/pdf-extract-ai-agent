import { useEffect, useMemo, useState, type FormEvent } from 'react';

import { apiFetch, ApiError } from '../api/client';
import type { ToolInvokeResponse, ToolMeta } from '../api/types';
import { useAuth } from '../context/AuthContext';

const DEFAULT_ARGS: Record<string, string> = {
  send_email: JSON.stringify({ to: 'user@example.com', subject: 'Hello', body: 'Message body…' }, null, 2),
  search_docs: JSON.stringify({ query: 'your question', top_k: 5 }, null, 2),
  compliance_check: JSON.stringify({ text: 'Paste text to scan…', policy_hint: null }, null, 2),
};

export function ToolsPage() {
  const { user } = useAuth();
  const [meta, setMeta] = useState<ToolMeta[]>([]);
  const [metaErr, setMetaErr] = useState<string | null>(null);
  const [loadingMeta, setLoadingMeta] = useState(true);

  const [selected, setSelected] = useState<string>('');
  const [argsJson, setArgsJson] = useState('{}');
  const [invokeErr, setInvokeErr] = useState<string | null>(null);
  const [result, setResult] = useState<ToolInvokeResponse | null>(null);
  const [invoking, setInvoking] = useState(false);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      setMetaErr(null);
      setLoadingMeta(true);
      try {
        const list = await apiFetch<ToolMeta[]>('/tools');
        if (cancelled) return;
        setMeta(list);
        if (list.length > 0) {
          const first = list[0]!.name;
          setSelected(first);
          setArgsJson(DEFAULT_ARGS[first] ?? '{}');
        }
      } catch (e) {
        if (!cancelled) {
          setMetaErr(e instanceof ApiError ? e.message : 'Failed to load tools');
        }
      } finally {
        if (!cancelled) setLoadingMeta(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const selectedMeta = useMemo(() => meta.find((m) => m.name === selected), [meta, selected]);

  function onSelectTool(name: string) {
    setSelected(name);
    setArgsJson(DEFAULT_ARGS[name] ?? '{}');
    setResult(null);
    setInvokeErr(null);
  }

  async function onInvoke(e: FormEvent) {
    e.preventDefault();
    setInvokeErr(null);
    setResult(null);
    let parsed: Record<string, unknown>;
    try {
      parsed = JSON.parse(argsJson) as Record<string, unknown>;
    } catch {
      setInvokeErr('Arguments must be valid JSON.');
      return;
    }
    setInvoking(true);
    try {
      const res = await apiFetch<ToolInvokeResponse>('/tools/invoke', {
        method: 'POST',
        json: { tool_name: selected, arguments: parsed },
      });
      setResult(res);
    } catch (err) {
      setInvokeErr(err instanceof ApiError ? err.message : 'Invoke failed');
    } finally {
      setInvoking(false);
    }
  }

  const allowed = selectedMeta?.allowed_roles ?? [];
  const canRun = Boolean(user && allowed.includes(user.role));

  return (
    <div className="page">
      <h1 className="page-title">Tool calling</h1>
      <p className="page-desc">Registered backend tools with RBAC. Invocations are logged server-side.</p>

      {metaErr ? <div className="alert alert-error">{metaErr}</div> : null}

      {loadingMeta ? (
        <p className="page-desc">Loading tool registry…</p>
      ) : (
        <>
          <div className="card">
            <h3>Registry</h3>
            <div className="hits-list">
              {meta.map((m) => (
                <button
                  key={m.name}
                  type="button"
                  onClick={() => onSelectTool(m.name)}
                  className="hit-item"
                  style={{
                    cursor: 'pointer',
                    textAlign: 'left',
                    width: '100%',
                    border: selected === m.name ? '2px solid var(--accent)' : undefined,
                  }}
                >
                  <div style={{ fontWeight: 600, marginBottom: 4 }}>{m.name}</div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 8 }}>{m.description}</div>
                  <div>
                    {m.allowed_roles.map((r) => (
                      <span key={r} className="badge badge-accent" style={{ marginRight: 6 }}>
                        {r}
                      </span>
                    ))}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {selectedMeta ? (
            <div className="card">
              <h3>Invoke: {selectedMeta.name}</h3>
              {!canRun ? (
                <div className="alert alert-warn">
                  Your role ({user?.role}) cannot run this tool. You will get 403 from the API.
                </div>
              ) : null}
              <form onSubmit={onInvoke}>
                <div className="field">
                  <label htmlFor="args">Arguments (JSON)</label>
                  <textarea
                    id="args"
                    className="textarea mono-block"
                    style={{ minHeight: 180, fontFamily: 'var(--mono)' }}
                    value={argsJson}
                    onChange={(e) => setArgsJson(e.target.value)}
                    spellCheck={false}
                  />
                </div>
                <button type="submit" className="btn btn-primary" disabled={invoking}>
                  {invoking ? 'Running…' : 'Run tool'}
                </button>
              </form>
            </div>
          ) : null}

          {invokeErr ? <div className="alert alert-error">{invokeErr}</div> : null}

          {result ? (
            <div className="card">
              <h3>Response</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                log_id {result.log_id} · {result.duration_ms} ms · {result.success ? 'success' : 'failure'}
              </p>
              {result.error ? <div className="alert alert-error">{result.error}</div> : null}
              {result.output != null ? (
                <pre className="mono-block" style={{ margin: 0 }}>
                  {typeof result.output === 'string'
                    ? result.output
                    : JSON.stringify(result.output, null, 2)}
                </pre>
              ) : null}
            </div>
          ) : null}
        </>
      )}
    </div>
  );
}
