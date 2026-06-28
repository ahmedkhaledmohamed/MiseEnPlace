import Graph from "graphology";
import { GraphData, MealNode, IngredientNode } from "./types";
import {
  ColorByMode,
  getNodeColor,
  getIngredientCategoryColor,
  getCuisineColor,
} from "./colors";

export function buildMealGraph(data: GraphData, colorBy: ColorByMode): Graph {
  const graph = new Graph();

  for (const node of data.nodes) {
    if (node.type !== "meal") continue;
    const m = node as MealNode;
    graph.addNode(m.id, {
      label: m.label,
      x: m.x ?? Math.random() * 100,
      y: m.y ?? Math.random() * 100,
      size: 4 + (m.ingredientCount / 14) * 16,
      color: getNodeColor(colorBy, {
        cuisine: m.cuisine,
        difficulty: m.difficulty,
        mealType: m.mealType,
        costPerServing: m.costPerServing,
        seasons: m.seasons,
      }),
      nodeType: "meal",
      cuisine: m.cuisine,
      mealType: m.mealType,
      difficulty: m.difficulty,
      costPerServing: m.costPerServing,
      totalTime: m.totalTime,
      dietaryTags: m.dietaryTags,
      seasons: m.seasons,
    });
  }

  for (const edge of data.edges) {
    if (edge.type !== "similarity") continue;
    if (!graph.hasNode(edge.source) || !graph.hasNode(edge.target)) continue;
    try {
      graph.addEdge(edge.source, edge.target, {
        size: 0.5 + edge.overlapRatio * 3,
        color: `rgba(255, 255, 255, ${0.02 + edge.overlapRatio * 0.12})`,
        edgeType: "similarity",
        overlapRatio: edge.overlapRatio,
        sharedCount: edge.sharedCount,
        sharedIngredients: edge.sharedIngredients,
      });
    } catch {}
  }

  return graph;
}

export function buildIngredientGraph(
  data: GraphData,
  hidePantryStaples: boolean,
): Graph {
  const graph = new Graph();
  const meals = data.nodes.filter((n) => n.type === "meal") as MealNode[];

  const ingMap = new Map<string, IngredientNode>();
  for (const n of data.nodes) {
    if (n.type === "ingredient") ingMap.set(n.id, n as IngredientNode);
  }

  const mealsByIngredient = new Map<string, string[]>();
  for (const edge of data.edges) {
    if (edge.type !== "ingredient") continue;
    const list = mealsByIngredient.get(edge.target) || [];
    list.push(edge.source);
    mealsByIngredient.set(edge.target, list);
  }

  for (const [ingId, ingNode] of ingMap) {
    if (hidePantryStaples && ingNode.isPantryStaple) continue;
    if (ingNode.usageCount < 1) continue;
    graph.addNode(ingId, {
      label: ingNode.label,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: 3 + Math.min(ingNode.usageCount, 30) * 0.6,
      color: getIngredientCategoryColor(ingNode.category),
      nodeType: "ingredient",
      category: ingNode.category,
      isPantryStaple: ingNode.isPantryStaple,
      usageCount: ingNode.usageCount,
    });
  }

  const coOccurrence = new Map<string, number>();
  for (const meal of meals) {
    const ingIds = data.edges
      .filter((e) => e.type === "ingredient" && e.source === meal.id)
      .map((e) => e.target)
      .filter((id) => graph.hasNode(id));

    for (let i = 0; i < ingIds.length; i++) {
      for (let j = i + 1; j < ingIds.length; j++) {
        const key =
          ingIds[i] < ingIds[j]
            ? `${ingIds[i]}|${ingIds[j]}`
            : `${ingIds[j]}|${ingIds[i]}`;
        coOccurrence.set(key, (coOccurrence.get(key) || 0) + 1);
      }
    }
  }

  for (const [key, count] of coOccurrence) {
    if (count < 2) continue;
    const [a, b] = key.split("|");
    if (!graph.hasNode(a) || !graph.hasNode(b)) continue;
    try {
      graph.addEdge(a, b, {
        size: 0.3 + count * 0.3,
        color: `rgba(255, 255, 255, ${0.03 + Math.min(count, 15) * 0.02})`,
        edgeType: "cooccurrence",
        count,
      });
    } catch {}
  }

  return graph;
}

