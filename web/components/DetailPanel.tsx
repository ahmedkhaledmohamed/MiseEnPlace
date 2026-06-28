"use client";

import { GraphNode, GraphEdge, GraphData, MealNode, IngredientNode, SimilarityEdge, ViewMode } from "./types";
import { getCuisineColor, getIngredientCategoryColor } from "./colors";
import { getMealsForIngredient } from "./graphBuilders";

export default function DetailPanel({
  node, edges, allNodes, data, viewMode, onClose, onNavigate,
}: {
  node: GraphNode; edges: GraphEdge[]; allNodes: GraphNode[];
  data: GraphData; viewMode: ViewMode;
  onClose: () => void; onNavigate: (id: string) => void;
}) {
  if (viewMode === "ingredients" && node.type === "ingredient") {
    return <IngredientDetail ingredient={node as IngredientNode} data={data} onClose={onClose} onNavigate={onNavigate} />;
  }
  if (viewMode === "cuisines") {
    return <CuisineDetail nodeId={node.id} data={data} onClose={onClose} />;
  }
  if (node.type === "meal") {
    return <MealDetail meal={node as MealNode} edges={edges as SimilarityEdge[]} allNodes={allNodes} onClose={onClose} onNavigate={onNavigate} />;
  }
  return null;
}

function MealDetail({ meal, edges, allNodes, onClose, onNavigate }: {
  meal: MealNode; edges: SimilarityEdge[]; allNodes: GraphNode[]; onClose: () => void; onNavigate: (id: string) => void;
}) {
  const similarMeals = edges
    .map((e) => {
      const otherId = e.source === meal.id ? e.target : e.source;
      const otherNode = allNodes.find((n) => n.id === otherId);
      return otherNode ? { node: otherNode as MealNode, edge: e } : null;
    })
    .filter(Boolean)
    .sort((a, b) => b!.edge.overlapRatio - a!.edge.overlapRatio)
    .slice(0, 10) as { node: MealNode; edge: SimilarityEdge }[];

  return (
    <div className="absolute top-0 right-0 h-full w-[360px] bg-[var(--surface)] border-l border-[var(--border)] z-20 overflow-y-auto">
      <div className="p-4">
        <div className="flex justify-between items-start mb-3">
          <div>
            <h2 className="text-lg font-semibold leading-tight">{meal.label}</h2>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xs px-2 py-0.5 rounded-full" style={{ backgroundColor: getCuisineColor(meal.cuisine) + "33", color: getCuisineColor(meal.cuisine) }}>{meal.cuisine}</span>
              <span className="text-xs text-[var(--text-muted)]">{meal.mealType}</span>
              <span className="text-xs text-[var(--text-muted)]">{meal.difficulty}</span>
            </div>
          </div>
          <button onClick={onClose} className="text-[var(--text-muted)] hover:text-[var(--text)] text-lg leading-none">&times;</button>
        </div>

        <p className="text-sm text-[var(--text-muted)] mb-4">{meal.description}</p>

        <div className="grid grid-cols-3 gap-2 mb-4">
          <Stat label="Time" value={`${meal.totalTime} min`} />
          <Stat label="Cost" value={`$${meal.costPerServing?.toFixed(2)}`} />
          <Stat label="Servings" value={`${meal.servings}`} />
        </div>

        {meal.dietaryTags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-4">
            {meal.dietaryTags.map((tag) => (
              <span key={tag} className="text-xs px-2 py-0.5 rounded-full bg-green-900/30 text-green-400">{tag}</span>
            ))}
          </div>
        )}

        <Section title="Ingredients">
          <ul className="space-y-1">
            {meal.ingredients.map((ing, i) => (
              <li key={i} className="text-sm flex justify-between items-center">
                <span className={ing.isOptional ? "text-[var(--text-muted)] italic" : ""}>
                  <span className="inline-block w-2 h-2 rounded-full mr-1.5" style={{ backgroundColor: getIngredientCategoryColor(ing.category) }} />
                  {ing.name}
                  {ing.prepNote && <span className="text-[var(--text-muted)]"> ({ing.prepNote})</span>}
                </span>
                <span className="text-[var(--text-muted)] tabular-nums text-xs">{ing.quantity} {ing.unit}</span>
              </li>
            ))}
          </ul>
        </Section>

        <Section title="Steps">
          <ol className="space-y-2">
            {meal.steps.map((step) => (
              <li key={step.order} className="text-sm flex gap-2">
                <span className="text-[var(--accent)] font-medium shrink-0">{step.order}.</span>
                <span>{step.instruction}</span>
              </li>
            ))}
          </ol>
        </Section>

        {meal.tips.length > 0 && (
          <Section title="Tips">
            <ul className="space-y-1">{meal.tips.map((tip, i) => <li key={i} className="text-sm text-[var(--text-muted)]">&bull; {tip}</li>)}</ul>
          </Section>
        )}

        {meal.equipment.length > 0 && (
          <Section title="Equipment">
            <div className="flex flex-wrap gap-1">{meal.equipment.map((eq) => <span key={eq} className="text-xs px-2 py-0.5 rounded bg-[var(--border)]">{eq}</span>)}</div>
          </Section>
        )}

        {similarMeals.length > 0 && (
          <Section title="Similar Meals">
            <div className="space-y-1.5">
              {similarMeals.map(({ node: other, edge }) => (
                <button key={other.id} onClick={() => onNavigate(other.id)}
                  className="w-full text-left text-sm px-2 py-1.5 rounded hover:bg-[var(--border)] transition-colors flex justify-between items-center">
                  <div><span className="font-medium">{other.label}</span><span className="text-[var(--text-muted)] ml-2 text-xs">{other.cuisine}</span></div>
                  <span className="text-xs text-[var(--text-muted)] tabular-nums">{edge.sharedCount} shared ({Math.round(edge.overlapRatio * 100)}%)</span>
                </button>
              ))}
            </div>
          </Section>
        )}
      </div>
    </div>
  );
}

