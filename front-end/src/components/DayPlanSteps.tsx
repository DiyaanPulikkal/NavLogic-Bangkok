import { motion } from "framer-motion";
import { MapPin } from "lucide-react";
import type { DayPlanLeg, ScheduleLeg, RouteStep } from "../types";
import { getLineColor, getLineDisplayName } from "../utils/lineColors";
import { useTheme } from "../context/ThemeContext";

interface Props {
  legs: DayPlanLeg[];
  origin: string;
}

export default function DayPlanSteps({ legs, origin }: Props) {
  const { colors } = useTheme();

  return (
    <div className="space-y-3">
      <div className={`text-[11px] font-medium ${colors.textMuted} uppercase tracking-wider`}>
        Day plan from {origin}
      </div>

      {legs.map((leg, i) => (
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

          {/* Transit directions: prefer route (Dijkstra) over itineraries (schedule) */}
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
          ) : leg.itineraries && leg.itineraries.length > 0 ? (
            <div className="mb-3">
              <div className={`text-[11px] font-medium ${colors.textMuted} mb-2 uppercase tracking-wider`}>Transit</div>
              <div className="flex flex-col gap-0">
                {leg.itineraries[0].map((segment, j) => (
                  <LegSegment key={j} segment={segment} />
                ))}
              </div>
            </div>
          ) : (
            <div className={`text-xs ${colors.textMuted} mb-3 italic`}>
              No transit route found for this leg.
            </div>
          )}

          {/* Attractions */}
          {leg.attractions.length > 0 && (
            <div>
              <div className={`text-[11px] font-medium ${colors.textMuted} mb-2 uppercase tracking-wider`}>
                Near {leg.to}
              </div>
              <div className="flex flex-wrap gap-1.5">
                {leg.attractions.map((attr) => (
                  <span
                    key={attr}
                    className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-medium
                               ${colors.cardBg} border ${colors.cardBorder} ${colors.textSecondary}
                               transition-colors hover:border-[#e87722]/30 hover:text-[#e87722]`}
                  >
                    <MapPin size={11} className="opacity-50 flex-shrink-0" />
                    {attr}
                  </span>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      ))}
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

function LegSegment({ segment }: { segment: ScheduleLeg }) {
  const { colors } = useTheme();
  const isTransfer = segment.line.toLowerCase().includes("transfer") || segment.line.toLowerCase().includes("walk");
  const color = isTransfer ? "#f59e0b" : getLineColor(segment.line);

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
            {isTransfer ? "Walk" : segment.line}
          </span>
          <span className={`text-[11px] ${colors.textMuted} tabular-nums`}>
            {segment.depart} → {segment.arrive}
          </span>
        </div>
        <div className={`text-[11px] ${colors.textSecondary} mt-0.5`}>
          {segment.from} → {segment.to}
        </div>
      </div>
    </div>
  );
}
