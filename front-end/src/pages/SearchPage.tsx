import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import SearchBar from "../components/SearchBar";
import { fetchStations } from "../api/client";
import type { StationInfo } from "../types";

export default function SearchPage() {
  const navigate = useNavigate();
  const [stations, setStations] = useState<StationInfo[]>([]);
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    fetchStations().then(setStations).catch(console.error);
  }, []);

  function swap() {
    setFrom(to);
    setTo(from);
  }

  function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!from || !to) {
      setError("Please select both stations.");
      return;
    }
    setError("");
    navigate(`/route?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`);
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4">
      {/* Hero */}
      <motion.div
        className="text-center mb-10"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Bangkok Transit
        </h1>
        <p className="text-gray-500 text-lg">
          Find the fastest route across BTS, MRT, ARL & more
        </p>
      </motion.div>

      {/* Search form */}
      <motion.form
        onSubmit={submit}
        className="w-full max-w-md bg-white/80 backdrop-blur rounded-2xl shadow-xl p-6 space-y-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <SearchBar stations={stations} label="From" value={from} onChange={setFrom} />

        <div className="flex justify-center">
          <button
            type="button"
            onClick={swap}
            className="w-10 h-10 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center
                       text-gray-500 transition-colors text-lg"
            title="Swap"
          >
            ⇅
          </button>
        </div>

        <SearchBar stations={stations} label="To" value={to} onChange={setTo} />

        {error && (
          <p className="text-red-500 text-sm text-center">{error}</p>
        )}

        <button
          type="submit"
          className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl
                     shadow-md transition-colors text-base"
        >
          Find Route
        </button>
      </motion.form>

      {/* Quick links */}
      <motion.div
        className="mt-8 flex gap-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <button
          onClick={() => navigate("/query")}
          className="text-sm text-gray-400 hover:text-gray-600 transition-colors bg-transparent border-none cursor-pointer"
        >
          Ask a question instead →
        </button>
        <button
          onClick={() => navigate("/explore")}
          className="text-sm text-gray-400 hover:text-gray-600 transition-colors bg-transparent border-none cursor-pointer"
        >
          Explore stations & attractions →
        </button>
      </motion.div>
    </div>
  );
}
