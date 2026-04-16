import { AlertTriangle, Clock, Info, Sparkles, ChevronDown } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import RouteSteps from "./RouteSteps";
import type { PlanData, RouteStep, TimeContext } from "../types";
import { useTheme } from "../context/ThemeContext";

interface Props {
  data: PlanData;
}

export default function PlanResult({ data }: Props) {
  const { colors } = useTheme();

  const header = renderHeader(data);

  return (
    <div className="space-y-3">
      {header && <div className={`text-sm font-semibold ${colors.text}`}>{header}</div>}

      {data.time_context && <TimeContextBadge ctx={data.time_context} />}

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

      {data.steps && data.steps.length > 0 && (
        <RouteSteps steps={data.steps as RouteStep[]} />
      )}

      {data.audit_trail && data.audit_trail.length > 0 && (
        <AuditTrailDisclosure trail={data.audit_trail} />
      )}

      {data.alternatives && data.alternatives.length > 0 && (
        <AlternativesList names={data.alternatives} />
      )}
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
    const time = data.total_time != null ? ` · ~${data.total_time} min` : "";
    return `${left} → ${right}${time}`;
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
