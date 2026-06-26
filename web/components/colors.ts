export type ColorByMode = "cuisine" | "cost" | "difficulty" | "mealType" | "season";

export const CUISINE_COLORS: Record<string, string> = {
  "Chinese": "#ef4444",
  "Japanese": "#f87171",
  "Korean": "#dc2626",
  "East Asian": "#fb923c",
  "Thai": "#f97316",
  "Vietnamese": "#ea580c",
  "Southeast Asian": "#fb923c",
  "Indian": "#eab308",
  "South Asian": "#facc15",
  "Middle Eastern": "#22c55e",
  "Turkish": "#16a34a",
  "Greek": "#4ade80",
  "Mediterranean": "#34d399",
  "French": "#3b82f6",
  "Italian": "#60a5fa",
  "Spanish": "#2563eb",
  "British": "#93c5fd",
  "Scandinavian": "#7dd3fc",
  "Eastern European": "#818cf8",
  "American": "#a78bfa",
  "Mexican": "#c084fc",
  "Latin American": "#d946ef",
  "Caribbean": "#e879f9",
  "African": "#f472b6",
  "Fusion": "#94a3b8",
};

export const DIFFICULTY_COLORS: Record<string, string> = {
  easy: "#4ade80",
  medium: "#facc15",
  advanced: "#f97316",
  project: "#ef4444",
};

export const MEAL_TYPE_COLORS: Record<string, string> = {
  breakfast: "#fb923c",
  lunch: "#22c55e",
  dinner: "#3b82f6",
  snack: "#a78bfa",
  dessert: "#f472b6",
  side: "#94a3b8",
};

export const SEASON_COLORS: Record<string, string> = {
  spring: "#4ade80",
  summer: "#facc15",
  fall: "#f97316",
  winter: "#60a5fa",
  all: "#94a3b8",
};

export const INGREDIENT_CATEGORY_COLORS: Record<string, string> = {
  protein: "#ef4444",
  vegetable: "#22c55e",
  fruit: "#f97316",
  grain: "#eab308",
  dairy: "#93c5fd",
  spice: "#f59e0b",
  "oil-fat": "#a3a3a3",
  "sauce-condiment": "#c084fc",
  herb: "#34d399",
  legume: "#a78bfa",
  "nut-seed": "#d97706",
  sweetener: "#f472b6",
  liquid: "#7dd3fc",
  other: "#64748b",
};

export function getCuisineColor(cuisine: string): string {
  return CUISINE_COLORS[cuisine] || "#94a3b8";
}

export function getCostColor(costPerServing: number): string {
  const min = 0, max = 8;
  const t = Math.min(1, Math.max(0, (costPerServing - min) / (max - min)));
  const r = Math.round(34 + t * (239 - 34));
  const g = Math.round(197 - t * (197 - 68));
  const b = Math.round(94 - t * (94 - 68));
  return `rgb(${r}, ${g}, ${b})`;
}

export function getNodeColor(
  mode: ColorByMode,
  attrs: { cuisine: string; difficulty: string; mealType: string; costPerServing: number; seasons?: string[] },
): string {
  switch (mode) {
    case "cuisine":
      return CUISINE_COLORS[attrs.cuisine] || "#94a3b8";
    case "cost":
      return getCostColor(attrs.costPerServing);
    case "difficulty":
      return DIFFICULTY_COLORS[attrs.difficulty] || "#94a3b8";
    case "mealType":
      return MEAL_TYPE_COLORS[attrs.mealType] || "#94a3b8";
    case "season": {
      const seasons: string[] = attrs.seasons || ["all"];
      const primary = seasons.find((s) => s !== "all") || "all";
      return SEASON_COLORS[primary] || "#94a3b8";
    }
    default:
      return "#94a3b8";
  }
}

export function getIngredientCategoryColor(category: string): string {
  return INGREDIENT_CATEGORY_COLORS[category] || "#64748b";
}
