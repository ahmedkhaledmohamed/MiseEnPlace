"use client";

import { useState } from "react";
import { GraphMeta } from "./types";
import { ColorByMode, getCuisineColor } from "./colors";
import type { FilterState } from "./GraphExplorer";

const COLOR_BY_OPTIONS: { value: ColorByMode; label: string }[] = [
  { value: "cuisine", label: "Cuisine" },
  { value: "cost", label: "Cost" },
  { value: "difficulty", label: "Difficulty" },
  { value: "mealType", label: "Meal Type" },
  { value: "season", label: "Season" },
];

export default function FilterPanel({
  meta,
  filters,
  onFiltersChange,
  similarityThreshold,
  onSimilarityChange,
  colorBy,
  onColorByChange,
}: {
  meta: GraphMeta;
  filters: FilterState;
  onFiltersChange: (f: FilterState) => void;
  similarityThreshold: number;
  onSimilarityChange: (v: number) => void;
  colorBy: ColorByMode;
  onColorByChange: (mode: ColorByMode) => void;
}) {
  const [expanded, setExpanded] = useState(false);

  const toggle = (key: keyof FilterState, value: string) => {
    const current = filters[key];
    const next = current.includes(value)
      ? current.filter((v) => v !== value)
      : [...current, value];
    onFiltersChange({ ...filters, [key]: next });
  };

  const hasFilters =
    filters.cuisines.length > 0 ||
    filters.mealTypes.length > 0 ||
    filters.difficulties.length > 0 ||
    filters.dietaryTags.length > 0;

  return (
    <div className="bg-[var(--surface)] border border-[var(--border)] rounded-lg overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-3 py-2 text-sm font-medium flex justify-between items-center hover:bg-[var(--border)] transition-colors"
      >
        <span>Filters {hasFilters && `(active)`}</span>
        <span className="text-[var(--text-muted)]">{expanded ? "−" : "+"}</span>
      </button>

      {expanded && (
        <div className="px-3 pb-3 space-y-4 max-h-[60vh] overflow-y-auto">
          {hasFilters && (
            <button
              onClick={() =>
                onFiltersChange({
                  cuisines: [],
                  mealTypes: [],
                  difficulties: [],
                  dietaryTags: [],
                })
              }
              className="text-xs text-[var(--accent)] hover:underline"
            >
              Clear all
            </button>
          )}

          <div>
            <div className="text-xs font-medium text-[var(--text-muted)] mb-1.5 uppercase tracking-wide">
              Color by
            </div>
            <div className="flex flex-wrap gap-1">
              {COLOR_BY_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => onColorByChange(opt.value)}
                  className={`text-xs px-2 py-0.5 rounded-full border transition-colors ${
                    colorBy === opt.value
                      ? "border-[var(--accent)] bg-[var(--accent)]/20 text-[var(--accent)]"
                      : "border-[var(--border)] text-[var(--text-muted)] hover:border-[var(--text-muted)]"
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <div className="text-xs font-medium text-[var(--text-muted)] mb-1.5 uppercase tracking-wide">
              Similarity
            </div>
            <input
              type="range"
              min={0.05}
              max={0.75}
              step={0.05}
              value={similarityThreshold}
              onChange={(e) => onSimilarityChange(parseFloat(e.target.value))}
              className="w-full accent-[var(--accent)]"
            />
            <div className="text-xs text-[var(--text-muted)] mt-0.5">
              {Math.round(similarityThreshold * 100)}% min overlap
            </div>
          </div>

          <FilterGroup
            label="Cuisine"
            values={meta.cuisines}
            selected={filters.cuisines}
            onToggle={(v) => toggle("cuisines", v)}
            colorFn={getCuisineColor}
          />

          <FilterGroup
            label="Type"
            values={meta.mealTypes}
            selected={filters.mealTypes}
            onToggle={(v) => toggle("mealTypes", v)}
          />

          <FilterGroup
            label="Difficulty"
            values={meta.difficulties}
            selected={filters.difficulties}
            onToggle={(v) => toggle("difficulties", v)}
          />

          <FilterGroup
            label="Dietary"
            values={meta.dietaryTags}
            selected={filters.dietaryTags}
            onToggle={(v) => toggle("dietaryTags", v)}
          />
        </div>
      )}
    </div>
  );
}

function FilterGroup({
  label,
  values,
  selected,
  onToggle,
  colorFn,
}: {
  label: string;
  values: string[];
  selected: string[];
  onToggle: (v: string) => void;
  colorFn?: (v: string) => string;
}) {
  return (
    <div>
      <div className="text-xs font-medium text-[var(--text-muted)] mb-1.5 uppercase tracking-wide">
        {label}
      </div>
      <div className="flex flex-wrap gap-1">
        {values.map((v) => {
          const active = selected.includes(v);
          return (
            <button
              key={v}
              onClick={() => onToggle(v)}
              className={`text-xs px-2 py-0.5 rounded-full border transition-colors ${
                active
                  ? "border-[var(--accent)] bg-[var(--accent)]/20 text-[var(--accent)]"
                  : "border-[var(--border)] text-[var(--text-muted)] hover:border-[var(--text-muted)]"
              }`}
            >
              {colorFn && (
                <span
                  className="inline-block w-2 h-2 rounded-full mr-1"
                  style={{ backgroundColor: colorFn(v) }}
                />
              )}
              {v}
            </button>
          );
        })}
      </div>
    </div>
  );
}
