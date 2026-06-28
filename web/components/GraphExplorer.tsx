"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Graph from "graphology";
import forceAtlas2 from "graphology-layout-forceatlas2";
import {
  SigmaContainer,
  useRegisterEvents,
  useSigma,
  useLoadGraph,
  useSetSettings,
} from "@react-sigma/core";
import "@react-sigma/core/lib/style.css";
import { GraphData, MealNode, ViewMode } from "./types";
import { ColorByMode, getNodeColor, getIngredientCategoryColor } from "./colors";
import {
  buildMealGraph,
  buildIngredientGraph,
  buildCuisineGraph,
  buildEquipmentGraph,
} from "./graphBuilders";
import SearchBar from "./SearchBar";
import FilterPanel from "./FilterPanel";
import DetailPanel from "./DetailPanel";
import Legend from "./Legend";

const VIEW_TABS: { mode: ViewMode; label: string; desc: string }[] = [
  { mode: "meals", label: "Meals", desc: "Meal similarity by shared ingredients" },
  { mode: "ingredients", label: "Ingredients", desc: "Ingredient co-occurrence" },
  { mode: "cuisines", label: "Cuisines", desc: "How cuisines connect" },
  { mode: "equipment", label: "Equipment", desc: "Meals by shared equipment" },
];

function GraphEvents({
  onClickNode,
  onHoverNode,
}: {
  onClickNode: (id: string | null) => void;
  onHoverNode: (id: string | null) => void;
}) {
  const registerEvents = useRegisterEvents();
  useEffect(() => {
    registerEvents({
      clickNode: (event) => onClickNode(event.node),
      clickStage: () => onClickNode(null),
      enterNode: (event) => onHoverNode(event.node),
      leaveNode: () => onHoverNode(null),
    });
  }, [registerEvents, onClickNode, onHoverNode]);
  return null;
}

function CameraNavigator({ targetNode }: { targetNode: string | null }) {
  const sigma = useSigma();
  useEffect(() => {
    if (!targetNode) return;
    const graph = sigma.getGraph();
    if (!graph.hasNode(targetNode)) return;
    const attrs = graph.getNodeAttributes(targetNode);
    sigma.getCamera().animate({ x: attrs.x, y: attrs.y, ratio: 0.15 }, { duration: 400 });
  }, [targetNode, sigma]);
  return null;
}

