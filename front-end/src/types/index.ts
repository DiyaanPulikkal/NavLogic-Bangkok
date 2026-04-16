export interface StationInfo {
  name: string;
  lines: string[];
}

export interface AttractionInfo {
  name: string;
  station: string;
  tags: string[];
}

export interface RouteStep {
  type: "ride" | "transfer";
  line?: string;
  board?: string;
  alight?: string;
  stations?: string[];
  from?: string;
  to?: string;
}

export interface RouteData {
  origin: string;
  destination: string;
  total_time: number;
  steps: RouteStep[];
}

export interface RouteResponse {
  type: "plan";
  data: RouteData;
}

export interface ErrorResponse {
  type: "error";
  data: { message: string };
}

export interface AuditEntry {
  candidate: string;
  violations: { step: RouteStep; reason: string }[];
}

export interface TimeContext {
  weekday: string;
  hour: number;
  minute: number;
  display: string;
}

export interface PlanData {
  origin: string;
  destination?: string;
  poi?: string;
  total_time?: number;
  steps?: RouteStep[];
  preference_score?: number;
  time_context?: TimeContext | null;
  relaxation_note?: string[] | null;
  audit_trail?: AuditEntry[] | null;
  alternatives?: string[] | null;
  unknown_tags?: string[];
  note?: string;
  answer?: string;
}

export interface PlanResponse {
  type: "plan";
  data: PlanData;
}

export interface AnswerResponse {
  type: "answer";
  data: { answer: string };
}

export type ApiRouteResult = RouteResponse | ErrorResponse;
export type QueryResponse = PlanResponse | AnswerResponse | ErrorResponse;
export type ApiResult = QueryResponse;
