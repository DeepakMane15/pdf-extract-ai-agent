export type UserRole = 'admin' | 'user' | 'auditor';

export interface UserRead {
  id: number;
  email: string;
  full_name: string | null;
  role: UserRole;
  is_active: boolean;
}

/** Response from GET /users/me */
export interface UserMe extends UserRead {
  openai_key_configured: boolean;
  openai_key_hint: string | null;
  server_openai_configured: boolean;
  openai_embed_prompt_tokens_total: number;
  openai_chat_prompt_tokens_total: number;
  openai_chat_completion_tokens_total: number;
  openai_tokens_grand_total: number;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface SearchHit {
  chunk_id: number;
  document_id: number;
  document_original_filename?: string | null;
  chunk_text: string;
  page_number: number | null;
  cosine_distance: number;
  rerank_score: number | null;
}

export interface SearchResponse {
  results: SearchHit[];
}

export interface SourceCitation {
  chunk_id: number;
  document_id: number;
  page_number: number | null;
  cosine_distance: number;
  rerank_score: number | null;
  excerpt: string;
}

export interface ChatAskResponse {
  answer: string;
  sources: SourceCitation[];
  cited_chunk_ids: number[];
}

export interface PdfUploadResponse {
  document_id: number;
  original_filename: string | null;
  stored_filename: string;
  content_type: string | null;
  size_bytes: number;
  extracted_char_count: number | null;
  cleaned_char_count: number | null;
  chunk_count: number;
  processing_error: string | null;
}

export interface ToolMeta {
  name: string;
  description: string;
  allowed_roles: string[];
  input_schema: Record<string, unknown>;
}

export interface ToolInvokeResponse {
  success: boolean;
  output: unknown;
  error: string | null;
  duration_ms: number;
  log_id: number;
}

export interface HealthResponse {
  status: string;
}

export interface PdfDocumentListItem {
  id: number;
  original_filename: string | null;
  stored_filename: string;
  file_size_bytes: number;
  chunk_count: number;
  processing_error: string | null;
  created_at: string;
}
