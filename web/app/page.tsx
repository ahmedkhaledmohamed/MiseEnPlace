"use client";

import Link from "next/link";

const STATS = [
  { value: "120", label: "Meals" },
  { value: "282", label: "Ingredients" },
  { value: "25", label: "Cuisines" },
  { value: "976", label: "Connections" },
];

const FEATURES = [
  {
    title: "The Meal Graph",
    description:
      "Meals aren't isolated recipes — they're nodes in a graph connected through shared ingredients, techniques, and cuisines. This graph powers everything: smart planning, zero-waste grocery lists, and discovery you can't get from a flat recipe database.",
    icon: "🔗",
  },
  {
    title: "Cost-Aware Planning",
    description:
      "Set a weekly budget and get meal plans that maximize variety while minimizing grocery cost. The graph knows which meals share ingredients — so buying for 5 meals costs less than 5 separate trips.",
    icon: "💰",
  },
  {
    title: "Visual-First Discovery",
    description:
      "Browse meals like you browse Instagram — beautiful cards, quick filters by cuisine, difficulty, dietary needs, or time. Tap into any meal for the full recipe with step-by-step instructions.",
    icon: "📸",
  },
  {
    title: "Smart Grocery Lists",
    description:
      "Plan your week, get one unified grocery list. Quantities aggregated across meals, grouped by store section, with cost estimates. No more buying onions three times.",
    icon: "🛒",
  },
];

const VIEWS = [
  {
    title: "Meals",
    description: "120 meals connected by ingredient similarity, clustered by cuisine",
  },
  {
    title: "Ingredients",
    description: "282 ingredients connected by co-occurrence — see how garlic bridges 31 meals across 15 cuisines",
  },
  {
    title: "Cuisines",
    description: "25 food traditions connected by shared ingredients — discover cross-cuisine bridges",
  },
  {
    title: "Equipment",
    description: "Find meals by equipment — 'I only have a skillet and cutting board'",
  },
];

