const BASE_URL = "http://localhost:8000";

function authHeaders(token: string | null): Record<string, string> {
  const headers: Record<string, string> = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

// ─── Auth ───────────────────────────────────────────────────────────────────

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
}

export async function login(
  _token: string | null,
  credentials: LoginRequest
): Promise<LoginResponse> {
  const response = await fetch(`${BASE_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(credentials),
  });
  if (!response.ok) {
    throw new ApiError(response.status, `Login failed: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

// ─── Documents ──────────────────────────────────────────────────────────────

export interface DocumentResponse {
  id: string;
  filename: string;
  doc_type: string;
  page_count: number | null;
  upload_status: string;
  uploaded_at: string;
  processed_at: string | null;
  error_message: string | null;
}

export async function listDocuments(token: string | null): Promise<DocumentResponse[]> {
  const response = await fetch(`${BASE_URL}/api/v1/documents`, {
    headers: authHeaders(token),
  });
  if (!response.ok) {
    throw new ApiError(response.status, `Failed to list documents: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

export interface UploadDocumentResponse {
  document_id: string;
  status: string;
}

export async function uploadDocument(
  token: string | null,
  file: File,
  docType: string
): Promise<UploadDocumentResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("doc_type", docType);

  const response = await fetch(`${BASE_URL}/api/v1/documents/upload`, {
    method: "POST",
    headers: authHeaders(token),
    body: formData,
  });
  if (!response.ok) {
    throw new ApiError(response.status, `Upload failed: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

export interface DocumentPageResponse {
  document_id: string;
  page_number: number;
  text: string;
  image_url: string;
  page_count: number;
}

export async function getDocumentPage(
  token: string | null,
  documentId: string,
  pageNumber: number
): Promise<DocumentPageResponse> {
  const response = await fetch(
    `${BASE_URL}/api/v1/documents/${documentId}/page/${pageNumber}`,
    {
      headers: authHeaders(token),
    }
  );
  if (!response.ok) {
    throw new ApiError(response.status, `Failed to load page: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

// ─── Chat ───────────────────────────────────────────────────────────────────

export interface ChatRequest {
  query: string;
}

export interface ChatCitation {
  index: number;
  document_filename: string;
  page_number: number | null;
  content: string;
  score: number;
  document_id: string;
}

export interface ChatResponse {
  answer: string;
  citations: ChatCitation[];
}

export async function sendChatMessage(
  token: string | null,
  query: string
): Promise<ChatResponse> {
  const response = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(token),
    },
    body: JSON.stringify({ query }),
  });
  if (!response.ok) {
    throw new ApiError(response.status, `Chat request failed: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

// ─── Conversations ──────────────────────────────────────────────────────────

export interface ConversationResponse {
  id: string;
  user_id: string;
  created_at: string;
}

export async function createConversation(
  token: string | null
): Promise<ConversationResponse> {
  const response = await fetch(`${BASE_URL}/api/v1/conversations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(token),
    },
    body: JSON.stringify({}),
  });
  if (!response.ok) {
    throw new ApiError(
      response.status,
      `Failed to create conversation: ${response.status} ${response.statusText}`
    );
  }
  return response.json();
}

export interface ConversationMessageResponse {
  id: string;
  conversation_id: string;
  role: "user" | "assistant";
  content: string;
  citations: Record<string, { document_id?: string | null; filename: string; page_number: number }> | null;
  created_at: string;
}

export async function getConversationMessages(
  token: string | null,
  conversationId: string
): Promise<ConversationMessageResponse[]> {
  const response = await fetch(
    `${BASE_URL}/api/v1/conversations/${conversationId}/messages`,
    {
      headers: authHeaders(token),
    }
  );
  if (!response.ok) {
    throw new ApiError(
      response.status,
      `Failed to fetch messages: ${response.status} ${response.statusText}`
    );
  }
  return response.json();
}

export interface MessageCitationEntry {
  document_id: string | null;
  filename: string;
  page_number: number;
}

export interface PersistMessageRequest {
  role: "user" | "assistant";
  content: string;
  citations: Record<string, MessageCitationEntry> | null;
}

export async function persistMessage(
  token: string | null,
  conversationId: string,
  payload: PersistMessageRequest
): Promise<ConversationMessageResponse> {
  const response = await fetch(
    `${BASE_URL}/api/v1/conversations/${conversationId}/messages`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(token),
      },
      body: JSON.stringify(payload),
    }
  );
  if (!response.ok) {
    throw new ApiError(
      response.status,
      `Failed to persist message: ${response.status} ${response.statusText}`
    );
  }
  return response.json();
}
