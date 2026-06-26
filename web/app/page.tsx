"use client";

import dynamic from "next/dynamic";

const GraphExplorer = dynamic(() => import("../components/GraphExplorer"), {
  ssr: false,
  loading: () => (
    <div className="h-screen w-screen flex items-center justify-center">
      <div className="text-[var(--text-muted)] text-lg">Loading graph...</div>
    </div>
  ),
});

export default function Home() {
  return (
    <div className="h-screen w-screen">
      <GraphExplorer />
    </div>
  );
}
