import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { fetchStations, fetchAttractions } from "../api/client";
import type { StationInfo, AttractionInfo } from "../types";
import LineBadge from "../components/LineBadge";
import { getLineColor, getLineDisplayName } from "../utils/lineColors";

type Tab = "stations" | "attractions";

export default function ExplorePage() {
  const navigate = useNavigate();
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
    <div className="min-h-screen bg-gray-50 pb-16">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 sticky top-0 z-40">
        <div className="max-w-2xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3 mb-4">
            <button
              onClick={() => navigate("/")}
              className="text-gray-400 hover:text-gray-700 transition-colors text-xl bg-transparent border-none cursor-pointer"
            >
              ←
            </button>
            <h1 className="text-lg font-bold text-gray-900">Explore</h1>
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
                    : "bg-gray-100 text-gray-500 hover:bg-gray-200"
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
            className="w-full px-4 py-2 rounded-xl border border-gray-200 bg-gray-50 text-sm
                       focus:outline-none focus:ring-2 focus:ring-blue-400"
          />

          {/* Line filter chips (stations tab only) */}
          {tab === "stations" && (
            <div className="flex gap-1.5 mt-3 overflow-x-auto pb-1">
              <button
                onClick={() => setLineFilter(null)}
                className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-colors border-none cursor-pointer ${
                  !lineFilter ? "bg-gray-800 text-white" : "bg-gray-100 text-gray-500"
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
                  className="bg-white rounded-xl border border-gray-100 px-4 py-3 shadow-sm
                             hover:shadow-md transition-shadow cursor-default"
                >
                  <p className="font-medium text-sm text-gray-900">{s.name}</p>
                  <div className="flex gap-1 mt-1.5 flex-wrap">
                    {s.lines.map((line) => (
                      <LineBadge key={line} line={line} />
                    ))}
                  </div>
                </motion.div>
              ))}
              {filteredStations.length === 0 && (
                <p className="text-gray-400 text-sm col-span-2 text-center py-8">
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
                  className="bg-white rounded-xl border border-gray-100 px-4 py-3 shadow-sm
                             hover:shadow-md transition-shadow cursor-default"
                >
                  <p className="font-medium text-sm text-gray-900">{a.name}</p>
                  <p className="text-xs text-gray-400 mt-1">Near {a.station}</p>
                </motion.div>
              ))}
              {filteredAttractions.length === 0 && (
                <p className="text-gray-400 text-sm col-span-2 text-center py-8">
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
