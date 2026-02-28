import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { fetchStations, fetchAttractions } from "../api/client";
import { useTheme } from "../context/ThemeContext";
import type { StationInfo, AttractionInfo } from "../types";
import LineBadge from "../components/LineBadge";
import { getLineColor, getLineDisplayName } from "../utils/lineColors";

type Tab = "stations" | "attractions";

export default function ExplorePage() {
  const navigate = useNavigate();
  const { theme, colors } = useTheme();
  const [tab, setTab] = useState<Tab>("stations");
  const [stations, setStations] = useState<StationInfo[]>([]);
  const [attractions, setAttractions] = useState<AttractionInfo[]>([]);
  const [lineFilter, setLineFilter] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetchStations().then(setStations).catch(console.error);
    fetchAttractions().then(setAttractions).catch(console.error);
  }, []);

  const allLines = [...new Set(stations.flatMap((s) => s.lines))].sort();

  const filteredStations = stations.filter((s) => {
    const matchesLine = !lineFilter || s.lines.includes(lineFilter);
    const matchesSearch = s.name.toLowerCase().includes(search.toLowerCase());
    return matchesLine && matchesSearch;
  });

  const filteredAttractions = attractions.filter((a) =>
    a.name.toLowerCase().includes(search.toLowerCase()) ||
    a.station.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className={`h-screen ${colors.bg} overflow-y-auto pb-16`}>
      {/* Header */}
      <div className={`${colors.headerBg} border-b ${colors.headerBorder} sticky top-0 z-40`}>
        <div className="max-w-2xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3 mb-4">
            <button
              onClick={() => navigate("/")}
              className={`${colors.textMuted} hover:${colors.text.replace("text-", "")} transition-colors text-xl bg-transparent border-none cursor-pointer`}
            >
              ←
            </button>
            <h1 className={`text-lg font-bold ${colors.text}`}>Explore</h1>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-3">
            {(["stations", "attractions"] as Tab[]).map((t) => (
              <button
                key={t}
                onClick={() => { setTab(t); setLineFilter(null); setSearch(""); }}
                className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors border-none cursor-pointer ${
                  tab === t
                    ? "bg-blue-600 text-white"
                    : `${colors.bgSecondary} ${colors.textMuted}`
                }`}
              >
                {t === "stations" ? "Stations" : "Attractions"}
              </button>
            ))}
          </div>

          {/* Search */}
          <input
            type="text"
            placeholder={tab === "stations" ? "Search stations..." : "Search attractions..."}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className={`w-full px-4 py-2 rounded-xl border ${colors.inputBorder} ${colors.inputBg} ${colors.text} text-sm
                       placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500`}
          />

          {/* Line filter chips */}
          {tab === "stations" && (
            <div className="flex gap-1.5 mt-3 overflow-x-auto pb-1">
              <button
                onClick={() => setLineFilter(null)}
                className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-colors border-none cursor-pointer ${
                  !lineFilter
                    ? theme === "dark" ? "bg-white text-gray-900" : "bg-gray-800 text-white"
                    : `${colors.bgSecondary} ${colors.textMuted}`
                }`}
              >
                All
              </button>
              {allLines.map((line) => (
                <button
                  key={line}
                  onClick={() => setLineFilter(lineFilter === line ? null : line)}
                  className="px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap text-white border-none cursor-pointer transition-opacity"
                  style={{
                    backgroundColor: getLineColor(line),
                    opacity: lineFilter === line ? 1 : 0.6,
                  }}
                >
                  {getLineDisplayName(line)}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="max-w-2xl mx-auto px-4 pt-4">
        <AnimatePresence mode="wait">
          {tab === "stations" ? (
            <motion.div
              key="stations"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="grid grid-cols-1 sm:grid-cols-2 gap-2"
            >
              {filteredStations.map((s, i) => (
                <motion.div
                  key={s.name}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: Math.min(i * 0.02, 0.5) }}
                  className={`${colors.cardBg} rounded-xl border ${colors.cardBorder} px-4 py-3
                             ${colors.cardHover} transition-colors cursor-default`}
                >
                  <p className={`font-medium text-sm ${colors.text}`}>{s.name}</p>
                  <div className="flex gap-1 mt-1.5 flex-wrap">
                    {s.lines.map((line) => (
                      <LineBadge key={line} line={line} />
                    ))}
                  </div>
                </motion.div>
              ))}
              {filteredStations.length === 0 && (
                <p className={`${colors.textMuted} text-sm col-span-2 text-center py-8`}>
                  No stations found.
                </p>
              )}
            </motion.div>
          ) : (
            <motion.div
              key="attractions"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="grid grid-cols-1 sm:grid-cols-2 gap-2"
            >
              {filteredAttractions.map((a, i) => (
                <motion.div
                  key={a.name}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: Math.min(i * 0.02, 0.5) }}
                  className={`${colors.cardBg} rounded-xl border ${colors.cardBorder} px-4 py-3
                             ${colors.cardHover} transition-colors cursor-default`}
                >
                  <p className={`font-medium text-sm ${colors.text}`}>{a.name}</p>
                  <p className={`text-xs ${colors.textMuted} mt-1`}>Near {a.station}</p>
                </motion.div>
              ))}
              {filteredAttractions.length === 0 && (
                <p className={`${colors.textMuted} text-sm col-span-2 text-center py-8`}>
                  No attractions found.
                </p>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
