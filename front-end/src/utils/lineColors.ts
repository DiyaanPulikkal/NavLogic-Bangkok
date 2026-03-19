const LINE_COLORS: Record<string, string> = {
  bts_sukhumvit: "#5a9a2f",
  bts_silom: "#8b6914",
  mrt_blue: "#1a3c8f",
  mrt_purple: "#6b2fa0",
  arl: "#c4161c",
  brt: "#e87722",
  srt_dark_red: "#8b1a1a",
  srt_light_red: "#d44a4a",
  // Display name variants (used by schedule results from Prolog)
  "BTS Sukhumvit Line": "#5a9a2f",
  "BTS Silom Line": "#8b6914",
  "MRT Blue Line": "#1a3c8f",
  "BTS Gold Line": "#d4a017",
  "Airport Rail Link": "#c4161c",
  "Transfer (Walk)": "#f59e0b",
};

const LINE_DISPLAY_NAMES: Record<string, string> = {
  bts_sukhumvit: "BTS Sukhumvit",
  bts_silom: "BTS Silom",
  mrt_blue: "MRT Blue",
  mrt_purple: "MRT Purple",
  arl: "Airport Rail Link",
  brt: "BRT",
  srt_dark_red: "SRT Dark Red",
  srt_light_red: "SRT Light Red",
};

export function getLineColor(line: string): string {
  return LINE_COLORS[line] ?? "#6b7280";
}

export function getLineDisplayName(line: string): string {
  return LINE_DISPLAY_NAMES[line] ?? line;
}
