import { motion } from "framer-motion";
import type { DayPlanLeg, ScheduleLeg } from "../types";
import { getLineColor } from "../utils/lineColors";
import { useTheme } from "../context/ThemeContext";

interface Props {
  legs: DayPlanLeg[];
  origin: string;
}

export default function DayPlanSteps({ legs, origin }: Props) {
  const { colors } = useTheme();

  return (
    <div className="space-y-4">
      <div className={`text-xs font-semibold ${colors.textMuted} uppercase tracking-wide`}>
        Day Plan from {origin}
      </div>

      {legs.map((leg, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.15, duration: 0.3 }}
          className={`${colors.cardBg} rounded-xl border ${colors.cardBorder} p-4`}
        >
          {/* Leg header */}
          <div className={`flex items-center gap-2 mb-3`}>
            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-orange-500 text-white text-xs font-bold">
              {i + 1}
            </span>
            <span className={`text-sm font-medium ${colors.text}`}>
              {leg.from} → {leg.to}
            </span>
            <span className={`text-xs ${colors.textMuted} ml-auto`}>
              arrive by {leg.arrive_by}
            </span>
          </div>

          {/* Transit itinerary (show best option) */}
          {leg.itineraries.length > 0 ? (
            <div className="mb-3">
              <div className={`text-xs font-semibold ${colors.textMuted} mb-2`}>Transit</div>
              <div className="flex flex-col gap-0">
                {leg.itineraries[0].map((segment, j) => (
                  <LegSegment key={j} segment={segment} index={j} />
                ))}
              </div>
            </div>
          ) : (
            <div className={`text-xs ${colors.textMuted} mb-3 italic`}>
              No scheduled transit found for this leg.
            </div>
          )}

          {/* Attractions */}
          {leg.attractions.length > 0 && (
            <div>
              <div className={`text-xs font-semibold ${colors.textMuted} mb-2`}>
                Things to do near {leg.to}
              </div>
              <div className="flex flex-wrap gap-1.5">
                {leg.attractions.map((attr) => (
                  <span
                    key={attr}
                    className={`inline-block px-2 py-1 rounded-full text-[11px] font-medium
                               ${colors.cardBg} border ${colors.cardBorder} ${colors.textSecondary}`}
                  >
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

function LegSegment({ segment, index }: { segment: ScheduleLeg; index: number }) {
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
          style={{ backgroundColor: color, opacity: 0.4 }}
        />
      </div>
      <div className="flex-1 pb-2">
        <div className="flex items-center gap-2">
          <span
            className="inline-block px-1.5 py-0.5 rounded text-[10px] font-semibold text-white"
            style={{ backgroundColor: color }}
          >
            {isTransfer ? "Walk" : segment.line}
          </span>
          <span className={`text-[11px] ${colors.textMuted}`}>
            {segment.depart} → {segment.arrive}
          </span>
        </div>
        <div className={`text-[11px] ${colors.textSecondary}`}>
          {segment.from} → {segment.to}
        </div>
      </div>
    </div>
  );
}
