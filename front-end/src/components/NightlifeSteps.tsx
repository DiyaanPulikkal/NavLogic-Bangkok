import { motion } from "framer-motion";
import { MapPin, Moon, AlertTriangle } from "lucide-react";
import type { RouteData, RouteStep } from "../types";
import { getLineColor, getLineDisplayName } from "../utils/lineColors";
import { useTheme } from "../context/ThemeContext";

interface NightlifeLeg {
  from: string;
  to: string;
  arrive_by: string;
  route: RouteData | null;
  attractions: string[];
}

interface NightlifeData {
  origin: string;
  stops: string[];
  legs: NightlifeLeg[];
  start_time: string;
  end_time: string;
  last_train_note: string | null;
  answer?: string;
}

interface Props {
  data: NightlifeData;
  mode?: "nightlife" | "explore";
}

export default function NightlifeSteps({ data, mode = "nightlife" }: Props) {
  const { colors } = useTheme();
  const isExplore = mode === "explore";
  const Icon = isExplore ? MapPin : Moon;
  const label = isExplore ? "Explore plan" : "Nightlife plan";
  const venueLabel = isExplore ? "Near" : "Venues near";

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Icon size={14} className="text-[#e87722]" />
        <span className={`text-[11px] font-medium ${colors.textMuted} uppercase tracking-wider`}>
          {label} from {data.origin}
        </span>
        <span className={`text-[11px] ${colors.textMuted} ml-auto tabular-nums`}>
          {data.start_time} — {data.end_time}
        </span>
      </div>

      {data.legs.map((leg, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.12, duration: 0.35, ease: [0.23, 1, 0.32, 1] }}
          className={`${colors.cardBg} rounded-xl border ${colors.cardBorder} p-4 transition-colors ${colors.cardHover}`}
        >
          {/* Leg header */}
          <div className="flex items-center gap-2.5 mb-3">
            <span className="inline-flex items-center justify-center w-6 h-6 rounded-lg bg-[#e87722] text-white text-xs font-bold">
              {i + 1}
            </span>
            <span className={`text-sm font-semibold ${colors.text} tracking-tight`}>
              {leg.from} → {leg.to}
            </span>
            <span className={`text-xs ${colors.textMuted} ml-auto tabular-nums`}>
              by {leg.arrive_by}
            </span>
          </div>

          {/* Route directions */}
          {leg.route ? (
            <div className="mb-3">
              <div className={`text-[11px] font-medium ${colors.textMuted} mb-2 uppercase tracking-wider`}>
                Transit — ~{leg.route.total_time} min
              </div>
              <div className="flex flex-col gap-0">
                {leg.route.steps.map((step, j) => (
                  <CompactRouteStep key={j} step={step} />
                ))}
              </div>
            </div>
          ) : (
            <div className={`text-xs ${colors.textMuted} mb-3 italic`}>
              No transit route found for this leg.
            </div>
          )}

          {/* Nightlife venues */}
          {leg.attractions.length > 0 && (
            <div>
              <div className={`text-[11px] font-medium ${colors.textMuted} mb-2 uppercase tracking-wider`}>
                {venueLabel} {leg.to}
              </div>
              <div className="flex flex-wrap gap-1.5">
                {leg.attractions.map((venue) => (
                  <span
                    key={venue}
                    className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-medium
                               ${colors.cardBg} border ${colors.cardBorder} ${colors.textSecondary}
                               transition-colors hover:border-[#e87722]/30 hover:text-[#e87722]`}
                  >
                    <MapPin size={11} className="opacity-50 flex-shrink-0" />
                    {venue}
                  </span>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      ))}

      {/* Last train warning */}
      {data.last_train_note && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: data.legs.length * 0.12 + 0.2 }}
          className="flex items-start gap-2.5 px-4 py-3 rounded-xl bg-amber-500/10 border border-amber-500/20"
        >
          <AlertTriangle size={14} className="text-amber-500 mt-0.5 flex-shrink-0" />
          <p className="text-xs text-amber-600 dark:text-amber-400 leading-relaxed">
            {data.last_train_note}
          </p>
        </motion.div>
      )}
    </div>
  );
}

function CompactRouteStep({ step }: { step: RouteStep }) {
  const { colors } = useTheme();

  if (step.type === "transfer") {
    return (
      <div className="flex gap-3 items-stretch">
        <div className="flex flex-col items-center w-5">
          <div className="w-2.5 h-2.5 rounded-full bg-amber-400 border-2 border-white shadow-sm flex-shrink-0" />
          <div className="flex-1 w-0.5 min-h-5 bg-amber-400/30" />
        </div>
        <div className="flex-1 pb-2">
          <span className="inline-block px-1.5 py-0.5 rounded-md text-[10px] font-semibold text-white bg-amber-400">
            Walk
          </span>
          <div className={`text-[11px] ${colors.textSecondary} mt-0.5`}>
            {step.from} → {step.to}
          </div>
        </div>
      </div>
    );
  }

  const color = getLineColor(step.line ?? "");
  return (
    <div className="flex gap-3 items-stretch">
      <div className="flex flex-col items-center w-5">
        <div
          className="w-2.5 h-2.5 rounded-full border-2 border-white shadow-sm flex-shrink-0"
          style={{ backgroundColor: color }}
        />
        <div
          className="flex-1 w-0.5 min-h-5"
          style={{ backgroundColor: color, opacity: 0.3 }}
        />
      </div>
      <div className="flex-1 pb-2">
        <div className="flex items-center gap-2">
          <span
            className="inline-block px-1.5 py-0.5 rounded-md text-[10px] font-semibold text-white"
            style={{ backgroundColor: color }}
          >
            {getLineDisplayName(step.line ?? "")}
          </span>
          {step.stations && step.stations.length > 2 && (
            <span className={`text-[10px] ${colors.textMuted}`}>
              {(step.stations?.length ?? 1) - 1} stops
            </span>
          )}
        </div>
        <div className={`text-[11px] ${colors.textSecondary} mt-0.5`}>
          {step.board} → {step.alight}
        </div>
      </div>
    </div>
  );
}
