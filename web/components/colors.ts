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

export function getCuisineColor(cuisine: string): string {
  return CUISINE_COLORS[cuisine] || "#94a3b8";
}
