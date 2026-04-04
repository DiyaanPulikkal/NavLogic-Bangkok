import { useState, useRef, useEffect } from "react";
import type { StationInfo } from "../types";
import { getLineColor } from "../utils/lineColors";

interface Props {
  stations: StationInfo[];
  label: string;
  value: string;
  onChange: (value: string) => void;
}

export default function SearchBar({ stations, label, value, onChange }: Props) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState(value);
  const [prevValue, setPrevValue] = useState(value);
  if (value !== prevValue) {
    setPrevValue(value);
    setQuery(value);
  }
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const filtered = stations.filter((s) =>
    s.name.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div ref={ref} className="relative w-full">
      <label className="block text-sm font-medium text-gray-600 mb-1">
        {label}
      </label>
      <input
        type="text"
        className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white shadow-sm
                   focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent
                   text-base transition-shadow"
        placeholder="Station or attraction..."
        value={query}
        onFocus={() => setOpen(true)}
        onChange={(e) => {
          setQuery(e.target.value);
          setOpen(true);
        }}
      />
      {open && filtered.length > 0 && (
        <ul className="absolute z-50 mt-1 w-full max-h-60 overflow-y-auto rounded-xl bg-white border border-gray-200 shadow-lg">
          {filtered.slice(0, 30).map((s) => (
            <li
              key={s.name}
              className="px-4 py-2 cursor-pointer hover:bg-blue-50 flex items-center gap-2 transition-colors"
              onMouseDown={() => {
                onChange(s.name);
                setQuery(s.name);
                setOpen(false);
              }}
            >
              <span className="flex-1 text-sm">{s.name}</span>
              <span className="flex gap-1">
                {s.lines.map((line) => (
                  <span
                    key={line}
                    className="w-2.5 h-2.5 rounded-full inline-block"
                    style={{ backgroundColor: getLineColor(line) }}
                  />
                ))}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