export function buildCuisineGraph(data: GraphData): Graph {
  const graph = new Graph();
  const meals = data.nodes.filter((n) => n.type === "meal") as MealNode[];

  const cuisineMeals = new Map<string, MealNode[]>();
  for (const m of meals) {
    const list = cuisineMeals.get(m.cuisine) || [];
    list.push(m);
    cuisineMeals.set(m.cuisine, list);
  }

  const mealIngredients = new Map<string, Set<string>>();
  for (const edge of data.edges) {
    if (edge.type !== "ingredient") continue;
    const set = mealIngredients.get(edge.source) || new Set();
    const ingNode = data.nodes.find((n) => n.id === edge.target);
    if (ingNode) set.add(ingNode.label);
    mealIngredients.set(edge.source, set);
  }

  const cuisines = Array.from(cuisineMeals.keys()).sort();
  const angleStep = (2 * Math.PI) / cuisines.length;
  const radius = 50;

  cuisines.forEach((cuisine, i) => {
    const mealList = cuisineMeals.get(cuisine)!;
    const avgCost =
      mealList.reduce((s, m) => s + (m.costPerServing || 0), 0) /
      mealList.length;
    const angle = angleStep * i - Math.PI / 2;

    graph.addNode(`cuisine-${cuisine}`, {
      label: cuisine,
      x: Math.cos(angle) * radius,
      y: Math.sin(angle) * radius,
      size: 8 + mealList.length * 2,
      color: getCuisineColor(cuisine),
      nodeType: "cuisine",
      cuisine,
      mealCount: mealList.length,
      avgCost: Math.round(avgCost * 100) / 100,
      meals: mealList.map((m) => m.label),
    });
  });

  for (let i = 0; i < cuisines.length; i++) {
    for (let j = i + 1; j < cuisines.length; j++) {
      const c1 = cuisines[i];
      const c2 = cuisines[j];
      const meals1 = cuisineMeals.get(c1)!;
      const meals2 = cuisineMeals.get(c2)!;

      const ings1 = new Set<string>();
      meals1.forEach((m) => {
        const set = mealIngredients.get(m.id);
        if (set) set.forEach((ing) => ings1.add(ing));
      });
      const ings2 = new Set<string>();
      meals2.forEach((m) => {
        const set = mealIngredients.get(m.id);
        if (set) set.forEach((ing) => ings2.add(ing));
      });

      const shared = [...ings1].filter((ing) => ings2.has(ing));
      if (shared.length < 3) continue;

      try {
        graph.addEdge(`cuisine-${c1}`, `cuisine-${c2}`, {
          size: 0.5 + shared.length * 0.2,
          color: `rgba(255, 255, 255, ${0.05 + Math.min(shared.length, 20) * 0.02})`,
          edgeType: "cuisine-bridge",
          sharedCount: shared.length,
          sharedIngredients: shared.sort(),
        });
      } catch {}
    }
  }

  return graph;
}

export function buildEquipmentGraph(data: GraphData): Graph {
  const graph = new Graph();
  const meals = data.nodes.filter((n) => n.type === "meal") as MealNode[];

  const allEquipment = new Set<string>();
  meals.forEach((m) => m.equipment.forEach((e) => allEquipment.add(e)));

  for (const m of meals) {
    graph.addNode(m.id, {
      label: m.label,
      x: m.x ?? Math.random() * 100,
      y: m.y ?? Math.random() * 100,
      size: 4 + m.equipment.length * 2,
      color: getEquipmentCountColor(m.equipment.length),
      nodeType: "meal",
      cuisine: m.cuisine,
      mealType: m.mealType,
      difficulty: m.difficulty,
      costPerServing: m.costPerServing,
      totalTime: m.totalTime,
      dietaryTags: m.dietaryTags,
      equipment: m.equipment,
    });
  }

  for (let i = 0; i < meals.length; i++) {
    for (let j = i + 1; j < meals.length; j++) {
      const shared = meals[i].equipment.filter((e) =>
        meals[j].equipment.includes(e),
      );
      if (shared.length < 2) continue;
      try {
        graph.addEdge(meals[i].id, meals[j].id, {
          size: 0.3 + shared.length * 0.4,
          color: `rgba(255, 255, 255, ${0.02 + shared.length * 0.02})`,
          edgeType: "equipment",
          sharedCount: shared.length,
          sharedEquipment: shared,
        });
      } catch {}
    }
  }

  return graph;
}

function getEquipmentCountColor(count: number): string {
  const t = Math.min(1, count / 6);
  const r = Math.round(59 + t * (249 - 59));
  const g = Math.round(130 + t * (115 - 130));
  const b = Math.round(246 - t * (246 - 22));
  return `rgb(${r}, ${g}, ${b})`;
}

export function getMealsForIngredient(
  data: GraphData,
  ingredientId: string,
): MealNode[] {
  const mealIds = data.edges
    .filter((e) => e.type === "ingredient" && e.target === ingredientId)
    .map((e) => e.source);
  return data.nodes.filter(
    (n) => n.type === "meal" && mealIds.includes(n.id),
  ) as MealNode[];
}
