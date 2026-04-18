import {
  AlertTriangle,
  Clock,
  Info,
  Sparkles,
  ChevronDown,
  Wallet,
  Wrench,
  Ban,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import RouteSteps from "./RouteSteps";
import type {
  BudgetAuditEntry,
  BudgetContext,
  Diagnosis,
  ExploreAlternative,
  FareSegment,
  InfeasibilityCertificate,
  PlanData,
  Repair,
  RepairStep,
  RouteStep,
  TimeContext,
} from "../types";
import { useTheme } from "../context/ThemeContext";

interface Props {
  data: PlanData;
}

const AGENCY_DISPLAY: Record<string, string> = {
  bts: "BTS",
  bem: "MRT",
  srtet: "Airport Rail Link",
};

function agencyLabel(atom: string): string {
  return AGENCY_DISPLAY[atom] ?? atom.toUpperCase();
}

function isExploreAlternatives(
  alts: PlanData["alternatives"]
): alts is ExploreAlternative[] {
  return Array.isArray(alts) && alts.length > 0 && typeof alts[0] !== "string";
}

export default function PlanResult({ data }: Props) {
  const { colors } = useTheme();

  const header = renderHeader(data);
  const exploreAlts = isExploreAlternatives(data.alternatives)
    ? data.alternatives
    : null;
  const stringAlts =
    !exploreAlts && Array.isArray(data.alternatives)
      ? (data.alternatives as string[])
      : null;

  return (
    <div className="space-y-3">
      {header && <div className={`text-sm font-semibold ${colors.text}`}>{header}</div>}

      <div className="flex flex-wrap gap-2">
        {data.time_context && <TimeContextBadge ctx={data.time_context} />}
        {data.budget_context && <BudgetContextBadge ctx={data.budget_context} />}
      </div>

      {data.unknown_tags && data.unknown_tags.length > 0 && (
        <UnknownTagsNotice tags={data.unknown_tags} note={data.note} />
      )}

      {data.relaxation_note && data.relaxation_note.length > 0 && (
        <RelaxationBanner notes={data.relaxation_note} />
      )}

      {data.answer && (
        <div className={`prose-chat text-sm ${colors.text} leading-relaxed`}>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{data.answer}</ReactMarkdown>
        </div>
      )}

      {data.fare_breakdown && data.fare_breakdown.length > 0 && (
        <FareBreakdown
          segments={data.fare_breakdown}
          total={data.total_fare ?? null}
          budget={data.budget_context?.max_thb ?? null}
        />
      )}

      {data.repair_trail && data.repair_trail.length > 0 && (
        <RepairTrailDisclosure trail={data.repair_trail} />
      )}

      {data.steps && data.steps.length > 0 && (
        <RouteSteps steps={data.steps as RouteStep[]} />
      )}

      {data.audit_trail && data.audit_trail.length > 0 && (
        <AuditTrailDisclosure trail={data.audit_trail} />
      )}

      {data.budget_audit && data.budget_audit.length > 0 && (
        <BudgetAuditDisclosure entries={data.budget_audit} />
      )}

      {exploreAlts && <ExploreAlternativesList alternatives={exploreAlts} />}
      {stringAlts && stringAlts.length > 0 && <AlternativesList names={stringAlts} />}
    </div>
  );
}

function renderHeader(data: PlanData): string | null {
  const parts: string[] = [];
  if (data.poi) {
    parts.push(data.poi);
    if (data.destination) parts.push(`(${data.destination})`);
  } else if (data.destination) {
    parts.push(data.destination);
  }
  if (data.origin && (data.destination || data.poi)) {
    const left = data.origin;
    const right = parts.join(" ");
    const bits: string[] = [];
    if (data.total_time != null) bits.push(`~${data.total_time} min`);
    if (data.total_fare != null) bits.push(`฿${data.total_fare}`);
    const tail = bits.length ? ` · ${bits.join(" · ")}` : "";
    return `${left} → ${right}${tail}`;
  }
  return null;
}

function TimeContextBadge({ ctx }: { ctx: TimeContext }) {
  const { colors } = useTheme();
  return (
    <div
      className={`inline-flex items-center gap-1.5 rounded-lg border ${colors.cardBorder} px-2 py-0.5 text-[11px] ${colors.textMuted}`}
    >
      <Clock size={11} />
      Evaluated for {ctx.display}
    </div>
  );
}

function BudgetContextBadge({ ctx }: { ctx: BudgetContext }) {
  return (
    <div className="inline-flex items-center gap-1.5 rounded-lg border border-emerald-400/40 bg-emerald-400/10 px-2 py-0.5 text-[11px] text-emerald-700 dark:text-emerald-300">
      <Wallet size={11} />
      Budget ≤ ฿{ctx.max_thb}
    </div>
  );
}

function RelaxationBanner({ notes }: { notes: string[] }) {
  return (
    <div className="rounded-xl border border-amber-400/40 bg-amber-400/10 px-3 py-2 text-xs text-amber-600 dark:text-amber-300 flex items-start gap-2">
      <Info size={14} className="mt-0.5 flex-shrink-0" />
      <div>
        <p className="font-medium mb-0.5">Relaxed constraints</p>
        <p className="text-amber-700 dark:text-amber-200/90">
          Dropped: {notes.join(", ")}
        </p>
      </div>
    </div>
  );
}

function UnknownTagsNotice({ tags, note }: { tags: string[]; note?: string }) {
  return (
    <div className="rounded-xl border border-blue-400/40 bg-blue-400/10 px-3 py-2 text-xs text-blue-700 dark:text-blue-200 flex items-start gap-2">
      <AlertTriangle size={14} className="mt-0.5 flex-shrink-0" />
      <div>
        <p className="font-medium mb-0.5">
          Unrecognized term{tags.length > 1 ? "s" : ""}: {tags.join(", ")}
        </p>
        {note && <p className="text-blue-700/90 dark:text-blue-200/80">{note}</p>}
      </div>
    </div>
  );
}

function FareBreakdown({
  segments,
  total,
  budget,
}: {
  segments: FareSegment[];
  total: number | null;
  budget: number | null;
}) {
  const { colors } = useTheme();
  const within = budget != null && total != null && total <= budget;
  return (
    <div
      className={`rounded-xl border ${colors.cardBorder} ${colors.cardBg} px-3 py-2.5`}
    >
      <div className="flex items-center justify-between mb-1.5">
        <div className={`text-xs font-medium ${colors.text} flex items-center gap-1.5`}>
          <Wallet size={13} className="text-emerald-500" />
          Fare breakdown
        </div>
        {total != null && (
          <div
            className={`text-xs font-semibold ${
              within
                ? "text-emerald-600 dark:text-emerald-400"
                : colors.text
            }`}
          >
            ฿{total}
            {budget != null && (
              <span className={`ml-1 font-normal ${colors.textMuted}`}>
                / ฿{budget}
              </span>
            )}
          </div>
        )}
      </div>
      <ul className="space-y-1">
        {segments.map((seg, i) => (
          <li
            key={i}
            className={`flex items-center justify-between text-xs ${colors.textSecondary}`}
          >
            <div className="flex items-center gap-2 min-w-0">
              <span className="inline-block px-1.5 py-0.5 rounded-md bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 text-[10px] font-semibold tracking-wide flex-shrink-0">
                {agencyLabel(seg.agency)}
              </span>
              <span className="truncate">
                {seg.tap_in === seg.tap_out
                  ? seg.tap_in
                  : `${seg.tap_in} → ${seg.tap_out}`}
              </span>
            </div>
            <span className={`${colors.text} font-medium ml-2 flex-shrink-0`}>
              ฿{seg.fare}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function RepairTrailDisclosure({ trail }: { trail: RepairStep[] }) {
  const { colors } = useTheme();
  return (
    <details
      className={`rounded-xl border ${colors.cardBorder} ${colors.cardBg} px-3 py-2`}
    >
      <summary
        className={`text-xs ${colors.textSecondary} cursor-pointer flex items-center gap-1.5`}
      >
        <Wrench size={12} className="text-emerald-500" />
        Reasoning chain — {trail.length} repair{trail.length > 1 ? "s" : ""}{" "}
        applied
      </summary>
      <ol className="mt-2 space-y-2">
        {trail.map((step, i) => (
          <li
            key={i}
            className={`text-xs ${colors.textSecondary} border-l-2 border-emerald-500/40 pl-2`}
          >
            <p>
              <span className={`font-medium ${colors.text}`}>Step {i + 1}.</span>{" "}
              {describeDiagnosis(step.diagnosis)}
            </p>
            <p className={`${colors.textMuted} mt-0.5`}>
              Applied: {describeRepair(step.repair_applied)}
            </p>
          </li>
        ))}
      </ol>
    </details>
  );
}

function describeDiagnosis(d: Diagnosis): string {
  if (d.kind === "within_budget") return `Within budget (฿${d.total}).`;
  const boundaryNames = d.boundaries
    .map((b) => `${b.a}↔${b.b}`)
    .join(", ");
  const crossings = d.boundaries.length
    ? ` crossing ${boundaryNames}`
    : "";
  return `Path costs ฿${d.total}, over by ฿${d.overage}${crossings}.`;
}

function describeRepair(r: Repair): string {
  switch (r.kind) {
    case "avoid_specific_boundary":
      return `avoid the ${r.a} ↔ ${r.b} crossing`;
    case "avoid_agency_pair":
      return `avoid all ${agencyLabel(r.a)} ↔ ${agencyLabel(r.b)} crossings`;
    case "force_single_agency":
      return `stay entirely on ${agencyLabel(r.agency)}`;
    case "infeasible":
      return `infeasible${r.reason ? ` (${r.reason})` : ""}`;
  }
}

function AuditTrailDisclosure({
  trail,
}: {
  trail: { candidate: string; violations: { reason: string }[] }[];
}) {
  const { colors } = useTheme();
  return (
    <details className={`rounded-xl border ${colors.cardBorder} ${colors.cardBg} px-3 py-2`}>
      <summary
        className={`text-xs ${colors.textMuted} cursor-pointer flex items-center gap-1.5`}
      >
        <ChevronDown size={12} />
        Why other candidates were skipped ({trail.length})
      </summary>
      <ul className="mt-2 space-y-1">
        {trail.map((entry, i) => (
          <li key={i} className={`text-xs ${colors.textSecondary}`}>
            <span className="font-medium">{entry.candidate}</span> rejected:{" "}
            {entry.violations.map((v) => v.reason).join(", ")}
          </li>
        ))}
      </ul>
    </details>
  );
}

function BudgetAuditDisclosure({ entries }: { entries: BudgetAuditEntry[] }) {
  const { colors } = useTheme();
  return (
    <details
      className={`rounded-xl border border-rose-400/30 bg-rose-400/5 px-3 py-2`}
    >
      <summary
        className={`text-xs text-rose-700 dark:text-rose-300 cursor-pointer flex items-center gap-1.5`}
      >
        <Ban size={12} />
        Proved unreachable within budget ({entries.length})
      </summary>
      <ul className="mt-2 space-y-2">
        {entries.map((e, i) => (
          <li key={i} className={`text-xs ${colors.textSecondary}`}>
            <p>
              <span className={`font-medium ${colors.text}`}>{e.candidate}</span>{" "}
              — {describeCertificate(e.certificate)}
            </p>
            {e.repair_trail.length > 0 && (
              <p className={`${colors.textMuted} mt-0.5`}>
                Tried:{" "}
                {e.repair_trail
                  .map((s) => describeRepair(s.repair_applied))
                  .join(" → ")}
              </p>
            )}
          </li>
        ))}
      </ul>
    </details>
  );
}

function describeCertificate(cert: InfeasibilityCertificate): string {
  if (cert.fare_unknown) {
    const fu = cert.fare_unknown;
    return `fare data missing for ${agencyLabel(fu.agency)} (${fu.origin} → ${fu.destination}).`;
  }
  if (cert.graph_disconnected) {
    return "graph disconnected after all repairs — no path survives.";
  }
  if (cert.final_over_by != null) {
    const seen = cert.min_seen != null ? ` (best seen: ฿${cert.min_seen})` : "";
    return `still over budget by ฿${cert.final_over_by}${seen}.`;
  }
  return "no repair succeeded.";
}

function ExploreAlternativesList({
  alternatives,
}: {
  alternatives: ExploreAlternative[];
}) {
  const { colors } = useTheme();
  return (
    <div className="space-y-2">
      <div className={`flex items-center gap-2 ${colors.textMuted}`}>
        <Sparkles size={14} />
        <span className="text-xs">
          {alternatives.length} place{alternatives.length > 1 ? "s" : ""} you can
          reach
        </span>
      </div>
      <ul className="space-y-2">
        {alternatives.map((alt, i) => (
          <li
            key={i}
            className={`rounded-xl border ${colors.cardBorder} ${colors.cardBg}`}
          >
            <details>
              <summary
                className={`flex items-center justify-between px-3 py-2 cursor-pointer text-sm ${colors.text}`}
              >
                <div className="min-w-0 flex-1">
                  <span className="font-medium">{alt.name}</span>
                  <span className={`ml-2 text-xs ${colors.textMuted}`}>
                    {alt.station}
                  </span>
                </div>
                <div className={`text-xs ${colors.textSecondary} flex-shrink-0 ml-2`}>
                  ~{alt.total_time} min
                  {alt.total_fare != null && (
                    <span className="ml-2">฿{alt.total_fare}</span>
                  )}
                </div>
              </summary>
              <div className="px-3 pb-3 space-y-2">
                {alt.fare_breakdown && alt.fare_breakdown.length > 0 && (
                  <FareBreakdown
                    segments={alt.fare_breakdown}
                    total={alt.total_fare ?? null}
                    budget={null}
                  />
                )}
                {alt.repair_trail && alt.repair_trail.length > 0 && (
                  <RepairTrailDisclosure trail={alt.repair_trail} />
                )}
                {alt.steps && alt.steps.length > 0 && (
                  <RouteSteps steps={alt.steps} />
                )}
              </div>
            </details>
          </li>
        ))}
      </ul>
    </div>
  );
}

function AlternativesList({ names }: { names: string[] }) {
  const { colors } = useTheme();
  return (
    <div className="flex items-center gap-2 flex-wrap">
      <Sparkles size={14} className={colors.textMuted} />
      <span className={`text-xs ${colors.textMuted}`}>Also worth a look:</span>
      {names.map((n) => (
        <span
          key={n}
          className={`text-xs px-2 py-0.5 rounded-lg border ${colors.cardBorder} ${colors.textSecondary}`}
        >
          {n}
        </span>
      ))}
    </div>
  );
}
