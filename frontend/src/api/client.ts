import type { PdfUploadResponse } from './types';

const API_PREFIX = '/api/v1';

function baseUrl(): string {
  return import.meta.env.VITE_API_BASE_URL ?? '';
}

export function apiPath(path: string): string {
  const p = path.startsWith('/') ? path : `/${path}`;
  return `${baseUrl()}${API_PREFIX}${p}`;
}

const TOKEN_KEY = 'rag_access_token';

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token: string | null): void {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

async function parseErrorDetail(res: Response): Promise<string> {
  try {
    const data = (await res.json()) as { detail?: unknown };
    if (typeof data.detail === 'string') return data.detail;
    if (Array.isArray(data.detail)) {
      return data.detail.map((e) => JSON.stringify(e)).join('; ');
    }
    return res.statusText || `HTTP ${res.status}`;
  } catch {
    return res.statusText || `HTTP ${res.status}`;
  }
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

type Json = Record<string, unknown> | unknown[] | string | number | boolean | null;

export async function apiFetch<T>(
  path: string,
  options: RequestInit & { json?: Json; form?: URLSearchParams; token?: string | null } = {},
): Promise<T> {
  const { json, form, token, headers: hdrs, body: initBody, ...rest } = options;
  const headers = new Headers(hdrs);
  const auth = token !== undefined ? token : getStoredToken();
  if (auth) headers.set('Authorization', `Bearer ${auth}`);

  let body: BodyInit | undefined =
    initBody === undefined || initBody === null ? undefined : initBody;
  if (json !== undefined) {
    headers.set('Content-Type', 'application/json');
    body = JSON.stringify(json);
  } else if (form !== undefined) {
    headers.set('Content-Type', 'application/x-www-form-urlencoded');
    body = form.toString();
  }

  const res = await fetch(apiPath(path), { ...rest, headers, body });
  if (!res.ok) {
    throw new ApiError(await parseErrorDetail(res), res.status);
  }
  if (res.status === 204) {
    return undefined as T;
  }
  const ct = res.headers.get('content-type');
  if (ct?.includes('application/json')) {
    return (await res.json()) as T;
  }
  return (await res.text()) as T;
}

export async function uploadPdf(file: File, token?: string | null): Promise<PdfUploadResponse> {
  const auth = token !== undefined ? token : getStoredToken();
  const fd = new FormData();
  fd.append('file', file);
  const headers: HeadersInit = {};
  if (auth) headers.Authorization = `Bearer ${auth}`;
  const res = await fetch(apiPath('/pdf/upload'), { method: 'POST', headers, body: fd });
  if (!res.ok) {
    throw new ApiError(await parseErrorDetail(res), res.status);
  }
  return (await res.json()) as PdfUploadResponse;
}

export async function downloadPdfDocument(documentId: number, fallbackName?: string | null): Promise<void> {
  const auth = getStoredToken();
  const headers: HeadersInit = {};
  if (auth) headers.Authorization = `Bearer ${auth}`;
  const res = await fetch(apiPath(`/pdf/documents/${documentId}/download`), { headers });
  if (!res.ok) {
    throw new ApiError(await parseErrorDetail(res), res.status);
  }
  const blob = await res.blob();
  let name = fallbackName?.trim() || `document-${documentId}.pdf`;
  if (!name.toLowerCase().endsWith('.pdf')) {
    name = `${name}.pdf`;
  }
  const cd = res.headers.get('Content-Disposition');
  if (cd) {
    const star = /filename\*=UTF-8''([^;\n]+)/i.exec(cd);
    const plain = /filename="([^"]+)"/i.exec(cd);
    const raw = star?.[1] ?? plain?.[1];
    if (raw) {
      try {
        name = decodeURIComponent(raw.trim());
      } catch {
        name = raw.trim();
      }
    }
  }
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = name;
  a.rel = 'noopener';
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
