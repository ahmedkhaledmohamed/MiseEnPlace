"use client";

import { useState, useMemo } from "react";
import { GraphData, ViewMode } from "./types";

const PLACEHOLDERS: Record<ViewMode, string> = {
  meals: "Search meals...",
  ingredients: "Search ingredients...",
  cuisines: "Search cuisines...",
  equipment: "Search meals...",
};

export default function SearchBar({
  data,
  onSelect,
  viewMode,
}: {
  data: GraphData;
  onSelect: (id: string | null) => void;
  viewMode: ViewMode;
}) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);

  const results = useMemo(() => {
    if (query.length < 2) return [];
    const q = query.toLowerCase();

    if (viewMode === "ingredients") {
      return data.nodes
        .filter((n) => n.type === "ingredient" && n.label.toLowerCase().includes(q))
        .slice(0, 8);
    }
    if (viewMode === "cuisines") {
      return data.nodes
        .filter((n) => n.type === "meal")
        .reduce((acc, n) => {
          const cuisine = (n as any).cuisine;
          if (cuisine.toLowerCase().includes(q) && !acc.find((a: any) => a.id === `cuisine-${cuisine}`)) {
            acc.push({ id: `cuisine-${cuisine}`, type: "cuisine" as const, label: cuisine });
          }
          return acc;
        }, [] as { id: string; type: "cuisine"; label: string }[])
        .slice(0, 8);
    }
    return data.nodes
      .filter((n) => n.type === "meal" && n.label.toLowerCase().includes(q))
      .slice(0, 8);
  }, [query, data, viewMode]);

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
        placeholder={PLACEHOLDERS[viewMode]}
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
              {"category" in n && (
                <span className="text-xs text-[var(--text-muted)]">{(n as any).category}</span>
              )}
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
