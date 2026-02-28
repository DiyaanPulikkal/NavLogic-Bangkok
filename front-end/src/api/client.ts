import type { StationInfo, AttractionInfo, ApiRouteResult } from "../types";

const BASE = "/api";

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

export async function postQuery(message: string): Promise<QueryResponse> {
  const res = await fetch(`${BASE}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error("Failed to send query");
  return res.json();
}
