"use client";

import { useState, useMemo } from "react";
import { GraphData } from "./types";

export default function SearchBar({
  data,
  onSelect,
}: {
  data: GraphData;
  onSelect: (id: string | null) => void;
}) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);

  const results = useMemo(() => {
    if (query.length < 2) return [];
    const q = query.toLowerCase();
    return data.nodes
      .filter((n) => n.type === "meal" && n.label.toLowerCase().includes(q))
      .slice(0, 8);
  }, [query, data]);

  const handleSelect = (id: string) => {
    onSelect(id);
    setQuery("");
    setOpen(false);
  };

  return (
    <div className="relative">
      <input
        type="text"
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setOpen(true);
          if (!e.target.value) onSelect(null);
        }}
        onFocus={() => setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 200)}
        placeholder="Search meals..."
        className="w-full px-3 py-2 text-sm rounded-lg bg-[var(--surface)] border border-[var(--border)] text-[var(--text)] placeholder:text-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)]"
      />
      {open && results.length > 0 && (
        <div className="absolute top-full mt-1 w-full bg-[var(--surface)] border border-[var(--border)] rounded-lg overflow-hidden shadow-xl">
          {results.map((n) => (
            <button
              key={n.id}
              onMouseDown={() => handleSelect(n.id)}
              className="w-full px-3 py-2 text-left text-sm hover:bg-[var(--border)] transition-colors flex justify-between items-center"
            >
              <span>{n.label}</span>
              {"cuisine" in n && (
                <span className="text-xs text-[var(--text-muted)]">{(n as any).cuisine}</span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
