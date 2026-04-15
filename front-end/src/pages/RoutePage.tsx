import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import RouteSteps from "../components/RouteSteps";
import { fetchRoute } from "../api/client";
import { useTheme } from "../context/ThemeContext";
import type { ApiRouteResult, RouteData } from "../types";

export default function RoutePage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const { colors } = useTheme();
  const from = params.get("from") ?? "";
  const to = params.get("to") ?? "";

  const [route, setRoute] = useState<RouteData | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(Boolean(from && to));
  const [prevFrom, setPrevFrom] = useState(from);
  const [prevTo, setPrevTo] = useState(to);
  if (from !== prevFrom || to !== prevTo) {
    setPrevFrom(from);
    setPrevTo(to);
    if (from && to) setLoading(true);
  }

  useEffect(() => {
    if (!from || !to) return;
    let cancelled = false;
    fetchRoute(from, to)
      .then((res: ApiRouteResult) => {
        if (cancelled) return;
        if (res.type === "error") {
          setError(res.data.message);
        } else {
          setRoute(res.data);
        }
      })
      .catch(() => { if (!cancelled) setError("Failed to fetch route."); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [from, to]);

  if (!from || !to) {
    return (
      <div className={`h-screen flex flex-col items-center justify-center gap-4 px-4 ${colors.bg}`}>
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="text-center"
        >
          <p className="text-red-400 text-lg font-medium">Missing start or destination.</p>
          <button
            onClick={() => navigate("/")}
            className={`mt-4 px-6 py-2 ${colors.bgSecondary} ${colors.textSecondary} rounded-xl text-sm transition-colors border-none cursor-pointer`}
          >
            ← Back
          </button>
        </motion.div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className={`h-screen flex items-center justify-center ${colors.bg}`}>
        <motion.div
          className="w-10 h-10 border-4 border-gray-700 border-t-blue-500 rounded-full"
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 0.8, ease: "linear" }}
        />
      </div>
    );
  }

  if (error) {
    return (
      <div className={`h-screen flex flex-col items-center justify-center gap-4 px-4 ${colors.bg}`}>
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="text-center"
        >
          <p className="text-red-400 text-lg font-medium">{error}</p>
          <button
            onClick={() => navigate("/")}
            className={`mt-4 px-6 py-2 ${colors.bgSecondary} ${colors.textSecondary} rounded-xl text-sm transition-colors border-none cursor-pointer`}
          >
            ← Back
          </button>
        </motion.div>
      </div>
    );
  }

  if (!route) return null;

  return (
    <div className={`h-screen ${colors.bg} overflow-y-auto pb-16`}>
      {/* Header */}
      <div className={`${colors.headerBg} border-b ${colors.headerBorder} sticky top-0 z-40`}>
        <div className="max-w-lg mx-auto px-4 py-4 flex items-center gap-3">
          <button
            onClick={() => navigate("/")}
            className={`${colors.textMuted} hover:${colors.text.replace("text-", "")} transition-colors text-xl bg-transparent border-none cursor-pointer`}
          >
            ←
          </button>
          <div className="flex-1 min-w-0">
            <motion.h1
              className={`text-lg font-bold ${colors.text} truncate`}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              {route.origin} → {route.destination}
            </motion.h1>
            <motion.p
              className={`text-sm ${colors.textMuted}`}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              ~{route.total_time} min · {route.steps.filter((s) => s.type === "ride").length} line
              {route.steps.filter((s) => s.type === "ride").length > 1 ? "s" : ""}
            </motion.p>
          </div>
        </div>
      </div>

      {/* Route steps */}
      <div className="max-w-lg mx-auto px-4 pt-6">
        <RouteSteps steps={route.steps} />
      </div>
    </div>
  );
}
