# MiseEnPlace

A visual-first home cooking app powered by an intelligent meal-ingredient graph.

Browse beautiful meals, plan your week, get a smart grocery list — all optimized for your budget, time, and season.

## What Makes This Different

The core is a **meal graph**: meals connected through shared ingredients, techniques, cuisines, and seasons. This graph powers cost-optimized weekly planning, zero-waste grocery lists, and intelligent meal suggestions.

## Architecture

```
pipeline/          → Offline content generation (LLM → ground → cost → image → graph)
docs/              → Research document, design specs
```

## Status

Phase 0: Building the offline meal generation pipeline.

See [docs/RESEARCH.md](docs/RESEARCH.md) for the full product design document.
