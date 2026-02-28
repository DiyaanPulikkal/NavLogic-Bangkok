import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import RouteSteps from "../components/RouteSteps";
import { fetchRoute } from "../api/client";
import type { ApiRouteResult, RouteData } from "../types";

export default function RoutePage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const from = params.get("from") ?? "";
  const to = params.get("to") ?? "";

  const [route, setRoute] = useState<RouteData | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!from || !to) {
      setError("Missing start or destination.");
      setLoading(false);
      return;
    }
    setLoading(true);
    fetchRoute(from, to)
      .then((res: ApiRouteResult) => {
        if (res.type === "error") {
          setError(res.data.message);
        } else {
          setRoute(res.data);
        }
      })
      .catch(() => setError("Failed to fetch route."))
      .finally(() => setLoading(false));
  }, [from, to]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <motion.div
          className="w-10 h-10 border-4 border-blue-200 border-t-blue-600 rounded-full"
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 0.8, ease: "linear" }}
        />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 px-4">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="text-center"
        >
          <p className="text-red-500 text-lg font-medium">{error}</p>
          <button
            onClick={() => navigate("/")}
            className="mt-4 px-6 py-2 bg-gray-100 hover:bg-gray-200 rounded-xl text-sm transition-colors"
          >
            ← Back to search
          </button>
        </motion.div>
      </div>
    );
  }

  if (!route) return null;

  return (
    <div className="min-h-screen bg-gray-50 pb-16">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 sticky top-0 z-40">
        <div className="max-w-lg mx-auto px-4 py-4 flex items-center gap-3">
          <button
            onClick={() => navigate("/")}
            className="text-gray-400 hover:text-gray-700 transition-colors text-xl bg-transparent border-none cursor-pointer"
          >
            ←
          </button>
          <div className="flex-1 min-w-0">
            <motion.h1
              className="text-lg font-bold text-gray-900 truncate"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              {route.from} → {route.to}
            </motion.h1>
            <motion.p
              className="text-sm text-gray-400"
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
