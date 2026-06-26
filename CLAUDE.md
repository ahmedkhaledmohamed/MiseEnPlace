# MiseEnPlace — Claude Context

## Project Overview

Visual-first home cooking app built on a meal-ingredient graph database. The graph connects meals through shared ingredients, techniques, cuisines, and seasons — enabling cost-optimized weekly meal planning, zero-waste grocery lists, and constraint-based discovery.

## Current Phase

**Phase 0: Pipeline First** — Building the offline content generation pipeline before any UI work.

Pipeline stages: Generate (LLM) → Ground (web verification) → Cost (price estimation) → Image (AI generation) → Graph (build relationships) → Validate

## Key Decisions

- **Platform**: Web MVP (Next.js on Vercel) to test graph quality; native mobile is SwiftUI (iOS) + Jetpack Compose (Android) — no cross-platform frameworks
- **Database**: PostgreSQL (Neon) for MVP, Neo4j when graph queries demand it
- **Pipeline**: Python + Claude API for meal generation
- **Market**: Canada-first (Ontario grocery prices)
- **Images**: AI-generated for MVP

## Repo Structure

```
pipeline/          → Python scripts for offline content generation
docs/              → Research document, design specs
```

## Conventions

- Follow existing patterns
- Pipeline scripts are Python 3.12+
- Web app will be Next.js with TypeScript when we get there
- All generated content is JSON with strict schemas
