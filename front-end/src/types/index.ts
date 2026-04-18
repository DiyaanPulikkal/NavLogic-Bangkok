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

export interface BudgetContext {
  max_thb: number;
}

export interface FareSegment {
  agency: string;
  tap_in: string;
  tap_out: string;
  fare: number;
}

export interface Boundary {
  a: string;
  b: string;
  agency_a: string;
  agency_b: string;
}

export type Diagnosis =
  | { kind: "within_budget"; total: number }
  | {
      kind: "over_budget";
      total: number;
      overage: number;
      segments: FareSegment[];
      boundaries: Boundary[];
    };

export type Repair =
  | { kind: "avoid_specific_boundary"; a: string; b: string }
  | { kind: "avoid_agency_pair"; a: string; b: string }
  | { kind: "force_single_agency"; agency: string }
  | { kind: "infeasible"; reason?: string };

export interface RepairStep {
  diagnosis: Diagnosis;
  repair_applied: Repair;
}

export interface InfeasibilityCertificate {
  kind?: string;
  repairs_exhausted?: Repair[];
  final_over_by?: number;
  min_seen?: number;
  graph_disconnected?: boolean;
  fare_unknown?: { agency: string; origin: string; destination: string };
  raw?: string;
  [key: string]: unknown;
}

export interface BudgetAuditEntry {
  candidate: string;
  certificate: InfeasibilityCertificate;
  repair_trail: RepairStep[];
}

export interface ExploreAlternative {
  name: string;
  station: string;
  total_time: number;
  steps: RouteStep[];
  preference_score?: number;
  total_fare?: number;
  fare_breakdown?: FareSegment[];
  repair_trail?: RepairStep[];
}

export interface PlanData {
  origin: string;
  destination?: string;
  poi?: string;
  total_time?: number;
  steps?: RouteStep[];
  preference_score?: number;
  time_context?: TimeContext | null;
  budget_context?: BudgetContext | null;
  total_fare?: number | null;
  fare_breakdown?: FareSegment[] | null;
  repair_trail?: RepairStep[] | null;
  budget_audit?: BudgetAuditEntry[] | null;
  relaxation_note?: string[] | null;
  audit_trail?: AuditEntry[] | null;
  alternatives?: ExploreAlternative[] | string[] | null;
  explore?: boolean | null;
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