const PIPELINE_STAGES = [
  { stage: "Generate", description: "LLM creates structured meal records across 25 cuisines", status: "done" },
  { stage: "Ground", description: "Each recipe verified against real-world cooking knowledge", status: "done" },
  { stage: "Cost", description: "Ingredients priced against Canadian grocery data", status: "done" },
  { stage: "Image", description: "AI-generated food photography for each meal", status: "next" },
  { stage: "Graph", description: "Ingredient overlaps, substitutions, similarity computed", status: "done" },
  { stage: "Validate", description: "Consistency checks, quality scoring, outlier detection", status: "done" },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-[var(--bg)]/80 backdrop-blur-md border-b border-[var(--border)]">
        <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
          <span className="font-semibold text-lg tracking-tight">
            <span className="text-[var(--accent)]">Mise</span>EnPlace
          </span>
          <div className="flex items-center gap-4">
            <Link
              href="/explore"
              className="text-sm text-[var(--text-muted)] hover:text-[var(--text)] transition-colors"
            >
              Explore Graph
            </Link>
            <a
              href="#waitlist"
              className="text-sm px-4 py-1.5 rounded-full bg-[var(--accent)] text-black font-medium hover:bg-[var(--accent)]/90 transition-colors"
            >
              Get Early Access
            </a>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold tracking-tight leading-tight mb-6">
            Cook smarter with the{" "}
            <span className="text-[var(--accent)]">meal graph</span>
          </h1>
          <p className="text-xl text-[var(--text-muted)] max-w-2xl mx-auto mb-10 leading-relaxed">
            A visual-first cooking app powered by an intelligent graph that connects meals through shared ingredients, techniques, and cuisines — enabling cost-optimized weekly planning and zero-waste grocery lists.
          </p>
          <div className="flex gap-4 justify-center mb-16">
            <Link
              href="/explore"
              className="px-6 py-3 rounded-lg bg-[var(--accent)] text-black font-semibold hover:bg-[var(--accent)]/90 transition-colors"
            >
              Explore the Graph
            </Link>
            <a
              href="#waitlist"
              className="px-6 py-3 rounded-lg border border-[var(--border)] text-[var(--text)] font-semibold hover:bg-[var(--surface)] transition-colors"
            >
              Join Waitlist
            </a>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl mx-auto">
            {STATS.map((stat) => (
              <div key={stat.label} className="bg-[var(--surface)] rounded-xl p-4 border border-[var(--border)]">
                <div className="text-3xl font-bold text-[var(--accent)] mb-1">{stat.value}</div>
                <div className="text-sm text-[var(--text-muted)]">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Core insight */}
      <section className="py-20 px-6 bg-[var(--surface)]">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold mb-4 text-center">The core insight</h2>
          <p className="text-center text-[var(--text-muted)] text-lg max-w-3xl mx-auto mb-12">
            No cooking app models meals as a connected graph. They're all flat lists. MiseEnPlace treats the graph as the product — every feature emerges from ingredient relationships.
          </p>
          <div className="grid md:grid-cols-2 gap-6">
            {FEATURES.map((feature) => (
              <div key={feature.title} className="bg-[var(--bg)] rounded-xl p-6 border border-[var(--border)]">
                <div className="text-2xl mb-3">{feature.icon}</div>
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-sm text-[var(--text-muted)] leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Graph Explorer */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold mb-4 text-center">Four ways to explore</h2>
          <p className="text-center text-[var(--text-muted)] text-lg max-w-2xl mx-auto mb-10">
            The interactive graph explorer lets you see the data from four different angles. Each view reveals different patterns.
          </p>
          <div className="grid md:grid-cols-2 gap-4 mb-8">
            {VIEWS.map((view) => (
              <div key={view.title} className="bg-[var(--surface)] rounded-xl p-5 border border-[var(--border)]">
                <h3 className="font-semibold mb-1">{view.title}</h3>
                <p className="text-sm text-[var(--text-muted)]">{view.description}</p>
              </div>
            ))}
          </div>
          <div className="text-center">
            <Link
              href="/explore"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-[var(--surface)] border border-[var(--border)] font-medium hover:bg-[var(--border)] transition-colors"
            >
              Open Graph Explorer
              <span className="text-[var(--text-muted)]">&rarr;</span>
            </Link>
          </div>
        </div>
      </section>

      {/* Pipeline */}
      <section className="py-20 px-6 bg-[var(--surface)]">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold mb-4 text-center">Built on a 6-stage pipeline</h2>
          <p className="text-center text-[var(--text-muted)] text-lg max-w-2xl mx-auto mb-10">
            Every meal goes through automated generation, verification, costing, and graph indexing before it reaches you.
          </p>
          <div className="space-y-3 max-w-xl mx-auto">
            {PIPELINE_STAGES.map((stage, i) => (
              <div key={stage.stage} className="flex items-start gap-4 bg-[var(--bg)] rounded-lg p-4 border border-[var(--border)]">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-sm font-bold ${stage.status === "done" ? "bg-green-900/50 text-green-400" : "bg-amber-900/50 text-amber-400"}`}>
                  {i + 1}
                </div>
                <div>
                  <div className="font-medium">{stage.stage}</div>
                  <div className="text-sm text-[var(--text-muted)]">{stage.description}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Waitlist */}
      <section id="waitlist" className="py-20 px-6">
        <div className="max-w-xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Coming to iOS</h2>
          <p className="text-[var(--text-muted)] text-lg mb-8">
            Beautiful meal feed, weekly planner, smart grocery lists — powered by the meal graph. Built with SwiftUI, local-first, no account required.
          </p>
          <form
            className="flex gap-2 max-w-md mx-auto"
            onSubmit={(e) => e.preventDefault()}
          >
            <input
              type="email"
              placeholder="your@email.com"
              className="flex-1 px-4 py-3 rounded-lg bg-[var(--surface)] border border-[var(--border)] text-[var(--text)] placeholder:text-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)]"
            />
            <button
              type="submit"
              className="px-6 py-3 rounded-lg bg-[var(--accent)] text-black font-semibold hover:bg-[var(--accent)]/90 transition-colors shrink-0"
            >
              Notify Me
            </button>
          </form>
          <p className="text-xs text-[var(--text-muted)] mt-3">No spam. One email when the app launches.</p>
        </div>
      </section>

      {/* Tech stack */}
      <section className="py-16 px-6 border-t border-[var(--border)]">
        <div className="max-w-4xl mx-auto">
          <h3 className="text-sm font-medium text-[var(--text-muted)] uppercase tracking-wider mb-6 text-center">Built with</h3>
          <div className="flex flex-wrap justify-center gap-x-8 gap-y-3 text-sm text-[var(--text-muted)]">
            <span>Python</span>
            <span>Together AI (Llama 3.3 70B)</span>
            <span>FLUX.1</span>
            <span>SQLite</span>
            <span>Next.js</span>
            <span>Sigma.js</span>
            <span>Graphology</span>
            <span>Vercel</span>
            <span>SwiftUI (iOS)</span>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-[var(--border)]">
        <div className="max-w-4xl mx-auto flex justify-between items-center text-sm text-[var(--text-muted)]">
          <span>
            <span className="text-[var(--accent)]">Mise</span>EnPlace
          </span>
          <div className="flex gap-4">
            <Link href="/explore" className="hover:text-[var(--text)] transition-colors">
              Graph Explorer
            </Link>
            <a href="https://github.com/ahmedkhaledmohamed/MiseEnPlace" className="hover:text-[var(--text)] transition-colors">
              GitHub
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
