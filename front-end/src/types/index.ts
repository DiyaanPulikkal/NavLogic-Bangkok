export interface StationInfo {
  name: string;
  lines: string[];
}

export interface AttractionInfo {
  name: string;
  station: string;
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
  from: string;
  to: string;
  total_time: number;
  steps: RouteStep[];
}

export interface RouteResponse {
  type: "route";
  data: RouteData;
}

export interface ErrorResponse {
  type: "error";
  data: { message: string };
}

export type ApiRouteResult = RouteResponse | ErrorResponse;
