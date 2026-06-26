"use client";

import { useEffect, useState } from "react";
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
import { CUISINE_COLORS, getCuisineColor } from "./colors";
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
  const sigma = useSigma();

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
  filters,
  hoveredNode,
  selectedNode,
  searchMatch,
  similarityThreshold,
}: {
  data: GraphData;
  filters: FilterState;
  hoveredNode: string | null;
  selectedNode: string | null;
  searchMatch: string | null;
  similarityThreshold: number;
}) {
  const loadGraph = useLoadGraph();
  const setSettings = useSetSettings();
  const sigma = useSigma();

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
          color: getCuisineColor(m.cuisine),
          nodeType: "meal",
          cuisine: m.cuisine,
          mealType: m.mealType,
          difficulty: m.difficulty,
          costPerServing: m.costPerServing,
          totalTime: m.totalTime,
          dietaryTags: m.dietaryTags,
        });
      }
    }

    for (const edge of data.edges) {
      if (edge.type === "similarity" && graph.hasNode(edge.source) && graph.hasNode(edge.target)) {
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
    const activeNode = hoveredNode || selectedNode;

    setSettings({
      nodeReducer: (node, attrs) => {
        const res = { ...attrs };
        const g = sigma.getGraph();
        const nodeData = g.getNodeAttributes(node);

        if (nodeData.nodeType === "meal") {
          if (filters.cuisines.length > 0 && !filters.cuisines.includes(nodeData.cuisine)) {
            res.hidden = true;
            return res;
          }
          if (filters.mealTypes.length > 0 && !filters.mealTypes.includes(nodeData.mealType)) {
            res.hidden = true;
            return res;
          }
          if (filters.difficulties.length > 0 && !filters.difficulties.includes(nodeData.difficulty)) {
            res.hidden = true;
            return res;
          }
          if (filters.dietaryTags.length > 0) {
            const tags = nodeData.dietaryTags || [];
            if (!filters.dietaryTags.every((t: string) => tags.includes(t))) {
              res.hidden = true;
              return res;
            }
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
            res.color = `${res.color}33`;
            res.label = "";
          }
        }

        return res;
      },
      edgeReducer: (edge, attrs) => {
        const res = { ...attrs };
        const g = sigma.getGraph();
        const edgeData = g.getEdgeAttributes(edge);

        if (edgeData.overlapRatio !== undefined && edgeData.overlapRatio < similarityThreshold) {
          res.hidden = true;
          return res;
        }

        const [source, target] = g.extremities(edge);
        const sourceData = g.getNodeAttributes(source);
        const targetData = g.getNodeAttributes(target);

        if (sourceData.hidden || targetData.hidden) {
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
      labelRenderedSizeThreshold: 8,
      labelSize: 12,
      labelColor: { color: "#e4e4e7" },
      defaultEdgeType: "line",
    });
  }, [filters, hoveredNode, selectedNode, searchMatch, similarityThreshold, setSettings, sigma]);

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
          e.type === "similarity"
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
        />
        <GraphEvents
          onClickNode={setSelectedNode}
          onHoverNode={setHoveredNode}
        />
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
        />
      </div>

      <div className="absolute bottom-4 left-4 z-10">
        <Legend />
      </div>

      {selectedNodeData && (
        <DetailPanel
          node={selectedNodeData}
          edges={selectedEdges}
          allNodes={data.nodes}
          onClose={() => setSelectedNode(null)}
          onNavigate={setSelectedNode}
        />
      )}

      <div className="absolute top-4 right-4 z-10 text-xs text-[var(--text-muted)]">
        {data.meta.mealCount} meals &middot; {data.meta.ingredientCount} ingredients &middot; {data.meta.similarityPairCount} connections
      </div>
    </div>
  );
}
