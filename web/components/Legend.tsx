"use client";

import { useState } from "react";
import { CUISINE_COLORS } from "./colors";

const REGIONS: Record<string, string[]> = {
  "East Asia": ["Chinese", "Japanese", "Korean", "East Asian"],
  "SE Asia": ["Thai", "Vietnamese", "Southeast Asian"],
  "South Asia": ["Indian", "South Asian"],
  "Middle East": ["Middle Eastern", "Turkish"],
  "Mediterranean": ["Greek", "Mediterranean"],
  "Europe": ["French", "Italian", "Spanish", "British", "Scandinavian", "Eastern European"],
  "Americas": ["American", "Mexican", "Latin American", "Caribbean"],
  "Other": ["African", "Fusion"],
};

export default function Legend() {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-[var(--surface)] border border-[var(--border)] rounded-lg overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-3 py-1.5 text-xs font-medium flex justify-between items-center hover:bg-[var(--border)] transition-colors"
      >
        <span>Legend</span>
        <span className="text-[var(--text-muted)]">{expanded ? "−" : "+"}</span>
      </button>

      {expanded && (
        <div className="px-3 pb-2 space-y-2">
          {Object.entries(REGIONS).map(([region, cuisines]) => (
            <div key={region}>
              <div className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider mb-0.5">
                {region}
              </div>
              <div className="flex flex-wrap gap-x-3 gap-y-0.5">
                {cuisines
                  .filter((c) => CUISINE_COLORS[c])
                  .map((cuisine) => (
                    <div key={cuisine} className="flex items-center gap-1">
                      <span
                        className="w-2.5 h-2.5 rounded-full inline-block"
                        style={{ backgroundColor: CUISINE_COLORS[cuisine] }}
                      />
                      <span className="text-[11px] text-[var(--text-muted)]">{cuisine}</span>
                    </div>
                  ))}
              </div>
            </div>
          ))}

          <div className="pt-1 border-t border-[var(--border)]">
            <div className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider mb-0.5">
              Node size
            </div>
            <div className="text-[11px] text-[var(--text-muted)]">
              Larger = more ingredients
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
