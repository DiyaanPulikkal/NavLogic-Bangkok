import { motion } from "framer-motion";
import type { ScheduleLeg } from "../types";
import { getLineColor } from "../utils/lineColors";
import { useTheme } from "../context/ThemeContext";

interface Props {
  itineraries: ScheduleLeg[][];
  origin: string;
  destination: string;
  deadline: string;
}

export default function ScheduleSteps({ itineraries, origin, destination, deadline }: Props) {
  const { colors } = useTheme();

  return (
    <div className="space-y-4">
      <div className={`text-sm font-medium ${colors.text}`}>
        {origin} → {destination}
        <span className={`ml-2 text-xs ${colors.textMuted}`}>arrive by {deadline}</span>
      </div>

      {itineraries.map((legs, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1, duration: 0.3 }}
          className={`${colors.cardBg} rounded-xl border ${colors.cardBorder} p-4`}
        >
          <div className={`text-xs font-semibold ${colors.textMuted} mb-3`}>
            Option {i + 1}
          </div>

          <div className="flex flex-col gap-0">
            {legs.map((leg, j) => (
              <LegStep key={j} leg={leg} index={j} />
            ))}
          </div>

          {legs.length > 0 && (
            <div className={`mt-3 pt-2 border-t ${colors.cardBorder} flex justify-between text-xs ${colors.textMuted}`}>
              <span>Depart {legs[0].depart}</span>
              <span>Arrive {legs[legs.length - 1].arrive}</span>
            </div>
          )}
        </motion.div>
      ))}
    </div>
  );
}

function LegStep({ leg, index }: { leg: ScheduleLeg; index: number }) {
  const { colors } = useTheme();
  const isTransfer = leg.line.toLowerCase().includes("transfer") || leg.line.toLowerCase().includes("walk");
  const color = isTransfer ? "#f59e0b" : getLineColor(leg.line);

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.08, duration: 0.3 }}
      className="flex gap-3 items-stretch"
    >
      {/* Timeline */}
      <div className="flex flex-col items-center w-6">
        <div
          className="w-3 h-3 rounded-full border-2 border-white shadow-sm flex-shrink-0"
          style={{ backgroundColor: color }}
        />
        <div
          className="flex-1 w-0.5 min-h-6"
          style={{ backgroundColor: color, opacity: 0.4 }}
        />
      </div>

      {/* Content */}
      <div className="flex-1 pb-3">
        <div className="flex items-center gap-2 mb-1">
          <span
            className="inline-block px-1.5 py-0.5 rounded text-[10px] font-semibold text-white"
            style={{ backgroundColor: color }}
          >
            {isTransfer ? "Walk" : leg.line}
          </span>
          <span className={`text-xs ${colors.textMuted}`}>
            {leg.depart} → {leg.arrive}
          </span>
        </div>
        <div className={`text-xs ${colors.textSecondary}`}>
          {leg.from} → {leg.to}
        </div>
      </div>
    </motion.div>
  );
}
