"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Graph from "graphology";
import {
  SigmaContainer,
  useRegisterEvents,
  useSigma,
  useLoadGraph,
  useSetSettings,
} from "@react-sigma/core";
import "@react-sigma/core/lib/style.css";
import { GraphData, MealNode, IngredientNode } from "./types";
import {
  ColorByMode,
  getNodeColor,
  getIngredientCategoryColor,
} from "./colors";
import SearchBar from "./SearchBar";
import FilterPanel from "./FilterPanel";
import DetailPanel from "./DetailPanel";
import Legend from "./Legend";

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
    sigma.getCamera().animate(
      { x: attrs.x, y: attrs.y, ratio: 0.15 },
      { duration: 400 },
    );
  }, [targetNode, sigma]);

  return null;
}

function GraphSetup({
  data,
  filters,
  hoveredNode,
  selectedNode,
  searchMatch,
  similarityThreshold,
  colorBy,
  expandedMeal,
}: {
  data: GraphData;
  filters: FilterState;
  hoveredNode: string | null;
  selectedNode: string | null;
  searchMatch: string | null;
  similarityThreshold: number;
  colorBy: ColorByMode;
  expandedMeal: string | null;
}) {
  const loadGraph = useLoadGraph();
  const setSettings = useSetSettings();
  const sigma = useSigma();
  const prevExpandedRef = useRef<string | null>(null);

  useEffect(() => {
    const graph = new Graph();

    for (const node of data.nodes) {
      if (node.type === "meal") {
        const m = node as MealNode;
        const size = 4 + (m.ingredientCount / 14) * 16;
        graph.addNode(m.id, {
          label: m.label,
          x: m.x ?? Math.random() * 100,
          y: m.y ?? Math.random() * 100,
          size,
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
    }

    for (const edge of data.edges) {
      if (
        edge.type === "similarity" &&
        graph.hasNode(edge.source) &&
        graph.hasNode(edge.target)
      ) {
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
    }

    loadGraph(graph);
    sigma.getCamera().animatedReset();
  }, [data, loadGraph, sigma]);

  useEffect(() => {
    const graph = sigma.getGraph();
    graph.forEachNode((id, attrs) => {
      if (attrs.nodeType === "meal") {
        graph.setNodeAttribute(
          id,
          "color",
          getNodeColor(colorBy, {
            cuisine: attrs.cuisine,
            difficulty: attrs.difficulty,
            mealType: attrs.mealType,
            costPerServing: attrs.costPerServing,
            seasons: attrs.seasons,
          }),
        );
      }
    });
    sigma.refresh();
  }, [colorBy, sigma]);

  useEffect(() => {
    const graph = sigma.getGraph();
    const prev = prevExpandedRef.current;

    if (prev && prev !== expandedMeal) {
      const toRemove: string[] = [];
      graph.forEachNode((id, attrs) => {
        if (attrs.nodeType === "ingredient" && attrs.parentMeal === prev) {
          toRemove.push(id);
        }
      });
      toRemove.forEach((id) => {
        graph.forEachEdge(id, (edge) => graph.dropEdge(edge));
        graph.dropNode(id);
      });
    }

    if (expandedMeal && graph.hasNode(expandedMeal)) {
      const mealAttrs = graph.getNodeAttributes(expandedMeal);
      const mealNode = data.nodes.find((n) => n.id === expandedMeal) as
        | MealNode
        | undefined;
      if (mealNode) {
        const ings = mealNode.ingredients.filter((i) => !i.isOptional);
        const angleStep = (2 * Math.PI) / Math.max(ings.length, 1);
        const radius = 8;

        ings.forEach((ing, i) => {
          const ingNodeId = `${expandedMeal}:ing:${i}`;
          if (graph.hasNode(ingNodeId)) return;
          const angle = angleStep * i - Math.PI / 2;
          graph.addNode(ingNodeId, {
            label: ing.name,
            x: mealAttrs.x + Math.cos(angle) * radius,
            y: mealAttrs.y + Math.sin(angle) * radius,
            size: 3,
            color: getIngredientCategoryColor(ing.category),
            nodeType: "ingredient",
            parentMeal: expandedMeal,
            category: ing.category,
          });
          graph.addEdge(expandedMeal, ingNodeId, {
            size: 0.5,
            color: getIngredientCategoryColor(ing.category) + "66",
            edgeType: "ingredient",
          });
        });
      }
    }

    prevExpandedRef.current = expandedMeal;
    sigma.refresh();
  }, [expandedMeal, data, sigma]);

  useEffect(() => {
    const activeNode = hoveredNode || selectedNode;

    setSettings({
      nodeReducer: (node, attrs) => {
        const res = { ...attrs };
        const g = sigma.getGraph();
        const nd = g.getNodeAttributes(node);

        if (nd.nodeType === "meal") {
          if (
            filters.cuisines.length > 0 &&
            !filters.cuisines.includes(nd.cuisine)
          ) {
            res.hidden = true;
            return res;
          }
          if (
            filters.mealTypes.length > 0 &&
            !filters.mealTypes.includes(nd.mealType)
          ) {
            res.hidden = true;
            return res;
          }
          if (
            filters.difficulties.length > 0 &&
            !filters.difficulties.includes(nd.difficulty)
          ) {
            res.hidden = true;
            return res;
          }
          if (filters.dietaryTags.length > 0) {
            const tags = nd.dietaryTags || [];
            if (!filters.dietaryTags.every((t: string) => tags.includes(t))) {
              res.hidden = true;
              return res;
            }
          }
        }

        if (nd.nodeType === "ingredient") {
          if (nd.parentMeal && nd.parentMeal !== expandedMeal) {
            res.hidden = true;
            return res;
          }
        }

        if (searchMatch && node === searchMatch) {
          res.highlighted = true;
          res.zIndex = 10;
        }

        if (activeNode) {
          if (node === activeNode) {
            res.highlighted = true;
            res.zIndex = 10;
          } else if (g.hasNode(activeNode) && g.areNeighbors(node, activeNode)) {
            res.highlighted = true;
            res.zIndex = 5;
          } else {
            res.color = `${(res.color || "#94a3b8").replace(/[0-9a-f]{2}$/i, "")}33`;
            res.label = "";
          }
        }

        return res;
      },
      edgeReducer: (edge, attrs) => {
        const res = { ...attrs };
        const g = sigma.getGraph();
        const ed = g.getEdgeAttributes(edge);

        if (
          ed.overlapRatio !== undefined &&
          ed.edgeType === "similarity" &&
          ed.overlapRatio < similarityThreshold
        ) {
          res.hidden = true;
          return res;
        }

        const [source, target] = g.extremities(edge);
        const sd = g.getNodeAttributes(source);
        const td = g.getNodeAttributes(target);

        if (sd.hidden || td.hidden) {
          res.hidden = true;
          return res;
        }

        if (activeNode) {
          if (source !== activeNode && target !== activeNode) {
            res.hidden = true;
          }
        }

        return res;
      },
      labelRenderedSizeThreshold: 6,
      labelSize: 12,
      labelColor: { color: "#e4e4e7" },
      defaultEdgeType: "line",
    });
  }, [
    filters,
    hoveredNode,
    selectedNode,
    searchMatch,
    similarityThreshold,
    expandedMeal,
    setSettings,
    sigma,
  ]);

  return null;
}

export interface FilterState {
  cuisines: string[];
  mealTypes: string[];
  difficulties: string[];
  dietaryTags: string[];
}

export default function GraphExplorer() {
  const [data, setData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [searchMatch, setSearchMatch] = useState<string | null>(null);
  const [similarityThreshold, setSimilarityThreshold] = useState(0.25);
  const [colorBy, setColorBy] = useState<ColorByMode>("cuisine");
  const [expandedMeal, setExpandedMeal] = useState<string | null>(null);
  const [filters, setFilters] = useState<FilterState>({
    cuisines: [],
    mealTypes: [],
    difficulties: [],
    dietaryTags: [],
  });

  useEffect(() => {
    fetch("/graph.json")
      .then((r) => r.json())
      .then((d) => {
        setData(d);
        setLoading(false);
      });
  }, []);

  const handleClickNode = useCallback(
    (id: string | null) => {
      setSelectedNode(id);
      if (id && data) {
        const node = data.nodes.find((n) => n.id === id);
        if (node?.type === "meal") {
          setExpandedMeal((prev) => (prev === id ? null : id));
        }
      } else {
        setExpandedMeal(null);
      }
    },
    [data],
  );

  if (loading || !data) {
    return (
      <div className="h-full w-full flex items-center justify-center">
        <div className="text-[var(--text-muted)] text-lg">Loading graph...</div>
      </div>
    );
  }

  const selectedNodeData = selectedNode
    ? data.nodes.find((n) => n.id === selectedNode) || null
    : null;

  const selectedEdges = selectedNode
    ? data.edges.filter(
        (e) =>
          (e.source === selectedNode || e.target === selectedNode) &&
          e.type === "similarity",
      )
    : [];

  return (
    <div className="h-full w-full relative">
      <SigmaContainer
        className="sigma-container"
        settings={{
          allowInvalidContainer: true,
          renderEdgeLabels: false,
          enableEdgeEvents: false,
          defaultNodeType: "circle",
          labelFont: "Inter, sans-serif",
          labelWeight: "500",
        }}
      >
        <GraphSetup
          data={data}
          filters={filters}
          hoveredNode={hoveredNode}
          selectedNode={selectedNode}
          searchMatch={searchMatch}
          similarityThreshold={similarityThreshold}
          colorBy={colorBy}
          expandedMeal={expandedMeal}
        />
        <GraphEvents onClickNode={handleClickNode} onHoverNode={setHoveredNode} />
        <CameraNavigator targetNode={searchMatch || selectedNode} />
      </SigmaContainer>

      <div className="absolute top-4 left-4 z-10 flex flex-col gap-3 max-w-[280px]">
        <SearchBar data={data} onSelect={setSearchMatch} />
        <FilterPanel
          meta={data.meta}
          filters={filters}
          onFiltersChange={setFilters}
          similarityThreshold={similarityThreshold}
          onSimilarityChange={setSimilarityThreshold}
          colorBy={colorBy}
          onColorByChange={setColorBy}
        />
      </div>

      <div className="absolute bottom-4 left-4 z-10">
        <Legend colorBy={colorBy} showIngredients={expandedMeal !== null} />
      </div>

      {selectedNodeData && (
        <DetailPanel
          node={selectedNodeData}
          edges={selectedEdges}
          allNodes={data.nodes}
          onClose={() => {
            setSelectedNode(null);
            setExpandedMeal(null);
          }}
          onNavigate={handleClickNode}
        />
      )}

      <div className="absolute top-4 right-4 z-10 text-xs text-[var(--text-muted)]">
        {data.meta.mealCount} meals &middot; {data.meta.ingredientCount}{" "}
        ingredients &middot; {data.meta.similarityPairCount} connections
      </div>
    </div>
  );
}
