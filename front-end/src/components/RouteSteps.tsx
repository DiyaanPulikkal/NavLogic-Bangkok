import { motion } from "framer-motion";
import { Footprints } from "lucide-react";
import type { RouteStep } from "../types";
import { getLineColor, getLineDisplayName } from "../utils/lineColors";
import { useTheme } from "../context/ThemeContext";

interface Props {
  steps: RouteStep[];
}

export default function RouteSteps({ steps }: Props) {
  return (
    <div className="flex flex-col gap-0">
      {steps.map((step, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.15, duration: 0.4 }}
        >
          {step.type === "ride" ? (
            <RideStep step={step} />
          ) : (
            <TransferStep step={step} />
          )}
        </motion.div>
      ))}
    </div>
  );
}

function RideStep({ step }: { step: RouteStep }) {
  const { colors } = useTheme();
  const color = getLineColor(step.line ?? "");
  const stationCount = step.stations?.length ?? 0;

  return (
    <div className="flex gap-4 items-stretch">
      {/* Line indicator */}
      <div className="flex flex-col items-center w-8">
        <div
          className="w-4 h-4 rounded-full border-2 border-white shadow-md flex-shrink-0"
          style={{ backgroundColor: color }}
        />
        <div
          className="flex-1 w-1 min-h-8"
          style={{ backgroundColor: color }}
        />
        <div
          className="w-4 h-4 rounded-full border-2 border-white shadow-md flex-shrink-0"
          style={{ backgroundColor: color }}
        />
      </div>

      {/* Content */}
      <div className={`flex-1 ${colors.cardBg} rounded-xl border ${colors.cardBorder} p-4 my-1 transition-colors ${colors.cardHover}`}>
        <div className="flex items-center gap-2 mb-2">
          <span
            className="inline-block px-2.5 py-0.5 rounded-md text-[11px] font-semibold text-white tracking-wide"
            style={{ backgroundColor: color }}
          >
            {getLineDisplayName(step.line ?? "")}
          </span>
          {stationCount > 0 && (
            <span className={`text-[11px] ${colors.textMuted}`}>
              {stationCount - 1} stops
            </span>
          )}
        </div>
        <div className={`text-sm ${colors.textSecondary} space-y-0.5`}>
          <p>
            Board at <span className={`font-medium ${colors.text}`}>{step.board}</span>
          </p>
          <p>
            Alight at <span className={`font-medium ${colors.text}`}>{step.alight}</span>
          </p>
        </div>

        {step.stations && step.stations.length > 2 && (
          <details className="mt-2">
            <summary className={`text-xs ${colors.textMuted} cursor-pointer hover:${colors.textSecondary.replace("text-", "")} transition-colors`}>
              Show all stops
            </summary>
            <ul className="mt-1 space-y-0.5">
              {step.stations.map((s, j) => (
                <li key={j} className={`text-xs ${colors.textSecondary} flex items-center gap-1.5`}>
                  <span
                    className="w-1.5 h-1.5 rounded-full flex-shrink-0"
                    style={{ backgroundColor: color }}
                  />
                  {s}
                </li>
              ))}
            </ul>
          </details>
        )}
      </div>
    </div>
  );
}

function TransferStep({ step }: { step: RouteStep }) {
  const { colors } = useTheme();
  return (
    <div className="flex gap-4 items-center">
      <div className="flex flex-col items-center w-8">
        <motion.div
          className="w-5 h-5 rounded-full bg-amber-400 border-2 border-white shadow-md flex items-center justify-center"
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ repeat: Infinity, duration: 2 }}
        >
          <Footprints size={12} className="text-amber-900" />
        </motion.div>
      </div>
      <div className={`flex-1 ${colors.transferBg} rounded-xl border ${colors.transferBorder} px-4 py-3 my-1`}>
        <p className={`text-sm ${colors.transferText}`}>
          Walk from <span className="font-medium">{step.from}</span> to{" "}
          <span className="font-medium">{step.to}</span>
        </p>
      </div>
    </div>
  );
}