function GraphSetup({
  data,
  viewMode,
  filters,
  hoveredNode,
  selectedNode,
  searchMatch,
  similarityThreshold,
  colorBy,
  expandedMeal,
  hidePantryStaples,
}: {
  data: GraphData;
  viewMode: ViewMode;
  filters: FilterState;
  hoveredNode: string | null;
  selectedNode: string | null;
  searchMatch: string | null;
  similarityThreshold: number;
  colorBy: ColorByMode;
  expandedMeal: string | null;
  hidePantryStaples: boolean;
}) {
  const loadGraph = useLoadGraph();
  const setSettings = useSetSettings();
  const sigma = useSigma();
  const prevExpandedRef = useRef<string | null>(null);

  useEffect(() => {
    let graph: Graph;
    switch (viewMode) {
      case "meals":
        graph = buildMealGraph(data, colorBy);
        break;
      case "ingredients":
        graph = buildIngredientGraph(data, hidePantryStaples);
        break;
      case "cuisines":
        graph = buildCuisineGraph(data);
        break;
      case "equipment":
        graph = buildEquipmentGraph(data);
        break;
    }

    loadGraph(graph);

    if (viewMode === "ingredients" || viewMode === "equipment") {
      const settings = forceAtlas2.inferSettings(graph);
      settings.gravity = 3;
      settings.scalingRatio = 10;
      settings.barnesHutOptimize = true;
      forceAtlas2.assign(graph, { iterations: 300, settings });
    }

    sigma.getCamera().animatedReset();
    prevExpandedRef.current = null;
  }, [data, viewMode, colorBy, hidePantryStaples, loadGraph, sigma]);

  useEffect(() => {
    if (viewMode !== "meals") return;
    const graph = sigma.getGraph();
    graph.forEachNode((id, attrs) => {
      if (attrs.nodeType === "meal") {
        graph.setNodeAttribute(id, "color", getNodeColor(colorBy, {
          cuisine: attrs.cuisine, difficulty: attrs.difficulty,
          mealType: attrs.mealType, costPerServing: attrs.costPerServing,
          seasons: attrs.seasons,
        }));
      }
    });
    sigma.refresh();
  }, [colorBy, sigma, viewMode]);

  useEffect(() => {
    if (viewMode !== "meals") return;
    const graph = sigma.getGraph();
    const prev = prevExpandedRef.current;

    if (prev && prev !== expandedMeal) {
      const toRemove: string[] = [];
      graph.forEachNode((id, attrs) => {
        if (attrs.nodeType === "ingredient" && attrs.parentMeal === prev) toRemove.push(id);
      });
      toRemove.forEach((id) => {
        graph.forEachEdge(id, (edge) => graph.dropEdge(edge));
        graph.dropNode(id);
      });
    }

    if (expandedMeal && graph.hasNode(expandedMeal)) {
      const mealAttrs = graph.getNodeAttributes(expandedMeal);
      const mealNode = data.nodes.find((n) => n.id === expandedMeal) as MealNode | undefined;
      if (mealNode) {
        const ings = mealNode.ingredients.filter((i) => !i.isOptional);
        const angleStep = (2 * Math.PI) / Math.max(ings.length, 1);
        ings.forEach((ing, i) => {
          const ingNodeId = `${expandedMeal}:ing:${i}`;
          if (graph.hasNode(ingNodeId)) return;
          const angle = angleStep * i - Math.PI / 2;
          graph.addNode(ingNodeId, {
            label: ing.name, x: mealAttrs.x + Math.cos(angle) * 8,
            y: mealAttrs.y + Math.sin(angle) * 8, size: 3,
            color: getIngredientCategoryColor(ing.category),
            nodeType: "ingredient", parentMeal: expandedMeal, category: ing.category,
          });
          graph.addEdge(expandedMeal, ingNodeId, {
            size: 0.5, color: getIngredientCategoryColor(ing.category) + "66", edgeType: "ingredient",
          });
        });
      }
    }
    prevExpandedRef.current = expandedMeal;
    sigma.refresh();
  }, [expandedMeal, data, sigma, viewMode]);

  useEffect(() => {
    const activeNode = hoveredNode || selectedNode;

    setSettings({
      nodeReducer: (node, attrs) => {
        const res = { ...attrs };
        const g = sigma.getGraph();
        const nd = g.getNodeAttributes(node);

        if (viewMode === "meals" && nd.nodeType === "meal") {
          if (filters.cuisines.length > 0 && !filters.cuisines.includes(nd.cuisine)) { res.hidden = true; return res; }
          if (filters.mealTypes.length > 0 && !filters.mealTypes.includes(nd.mealType)) { res.hidden = true; return res; }
          if (filters.difficulties.length > 0 && !filters.difficulties.includes(nd.difficulty)) { res.hidden = true; return res; }
          if (filters.dietaryTags.length > 0) {
            const tags = nd.dietaryTags || [];
            if (!filters.dietaryTags.every((t: string) => tags.includes(t))) { res.hidden = true; return res; }
          }
        }

        if (viewMode === "ingredients" && nd.nodeType === "ingredient") {
          if (filters.ingredientCategories.length > 0 && !filters.ingredientCategories.includes(nd.category)) {
            res.hidden = true; return res;
          }
        }

        if (viewMode === "equipment" && nd.nodeType === "meal") {
          if (filters.equipment.length > 0) {
            const mealEquip: string[] = nd.equipment || [];
            if (!filters.equipment.every((e: string) => mealEquip.includes(e))) { res.hidden = true; return res; }
          }
        }

        if (nd.nodeType === "ingredient" && nd.parentMeal && nd.parentMeal !== expandedMeal) {
          res.hidden = true; return res;
        }

        if (searchMatch && node === searchMatch) { res.highlighted = true; res.zIndex = 10; }

        if (activeNode) {
          if (node === activeNode) { res.highlighted = true; res.zIndex = 10; }
          else if (g.hasNode(activeNode) && g.areNeighbors(node, activeNode)) { res.highlighted = true; res.zIndex = 5; }
          else { res.color = `${(res.color || "#94a3b8").replace(/[0-9a-f]{2}$/i, "")}33`; res.label = ""; }
        }
        return res;
      },
      edgeReducer: (edge, attrs) => {
        const res = { ...attrs };
        const g = sigma.getGraph();
        const ed = g.getEdgeAttributes(edge);
        if (viewMode === "meals" && ed.edgeType === "similarity" && ed.overlapRatio < similarityThreshold) { res.hidden = true; return res; }
        const [source, target] = g.extremities(edge);
        const sd = g.getNodeAttributes(source);
        const td = g.getNodeAttributes(target);
        if (sd.hidden || td.hidden) { res.hidden = true; return res; }
        if (activeNode && source !== activeNode && target !== activeNode) { res.hidden = true; }
        return res;
      },
      labelRenderedSizeThreshold: viewMode === "cuisines" ? 0 : 6,
      labelSize: viewMode === "cuisines" ? 14 : 12,
      labelColor: { color: "#e4e4e7" },
      defaultEdgeType: "line",
    });
  }, [filters, hoveredNode, selectedNode, searchMatch, similarityThreshold, expandedMeal, viewMode, setSettings, sigma]);

  return null;
}

export interface FilterState {
  cuisines: string[];
  mealTypes: string[];
  difficulties: string[];
  dietaryTags: string[];
  ingredientCategories: string[];
  equipment: string[];
}

