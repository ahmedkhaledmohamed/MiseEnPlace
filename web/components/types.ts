export interface MealNode {
  id: string;
  type: "meal";
  label: string;
  cuisine: string;
  mealType: string;
  difficulty: string;
  prepTime: number;
  cookTime: number;
  totalTime: number;
  servings: number;
  costPerServing: number;
  totalCost: number;
  description: string;
  sourceInspiration: string;
  groundingConfidence: number;
  dietaryTags: string[];
  seasons: string[];
  ingredients: {
    name: string;
    category: string;
    quantity: number;
    unit: string;
    isOptional: boolean;
    prepNote: string | null;
    cost: number | null;
  }[];
  ingredientCount: number;
  steps: { order: number; instruction: string; duration: number | null }[];
  equipment: string[];
  tips: string[];
  variations: string[];
  x?: number;
  y?: number;
}

export interface IngredientNode {
  id: string;
  type: "ingredient";
  label: string;
  category: string;
  isPantryStaple: boolean;
  usageCount: number;
}

export type GraphNode = MealNode | IngredientNode;

export interface SimilarityEdge {
  source: string;
  target: string;
  type: "similarity";
  sharedCount: number;
  overlapRatio: number;
  sharedIngredients: string[];
}

export interface IngredientEdge {
  source: string;
  target: string;
  type: "ingredient";
  quantity: number;
  unit: string;
  cost: number | null;
}

export type GraphEdge = SimilarityEdge | IngredientEdge;

export interface GraphMeta {
  cuisines: string[];
  mealTypes: string[];
  difficulties: string[];
  dietaryTags: string[];
  ingredientCategories: string[];
  mealCount: number;
  ingredientCount: number;
  similarityPairCount: number;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  meta: GraphMeta;
}
