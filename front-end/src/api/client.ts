import type { StationInfo, AttractionInfo, ApiRouteResult } from "../types";

const BASE = "/api";

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function fetchStations(): Promise<StationInfo[]> {
  const res = await fetch(`${BASE}/stations`);
  if (!res.ok) throw new Error("Failed to fetch stations");
  return res.json();
}

export async function fetchAttractions(): Promise<AttractionInfo[]> {
  const res = await fetch(`${BASE}/attractions`);
  if (!res.ok) throw new Error("Failed to fetch attractions");
  return res.json();
}

export async function fetchRoute(
  start: string,
  end: string
): Promise<ApiRouteResult> {
  const params = new URLSearchParams({ start, end });
  const res = await fetch(`${BASE}/route?${params}`);
  if (!res.ok) throw new Error("Failed to fetch route");
  return res.json();
}

export interface QueryResponse {
  type: "route" | "answer" | "error";
  data: Record<string, unknown>;
}

export async function postQuery(
  message: string,
  conversationId: number
): Promise<QueryResponse> {
  const res = await fetch(`${BASE}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ message, conversation_id: conversationId }),
  });
  if (!res.ok) throw new Error("Failed to send query");
  return res.json();
}

// ── Conversations ──

export interface ConversationInfo {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export async function listConversations(): Promise<ConversationInfo[]> {
  const res = await fetch(`${BASE}/conversations`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Failed to list conversations");
  return res.json();
}

export async function createConversation(
  title: string = "New conversation"
): Promise<ConversationInfo> {
  const res = await fetch(`${BASE}/conversations`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error("Failed to create conversation");
  return res.json();
}

export interface ConversationDetail extends ConversationInfo {
  messages: { id: number; role: string; content: string; created_at: string }[];
}

export async function getConversation(id: number): Promise<ConversationDetail> {
  const res = await fetch(`${BASE}/conversations/${id}`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Failed to get conversation");
  return res.json();
}

export async function deleteConversation(id: number): Promise<void> {
  const res = await fetch(`${BASE}/conversations/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Failed to delete conversation");
}