export default function GraphExplorer() {
  const [data, setData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<ViewMode>("meals");
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [searchMatch, setSearchMatch] = useState<string | null>(null);
  const [similarityThreshold, setSimilarityThreshold] = useState(0.25);
  const [colorBy, setColorBy] = useState<ColorByMode>("cuisine");
  const [expandedMeal, setExpandedMeal] = useState<string | null>(null);
  const [hidePantryStaples, setHidePantryStaples] = useState(true);
  const [filters, setFilters] = useState<FilterState>({
    cuisines: [], mealTypes: [], difficulties: [], dietaryTags: [],
    ingredientCategories: [], equipment: [],
  });

  useEffect(() => {
    fetch("/graph.json").then((r) => r.json()).then((d) => { setData(d); setLoading(false); });
  }, []);

  const handleViewChange = useCallback((mode: ViewMode) => {
    setViewMode(mode);
    setSelectedNode(null);
    setExpandedMeal(null);
    setSearchMatch(null);
    setHoveredNode(null);
  }, []);

  const handleClickNode = useCallback((id: string | null) => {
    setSelectedNode(id);
    if (id && viewMode === "meals" && data) {
      const node = data.nodes.find((n) => n.id === id);
      if (node?.type === "meal") setExpandedMeal((prev) => (prev === id ? null : id));
    } else if (!id) {
      setExpandedMeal(null);
    }
  }, [data, viewMode]);

  const allEquipment = useMemo(() => {
    if (!data) return [];
    const set = new Set<string>();
    data.nodes.filter((n) => n.type === "meal").forEach((n) => (n as MealNode).equipment.forEach((e) => set.add(e)));
    return Array.from(set).sort();
  }, [data]);

  if (loading || !data) {
    return <div className="h-full w-full flex items-center justify-center"><div className="text-[var(--text-muted)] text-lg">Loading graph...</div></div>;
  }

  const selectedNodeData = selectedNode ? data.nodes.find((n) => n.id === selectedNode) || null : null;
  const selectedEdges = selectedNode
    ? data.edges.filter((e) => (e.source === selectedNode || e.target === selectedNode) && e.type === "similarity")
    : [];

  return (
    <div className="h-full w-full relative">
      <div className="absolute top-0 left-0 right-0 z-20 flex justify-center pt-3 pointer-events-none">
        <div className="flex gap-1 bg-[var(--surface)] border border-[var(--border)] rounded-lg p-1 pointer-events-auto">
          {VIEW_TABS.map((tab) => (
            <button
              key={tab.mode}
              onClick={() => handleViewChange(tab.mode)}
              title={tab.desc}
              className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                viewMode === tab.mode
                  ? "bg-[var(--accent)] text-black font-medium"
                  : "text-[var(--text-muted)] hover:text-[var(--text)] hover:bg-[var(--border)]"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <SigmaContainer
        className="sigma-container"
        settings={{ allowInvalidContainer: true, renderEdgeLabels: false, enableEdgeEvents: false, defaultNodeType: "circle", labelFont: "Inter, sans-serif", labelWeight: "500" }}
      >
        <GraphSetup
          data={data} viewMode={viewMode} filters={filters}
          hoveredNode={hoveredNode} selectedNode={selectedNode}
          searchMatch={searchMatch} similarityThreshold={similarityThreshold}
          colorBy={colorBy} expandedMeal={expandedMeal}
          hidePantryStaples={hidePantryStaples}
        />
        <GraphEvents onClickNode={handleClickNode} onHoverNode={setHoveredNode} />
        <CameraNavigator targetNode={searchMatch || selectedNode} />
      </SigmaContainer>

      <div className="absolute top-14 left-4 z-10 flex flex-col gap-3 max-w-[280px]">
        <SearchBar data={data} onSelect={setSearchMatch} viewMode={viewMode} />
        <FilterPanel
          meta={data.meta} filters={filters} onFiltersChange={setFilters}
          similarityThreshold={similarityThreshold} onSimilarityChange={setSimilarityThreshold}
          colorBy={colorBy} onColorByChange={setColorBy}
          viewMode={viewMode} allEquipment={allEquipment}
          hidePantryStaples={hidePantryStaples} onHidePantryStaplesChange={setHidePantryStaples}
        />
      </div>

      <div className="absolute bottom-4 left-4 z-10">
        <Legend colorBy={colorBy} viewMode={viewMode} showIngredients={expandedMeal !== null} />
      </div>

      {selectedNodeData && (
        <DetailPanel
          node={selectedNodeData} edges={selectedEdges} allNodes={data.nodes}
          data={data} viewMode={viewMode}
          onClose={() => { setSelectedNode(null); setExpandedMeal(null); }}
          onNavigate={handleClickNode}
        />
      )}

      <div className="absolute top-14 right-4 z-10 text-xs text-[var(--text-muted)]">
        {viewMode === "meals" && <>{data.meta.mealCount} meals &middot; {data.meta.similarityPairCount} connections</>}
        {viewMode === "ingredients" && <>{data.meta.ingredientCount} ingredients</>}
        {viewMode === "cuisines" && <>{data.meta.cuisines.length} cuisines</>}
        {viewMode === "equipment" && <>{data.meta.mealCount} meals</>}
      </div>
    </div>
  );
}
