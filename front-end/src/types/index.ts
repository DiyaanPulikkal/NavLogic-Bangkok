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

export interface ScheduleLeg {
  from: string;
  to: string;
  line: string;
  depart: string;
  arrive: string;
}

export interface ScheduleData {
  origin: string;
  destination: string;
  deadline: string;
  itineraries: ScheduleLeg[][];
  answer?: string;
}

export interface ScheduleResponse {
  type: "schedule";
  data: ScheduleData;
}

export interface DayPlanLeg {
  from: string;
  to: string;
  arrive_by: string;
  itineraries: ScheduleLeg[][];
  route?: RouteData | null;
  attractions: string[];
}

export interface DayPlanData {
  origin: string;
  stops: string[];
  legs: DayPlanLeg[];
  answer?: string;
}

export interface DayPlanResponse {
  type: "day_plan";
  data: DayPlanData;
}

export interface NightlifeLeg {
  from: string;
  to: string;
  arrive_by: string;
  route: RouteData | null;
  attractions: string[];
}

export interface NightlifeData {
  origin: string;
  stops: string[];
  legs: NightlifeLeg[];
  start_time: string;
  end_time: string;
  last_train_note: string | null;
  answer?: string;
}

export interface NightlifeResponse {
  type: "nightlife";
  data: NightlifeData;
}

export type ApiRouteResult = RouteResponse | ErrorResponse;
export type ApiResult = RouteResponse | ScheduleResponse | DayPlanResponse | NightlifeResponse | ErrorResponse | { type: "answer"; data: { answer: string } };