function IngredientDetail({ ingredient, data, onClose, onNavigate }: {
  ingredient: IngredientNode; data: GraphData; onClose: () => void; onNavigate: (id: string) => void;
}) {
  const meals = getMealsForIngredient(data, ingredient.id);
  const byCuisine = new Map<string, MealNode[]>();
  meals.forEach((m) => {
    const list = byCuisine.get(m.cuisine) || [];
    list.push(m);
    byCuisine.set(m.cuisine, list);
  });

  return (
    <div className="absolute top-0 right-0 h-full w-[360px] bg-[var(--surface)] border-l border-[var(--border)] z-20 overflow-y-auto">
      <div className="p-4">
        <div className="flex justify-between items-start mb-3">
          <div>
            <h2 className="text-lg font-semibold leading-tight">{ingredient.label}</h2>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xs px-2 py-0.5 rounded-full" style={{ backgroundColor: getIngredientCategoryColor(ingredient.category) + "33", color: getIngredientCategoryColor(ingredient.category) }}>
                {ingredient.category}
              </span>
              {ingredient.isPantryStaple && <span className="text-xs text-[var(--text-muted)]">pantry staple</span>}
            </div>
          </div>
          <button onClick={onClose} className="text-[var(--text-muted)] hover:text-[var(--text)] text-lg leading-none">&times;</button>
        </div>

        <div className="grid grid-cols-2 gap-2 mb-4">
          <Stat label="Used in" value={`${ingredient.usageCount} meals`} />
          <Stat label="Cuisines" value={`${byCuisine.size}`} />
        </div>

        <Section title={`Meals using ${ingredient.label}`}>
          <div className="space-y-3">
            {Array.from(byCuisine.entries()).map(([cuisine, cuisineMeals]) => (
              <div key={cuisine}>
                <div className="text-xs font-medium mb-1" style={{ color: getCuisineColor(cuisine) }}>{cuisine}</div>
                <div className="space-y-1">
                  {cuisineMeals.map((m) => (
                    <button key={m.id} onClick={() => onNavigate(m.id)}
                      className="w-full text-left text-sm px-2 py-1 rounded hover:bg-[var(--border)] transition-colors flex justify-between">
                      <span>{m.label}</span>
                      <span className="text-xs text-[var(--text-muted)]">${m.costPerServing?.toFixed(2)}</span>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Section>
      </div>
    </div>
  );
}

function CuisineDetail({ nodeId, data, onClose }: {
  nodeId: string; data: GraphData; onClose: () => void;
}) {
  const cuisineName = nodeId.replace("cuisine-", "");
  const meals = (data.nodes.filter((n) => n.type === "meal" && (n as MealNode).cuisine === cuisineName) as MealNode[]);
  const avgCost = meals.length > 0 ? meals.reduce((s, m) => s + (m.costPerServing || 0), 0) / meals.length : 0;
  const avgTime = meals.length > 0 ? meals.reduce((s, m) => s + (m.totalTime || 0), 0) / meals.length : 0;

  const ingCounts = new Map<string, number>();
  meals.forEach((m) => m.ingredients.forEach((ing) => {
    ingCounts.set(ing.name, (ingCounts.get(ing.name) || 0) + 1);
  }));
  const topIngs = Array.from(ingCounts.entries()).sort((a, b) => b[1] - a[1]).slice(0, 10);

  return (
    <div className="absolute top-0 right-0 h-full w-[360px] bg-[var(--surface)] border-l border-[var(--border)] z-20 overflow-y-auto">
      <div className="p-4">
        <div className="flex justify-between items-start mb-3">
          <h2 className="text-lg font-semibold leading-tight" style={{ color: getCuisineColor(cuisineName) }}>{cuisineName}</h2>
          <button onClick={onClose} className="text-[var(--text-muted)] hover:text-[var(--text)] text-lg leading-none">&times;</button>
        </div>

        <div className="grid grid-cols-3 gap-2 mb-4">
          <Stat label="Meals" value={`${meals.length}`} />
          <Stat label="Avg cost" value={`$${avgCost.toFixed(2)}`} />
          <Stat label="Avg time" value={`${Math.round(avgTime)} min`} />
        </div>

        <Section title="Top Ingredients">
          <ul className="space-y-1">
            {topIngs.map(([name, count]) => (
              <li key={name} className="text-sm flex justify-between">
                <span>{name}</span>
                <span className="text-xs text-[var(--text-muted)]">{count} meals</span>
              </li>
            ))}
          </ul>
        </Section>

        <Section title="Meals">
          <div className="space-y-1">
            {meals.map((m) => (
              <div key={m.id} className="text-sm px-2 py-1 rounded flex justify-between">
                <span>{m.label}</span>
                <span className="text-xs text-[var(--text-muted)]">{m.difficulty} &middot; ${m.costPerServing?.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </Section>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return <div className="bg-[var(--bg)] rounded-lg px-2 py-1.5 text-center">
    <div className="text-xs text-[var(--text-muted)]">{label}</div>
    <div className="text-sm font-medium">{value}</div>
  </div>;
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return <div className="mb-4">
    <h3 className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wide mb-2">{title}</h3>
    {children}
  </div>;
}
