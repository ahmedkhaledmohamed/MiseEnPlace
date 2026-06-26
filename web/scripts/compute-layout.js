/**
 * Pre-compute ForceAtlas2 layout for graph.json.
 * Run: node scripts/compute-layout.js
 */

import { readFileSync, writeFileSync } from "fs";
import Graph from "graphology";
import forceAtlas2 from "graphology-layout-forceatlas2";
import { circular } from "graphology-layout";

const GRAPH_PATH = new URL("../public/graph.json", import.meta.url).pathname;

const data = JSON.parse(readFileSync(GRAPH_PATH, "utf-8"));

const graph = new Graph();

const cuisineGroups = {};
const mealNodes = data.nodes.filter((n) => n.type === "meal");

mealNodes.forEach((n) => {
  if (!cuisineGroups[n.cuisine]) cuisineGroups[n.cuisine] = [];
  cuisineGroups[n.cuisine].push(n.id);
});

mealNodes.forEach((n) => {
  graph.addNode(n.id, { label: n.label, cuisine: n.cuisine });
});

data.edges
  .filter((e) => e.type === "similarity")
  .forEach((e, i) => {
    if (graph.hasNode(e.source) && graph.hasNode(e.target)) {
      graph.addEdge(e.source, e.target, { weight: e.overlapRatio, id: `sim-${i}` });
    }
  });

circular.assign(graph);

const settings = forceAtlas2.inferSettings(graph);
settings.gravity = 2;
settings.scalingRatio = 10;
settings.barnesHutOptimize = true;
settings.strongGravityMode = true;

forceAtlas2.assign(graph, { iterations: 600, settings });

const cuisineCentroids = {};
for (const [cuisine, ids] of Object.entries(cuisineGroups)) {
  let cx = 0, cy = 0;
  ids.forEach((id) => {
    const attrs = graph.getNodeAttributes(id);
    cx += attrs.x;
    cy += attrs.y;
  });
  cuisineCentroids[cuisine] = { x: cx / ids.length, y: cy / ids.length };
}

graph.forEachNode((id, attrs) => {
  const centroid = cuisineCentroids[attrs.cuisine];
  if (centroid) {
    attrs.x = attrs.x * 0.8 + centroid.x * 0.2;
    attrs.y = attrs.y * 0.8 + centroid.y * 0.2;
  }
});

const positions = {};
graph.forEachNode((id, attrs) => {
  positions[id] = { x: attrs.x, y: attrs.y };
});

for (const node of data.nodes) {
  if (positions[node.id]) {
    node.x = positions[node.id].x;
    node.y = positions[node.id].y;
  }
}

writeFileSync(GRAPH_PATH, JSON.stringify(data));
console.log(`Layout computed for ${mealNodes.length} meal nodes, written to ${GRAPH_PATH}`);
