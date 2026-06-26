"use client";

import { useState } from "react";
import {
  ColorByMode,
  CUISINE_COLORS,
  DIFFICULTY_COLORS,
  MEAL_TYPE_COLORS,
  SEASON_COLORS,
  INGREDIENT_CATEGORY_COLORS,
} from "./colors";

const REGIONS: Record<string, string[]> = {
  "East Asia": ["Chinese", "Japanese", "Korean", "East Asian"],
  "SE Asia": ["Thai", "Vietnamese", "Southeast Asian"],
  "South Asia": ["Indian", "South Asian"],
  "Middle East": ["Middle Eastern", "Turkish"],
  "Mediterranean": ["Greek", "Mediterranean"],
  Europe: [
    "French",
    "Italian",
    "Spanish",
    "British",
    "Scandinavian",
    "Eastern European",
  ],
  Americas: ["American", "Mexican", "Latin American", "Caribbean"],
  Other: ["African", "Fusion"],
};

export default function Legend({
  colorBy,
  showIngredients,
}: {
  colorBy: ColorByMode;
  showIngredients: boolean;
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-[var(--surface)] border border-[var(--border)] rounded-lg overflow-hidden max-w-[280px]">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-3 py-1.5 text-xs font-medium flex justify-between items-center hover:bg-[var(--border)] transition-colors"
      >
        <span>Legend</span>
        <span className="text-[var(--text-muted)]">
          {expanded ? "−" : "+"}
        </span>
      </button>

      {expanded && (
        <div className="px-3 pb-2 space-y-2">
          {colorBy === "cuisine" && <CuisineLegend />}
          {colorBy === "cost" && <CostLegend />}
          {colorBy === "difficulty" && (
            <ColorMapLegend title="Difficulty" map={DIFFICULTY_COLORS} />
          )}
          {colorBy === "mealType" && (
            <ColorMapLegend title="Meal Type" map={MEAL_TYPE_COLORS} />
          )}
          {colorBy === "season" && (
            <ColorMapLegend title="Season" map={SEASON_COLORS} />
          )}

          {showIngredients && (
            <>
              <div className="pt-1 border-t border-[var(--border)]">
                <div className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider mb-1">
                  Ingredient Categories
                </div>
                <div className="flex flex-wrap gap-x-3 gap-y-0.5">
                  {Object.entries(INGREDIENT_CATEGORY_COLORS).map(
                    ([cat, color]) => (
                      <div key={cat} className="flex items-center gap-1">
                        <span
                          className="w-2 h-2 rounded-full inline-block"
                          style={{ backgroundColor: color }}
                        />
                        <span className="text-[11px] text-[var(--text-muted)]">
                          {cat}
                        </span>
                      </div>
                    ),
                  )}
                </div>
              </div>
            </>
          )}

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

function CuisineLegend() {
  return (
    <>
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
                  <span className="text-[11px] text-[var(--text-muted)]">
                    {cuisine}
                  </span>
                </div>
              ))}
          </div>
        </div>
      ))}
    </>
  );
}

function CostLegend() {
  return (
    <div>
      <div className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider mb-1">
        Cost per serving
      </div>
      <div className="flex items-center gap-1">
        <span className="text-[11px] text-[var(--text-muted)]">$0</span>
        <div
          className="flex-1 h-3 rounded"
          style={{
            background:
              "linear-gradient(to right, #22c55e, #eab308, #f97316, #ef4444)",
          }}
        />
        <span className="text-[11px] text-[var(--text-muted)]">$8+</span>
      </div>
    </div>
  );
}

function ColorMapLegend({
  title,
  map,
}: {
  title: string;
  map: Record<string, string>;
}) {
  return (
    <div>
      <div className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider mb-1">
        {title}
      </div>
      <div className="flex flex-wrap gap-x-3 gap-y-0.5">
        {Object.entries(map).map(([key, color]) => (
          <div key={key} className="flex items-center gap-1">
            <span
              className="w-2.5 h-2.5 rounded-full inline-block"
              style={{ backgroundColor: color }}
            />
            <span className="text-[11px] text-[var(--text-muted)]">{key}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
