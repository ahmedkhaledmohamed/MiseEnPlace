# MiseEnPlace — Research & Product Design Document

## 1. Executive Summary

MiseEnPlace is a visual-first home cooking app built on top of an intelligent meal-ingredient graph database. The core insight: meals are not isolated recipes — they are nodes in a rich graph connected through shared ingredients, techniques, cuisines, seasons, and cost profiles. By modeling this graph explicitly and generating a massive inventory offline, we can power experiences no existing cooking app offers: true cost-optimized weekly meal planning, zero-waste grocery lists, constraint-based meal discovery (budget, time, season, dietary), and ingredient-aware suggestions that maximize what you already have.

The app surface is Instagram-like — scroll through beautifully presented meals, tap into rich detail pages with steps, timings, costs, and eventually voice/video walkthroughs. But the magic is underneath: a graph engine that understands how meals relate, what they cost, and how to compose optimal weeks of cooking.

---

## 2. Product Vision

### The Problem

Home cooking apps today fall into two categories:

1. **Recipe databases** (AllRecipes, Epicurious, NYT Cooking) — search-driven, text-heavy, no intelligence about how recipes relate or compose into weekly plans. No cost awareness.

2. **Meal planning tools** (Mealime, Plan to Eat) — utilitarian, not inspiring. Focus on logistics over discovery. Limited ingredient intelligence.

Neither combines **visual discovery** (the dopamine loop of Instagram) with **intelligent planning** (constraint-aware, cost-optimized, waste-reducing).

### The Opportunity

Build the system that treats meals as a connected graph, not a flat list. This unlocks:

- **"I have $80 and 3 hours on Sunday"** → Here are 5 meals for the week that share ingredients, fit your budget, and respect your time.
- **"I bought too much chicken"** → Here are 4 meals this week that use chicken in different ways.
- **"It's winter and I want comfort food under $5/serving"** → Seasonal, budget-aware, filtered discovery.
- **"I made meal A — what should I make tomorrow to use the leftover herbs?"** → Graph traversal from current state.

### Core Thesis

The meal graph is the product. Everything else — the beautiful UI, the meal planning, the grocery lists, the cost estimates — is a view on top of the graph. Build the graph right, and the features emerge naturally.

---

## 3. Market Landscape

### Direct Competitors

| App | Strengths | Gaps |
|-----|-----------|------|
| **NYT Cooking** | High-quality curated recipes, strong brand | No planning, no cost awareness, no ingredient graph, subscription-gated |
| **Mealime** | Good meal planning, auto grocery lists | Utilitarian UI, limited recipe variety, no cost tracking |
| **Paprika** | Power-user recipe management | No discovery, no visual feed, no intelligence |
| **Yummly** | Decent recommendations, visual | Shallow intelligence, ad-heavy, no real planning |
| **Whisk/Samsung Food** | Grocery integration, meal planning | Corporate, no soul, weak discovery |
| **Tasty (BuzzFeed)** | Great video content, viral recipes | No planning, no cost, content-only |

### Indirect Competitors

- **Instagram food accounts** — Discovery and inspiration, but no structure
- **TikTok recipes** — Engagement model we want, but ephemeral and unstructured
- **ChatGPT/AI chat** — Can generate recipes on demand, but no persistence, no graph, no visual experience

### Our Differentiation

1. **The graph** — No competitor models meal-ingredient relationships as a queryable graph
2. **Cost-aware planning** — Real price estimates, budget constraints, cost-per-serving
3. **Visual-first + intelligent** — Instagram's engagement model meets actual utility
4. **Offline-generated inventory** — Thousands of meals at launch, not user-generated-content dependent
5. **Seasonal + local** — Time-aware recommendations grounded in real availability

---

## 4. Core Innovation: The Meal Graph

### Graph Schema

```
NODES:
  Meal            — name, description, servings, prep_time, cook_time, total_time,
                    difficulty, cuisine, season[], dietary_tags[], image_url,
                    source_url (grounding), is_verified, popularity_score
  
  Ingredient      — name, category (protein/vegetable/grain/dairy/spice/etc),
                    unit, avg_price_per_unit, season[], shelf_life_days,
                    is_pantry_staple, nutritional_info{}
  
  Cuisine         — name, region, description
  
  Technique       — name, description, difficulty, equipment_needed[]
  
  Season          — name (spring/summer/fall/winter), months[]
  
  DietaryTag      — name (vegan/vegetarian/gluten-free/keto/halal/kosher/etc)
  
  Chef            — name, bio, source, specialty
  
  Equipment       — name, is_common (bool)

EDGES:
  (Meal)-[REQUIRES]->(Ingredient)
      properties: quantity, unit, is_optional, prep_note
  
  (Meal)-[BELONGS_TO]->(Cuisine)
  
  (Meal)-[USES_TECHNIQUE]->(Technique)
  
  (Meal)-[BEST_IN]->(Season)
  
  (Meal)-[TAGGED]->(DietaryTag)
  
  (Meal)-[VARIATION_OF]->(Meal)
      properties: variation_type (simpler/fancier/regional/dietary)
  
  (Meal)-[PAIRS_WITH]->(Meal)
      properties: pairing_type (side_dish/dessert/appetizer)
  
  (Meal)-[CREATED_BY]->(Chef)
  
  (Meal)-[NEEDS]->(Equipment)
  
  (Ingredient)-[SUBSTITUTES]->(Ingredient)
      properties: ratio, flavor_impact (none/mild/significant), notes
  
  (Ingredient)-[CATEGORY_OF]->(IngredientCategory)
  
  (Ingredient)-[IN_SEASON]->(Season)

DERIVED/COMPUTED:
  (Meal)-[SHARES_INGREDIENTS_WITH]->(Meal)
      properties: shared_count, shared_ingredients[], overlap_ratio
  
  (Meal)-[COST_ESTIMATE]
      properties: total_cost, cost_per_serving, price_date, region
```

### Graph Powers

This graph structure enables queries that flat databases cannot:

1. **Ingredient overlap** — "Find meals that share ≥3 ingredients with Meal X" → one graph traversal
2. **Budget-constrained planning** — "Find a set of 5 meals where total unique ingredients cost < $80" → constraint optimization over graph
3. **Waste minimization** — "Given these 5 meals, which ingredients are only used in 1 meal?" → identify waste risk
4. **Substitution chains** — "User is allergic to peanuts → find all substitutes → re-cost the meal"
5. **Seasonal filtering** — "Show me meals where ≥80% of ingredients are in season in June in Ontario"
6. **Technique progression** — "User has mastered sautéing → suggest meals that introduce braising"
7. **Leftover utilization** — "User has leftover rice and chicken → traverse graph for meals using both"

### Graph Database Choice

**Recommended: Neo4j (or Memgraph for performance)**

- Native graph storage and traversal
- Cypher query language maps directly to our traversal patterns
- Strong ecosystem (APOC procedures, GDS for graph algorithms)
- Neo4j Aura for managed hosting, or self-hosted for cost control

**Alternative: PostgreSQL with Apache AGE extension**
- If we want to stay in the relational world for simpler ops
- Graph queries via openCypher on top of Postgres
- Easier for a small team to operate

**For MVP**: Start with PostgreSQL + junction tables. The graph queries we need for MVP (ingredient overlap, basic filtering) can be done with SQL joins. Migrate to Neo4j when traversal complexity demands it.

---

## 5. MVP Definition

### MVP Scope (v0.1)

**In scope:**

1. **Meal Feed** — Instagram-style vertical scroll of meal cards (image, name, time, cost, tags)
2. **Meal Detail** — Full recipe page: ingredients with quantities, step-by-step instructions, total cost estimate, cooking time, serving size
3. **Weekly Planner** — Select meals for each day of the week (drag or tap to add)
4. **Grocery List** — Auto-generated from weekly plan, deduplicated, grouped by store section, with quantities aggregated across meals
5. **Budget Filter** — Set a weekly budget; meals and plans that exceed it are flagged
6. **Basic Filters** — Cuisine, dietary restrictions, cooking time, cost range
7. **Offline meal inventory** — 500-1000 meals generated and grounded before launch

**Out of scope for MVP:**
- Voice-over / video generation
- Chef profiles
- Social features (sharing, comments)
- Local ingredient sourcing
- User-submitted recipes
- Advanced AI suggestions ("you should also make X")
- Nutritional tracking
- Supermarket API integration (use estimated prices)
- User accounts / sync (local-first MVP)

### MVP Success Criteria

- User can browse and discover meals they want to cook
- User can plan a full week in under 5 minutes
- Grocery list is accurate and actionable
- Cost estimates are within 20% of actual supermarket prices
- App feels fast, beautiful, and delightful

---

## 6. System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                    CLIENT (iOS/Android)               │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ Feed View │  │ Meal     │  │ Planner +         │  │
│  │ (scroll)  │  │ Detail   │  │ Grocery List      │  │
│  └──────────┘  └──────────┘  └───────────────────┘  │
│                       │                               │
│              Local Cache / SQLite                     │
└───────────────────────┬─────────────────────────────┘
                        │ API (REST or GraphQL)
┌───────────────────────┴─────────────────────────────┐
│                    BACKEND API                        │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ Feed     │  │ Planner  │  │ Grocery           │  │
│  │ Service  │  │ Service  │  │ Service            │  │
│  └──────────┘  └──────────┘  └───────────────────┘  │
│                       │                               │
│              ┌────────┴────────┐                     │
│              │   Graph Engine  │                     │
│              │   (query layer) │                     │
│              └────────┬────────┘                     │
│                       │                               │
│         ┌─────────────┼─────────────┐                │
│         │             │             │                 │
│    ┌────┴────┐  ┌─────┴────┐  ┌────┴─────┐         │
│    │ Meal DB │  │ Price DB │  │ Image    │          │
│    │ (graph) │  │          │  │ Storage  │          │
│    └─────────┘  └──────────┘  └──────────┘         │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│              OFFLINE PIPELINE (runs pre-launch       │
│              and on schedule)                         │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ Meal     │  │ Grounding│  │ Cost              │  │
│  │ Generator│  │ Verifier │  │ Estimator         │  │
│  │ (LLM)   │  │ (web)    │  │                    │  │
│  └──────────┘  └──────────┘  └───────────────────┘  │
│  ┌──────────┐  ┌──────────┐                         │
│  │ Image    │  │ Graph    │                         │
│  │ Generator│  │ Builder  │                         │
│  └──────────┘  └──────────┘                         │
└─────────────────────────────────────────────────────┘
```

### Tech Stack (Recommended for MVP)

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Mobile Client** | React Native (Expo) or Swift/Kotlin | Expo for speed-to-market; native for polish. Decision depends on team. |
| **Backend API** | Next.js API routes on Vercel | Fast to build, serverless, Ahmed knows the stack |
| **Database** | PostgreSQL (Neon on Vercel Marketplace) | Relational with JSON support, graph queries via joins for MVP |
| **Image Storage** | Vercel Blob or Cloudflare R2 | Cost-effective image hosting |
| **Search** | PostgreSQL full-text search → Algolia later | Start simple, upgrade when needed |
| **Offline Pipeline** | Python scripts + Claude API | Batch generation, grounding, cost estimation |
| **Image Generation** | DALL-E 3 / Flux / Midjourney API | High-quality food photography style |
| **Hosting** | Vercel (API + web) + Expo EAS (mobile) | Familiar stack, low ops burden |

### Alternative: Mobile-First Native

If polish and performance are priorities over speed:
- **iOS**: SwiftUI + SwiftData (local-first)
- **Android**: Jetpack Compose + Room
- **Backend**: Same (Next.js on Vercel)
- **Sync**: Simple REST API for pulling meal data, plans stored locally

---

## 7. Offline Content Generation Pipeline

This is the most critical pre-launch workstream. The app lives or dies on content quality.

### Pipeline Stages

```
Stage 1: GENERATE
  Input:  Cuisine categories, difficulty levels, seasonal constraints
  Process: LLM generates structured meal objects (JSON)
  Output: Raw meal records (name, description, ingredients, steps, metadata)
  Volume: 1000 meals for MVP

Stage 2: GROUND
  Input:  Raw meal records
  Process: Search web for matching real recipes (Google, AllRecipes, Serious Eats)
           Compare generated recipe against real ones
           Flag divergences, adjust quantities, validate feasibility
  Output: Grounded meal records with source_urls and confidence scores
  Rule:   Meals with confidence < 0.7 go to manual review queue

Stage 3: COST
  Input:  Grounded meal records with ingredient lists
  Process: Match ingredients to price database
           Estimate cost per serving, total cost
           Flag outlier costs for review
  Output: Costed meal records
  Source: Initial price DB from grocery store websites (Loblaws, Walmart, Metro for Canada)
          Updated monthly via web scraping or API

Stage 4: IMAGE
  Input:  Costed meal records
  Process: Generate food photography-style images via AI
           Each meal gets 1 hero image (feed card) + 3-5 step images
  Output: Image URLs linked to meal records
  Quality: Must look like professional food photography, not AI-generated
  
Stage 5: GRAPH
  Input:  All costed, imaged meal records
  Process: Build ingredient overlap edges
           Compute substitution relationships
           Assign seasonal tags based on ingredient seasonality
           Cluster meals by cuisine/technique/difficulty
           Calculate similarity scores between all meal pairs
  Output: Complete graph database ready for querying

Stage 6: VALIDATE
  Input:  Complete graph
  Process: Run consistency checks:
           - Every meal has ≥2 ingredients
           - Every ingredient has a price
           - Cost per serving is between $1-30 (flag outliers)
           - Images exist for all meals
           - No orphan nodes
           - Seasonal tags are coherent (no strawberries in winter without note)
  Output: Validation report, flagged records for review
```

### LLM Generation Prompt Strategy

The generation prompts should produce structured JSON:

```json
{
  "name": "Chicken Shawarma Bowl",
  "description": "Spiced chicken thighs over rice with pickled vegetables and garlic sauce",
  "cuisine": "Middle Eastern",
  "difficulty": "medium",
  "prep_time_minutes": 20,
  "cook_time_minutes": 25,
  "total_time_minutes": 45,
  "servings": 4,
  "seasons": ["all"],
  "dietary_tags": ["halal", "gluten-free-adaptable"],
  "ingredients": [
    {"name": "chicken thighs", "quantity": 1.5, "unit": "lb", "is_optional": false, "category": "protein"},
    {"name": "basmati rice", "quantity": 2, "unit": "cup", "is_optional": false, "category": "grain"},
    ...
  ],
  "steps": [
    {"order": 1, "instruction": "Mix shawarma spices: cumin, paprika, turmeric, cinnamon, allspice", "duration_minutes": 5},
    ...
  ],
  "equipment": ["oven", "baking sheet", "rice cooker or pot"],
  "tips": ["Marinate overnight for deeper flavor", "Use a cast iron skillet for crispier chicken"],
  "variations": ["swap chicken for lamb", "make it vegan with roasted cauliflower"],
  "source_inspiration": "Traditional Levantine shawarma"
}
```

### Generation Diversity Strategy

To avoid a homogeneous meal set:

1. **Cuisine matrix** — Generate across 20+ cuisines with quotas (don't over-index on Western)
2. **Difficulty spread** — 30% easy (under 30 min), 40% medium, 20% advanced, 10% project meals
3. **Cost spread** — 25% budget (<$3/serving), 50% moderate ($3-8), 25% premium ($8+)
4. **Meal type coverage** — Breakfast, lunch, dinner, snacks, desserts, sides
5. **Seasonal distribution** — Tag all meals, ensure each season has ≥200 options
6. **Dietary coverage** — Ensure substantial options for vegan, vegetarian, gluten-free, halal, kosher

### Grounding Methodology

Grounding prevents the LLM from hallucinating recipes that don't work:

1. Search for the meal name + key ingredients on 3+ recipe sites
2. Compare ingredient lists — flag if generated recipe is missing a common ingredient or has unusual ratios
3. Compare cooking times — flag if generated time is <50% or >200% of real recipes
4. Validate technique feasibility — does the step sequence make culinary sense?
5. Score confidence: `(ingredient_overlap * 0.4) + (time_similarity * 0.2) + (technique_validity * 0.2) + (source_count * 0.2)`

---

## 8. Cost Estimation Engine

### Price Database

Build an ingredient price database with:

```
ingredient_prices:
  ingredient_id   → FK to ingredient
  region          → "Ontario-CA", "NYC-US", etc.
  store_tier      → "budget" | "mid" | "premium"
  price           → decimal
  unit            → standardized (kg, L, each)
  last_updated    → timestamp
  source          → "loblaws.ca", "walmart.ca", "manual"
```

### Initial Price Seeding

For MVP (Canadian market):
1. Scrape Loblaws/Walmart/Metro online grocery stores for ~300 common ingredients
2. Normalize to standard units (price per kg, price per L, price per each)
3. Store 3 price tiers per ingredient (budget/mid/premium)
4. Update monthly

### Cost Calculation

```
meal_cost = SUM(ingredient.quantity * ingredient.price_per_unit)
cost_per_serving = meal_cost / meal.servings

weekly_plan_cost = SUM(unique_ingredients_across_all_meals * needed_quantity * price)
  // NOT sum of individual meal costs — shared ingredients counted once
```

The distinction between summing meal costs and computing actual grocery cost is critical. If 3 meals use onions, you buy onions once, not three times. The graph makes this calculation natural.

### Budget Constraint Algorithm

Given a weekly budget B and a set of candidate meals:

```
OPTIMIZE:
  Select S meals (S = 5-7 for a week) from candidates
  WHERE grocery_cost(S) <= B
  MAXIMIZE: diversity_score(S) + preference_score(S)
  SUBJECT TO:
    - At least 1 meal per day
    - Dietary constraints met
    - Cooking time constraints met
    - Ingredient waste minimized (penalize single-use ingredients)
```

This is a variant of the knapsack problem. For MVP, a greedy algorithm works:
1. Sort meals by cost-per-serving ascending
2. Pick meals greedily, tracking cumulative unique ingredient cost
3. Prefer meals that share ingredients with already-selected meals
4. Stop when budget or meal count reached

Post-MVP: use proper optimization (constraint programming with OR-Tools, or even LLM-assisted planning).

---

## 9. Meal Planning Algorithm

### Weekly Plan Generation

The planner should balance multiple objectives:

1. **Budget compliance** — Total grocery cost ≤ weekly budget
2. **Variety** — Don't repeat cuisines on consecutive days
3. **Time awareness** — Lighter meals on weekdays, complex ones on weekends
4. **Ingredient efficiency** — Maximize shared ingredients, minimize waste
5. **Nutritional balance** — Rough macronutrient distribution (not calorie counting)
6. **Seasonal fit** — Prefer in-season ingredients
7. **User preferences** — Learned over time (likes, dislikes, history)

### Grocery List Generation

```
1. Collect all (Meal)-[REQUIRES]->(Ingredient) edges for selected meals
2. Group by ingredient
3. Sum quantities (convert units if needed: 2 cups + 500mL → unified)
4. Apply pantry filter (user marks staples they always have: salt, oil, etc.)
5. Group by store section (produce, dairy, meat, pantry, frozen)
6. Sort within sections alphabetically or by store layout
7. Show per-ingredient: total quantity, which meals use it, cost estimate
```

### Suggestion Engine

After user selects initial meals, suggest improvements:

- **"Swap Meal C for Meal D"** — saves $4 because D shares 3 ingredients with your other meals
- **"Add Meal E on Wednesday"** — you're already buying all its ingredients for other meals, so it's essentially free
- **"Consider making Meal F on Sunday"** — it takes 2 hours but produces leftovers for Monday lunch

These suggestions are graph traversals: find meals with high ingredient overlap with the current plan that aren't already selected.

---

## 10. UI/UX Design Principles

### Design Philosophy

- **Food photography first** — Every screen should make you hungry
- **Minimal chrome** — Let the images and content breathe
- **Gestural navigation** — Swipe to add to plan, swipe to dismiss
- **Information hierarchy** — Time and cost visible at a glance, full recipe on tap
- **Dark mode default** — Food looks better on dark backgrounds (restaurant menu principle)

### Key Screens

#### 1. Feed (Home)
- Full-bleed meal cards, vertical scroll
- Each card: hero image, meal name, cooking time, cost per serving, cuisine tag
- Floating filter chips at top (cuisine, time, cost, dietary)
- Tap card → meal detail
- Long press or swipe right → add to weekly plan

#### 2. Meal Detail
- Hero image with parallax scroll
- Quick stats bar: time | cost | servings | difficulty
- Ingredients list (tap to expand with substitutions)
- Step-by-step instructions (checkbox to track progress)
- "Similar meals" carousel at bottom (graph-powered)
- "Add to plan" button

#### 3. Weekly Planner
- 7-day grid view
- Drag and drop meals between days
- Running cost total at top
- Budget bar (fills as you add meals, turns red if over)
- "Suggest meals" button → AI fills remaining slots optimally
- "Generate grocery list" button

#### 4. Grocery List
- Grouped by store section
- Checkboxes for shopping
- Per-item: quantity, cost estimate, which meals need it
- Total cost at bottom
- "I already have" toggle per item (removes from list, remembers for next time)

#### 5. Discover / Explore
- Category grids (by cuisine, by season, by time, by cost)
- "What can I make with..." ingredient search
- Chef spotlights (post-MVP)
- Trending / seasonal highlights

### Visual Identity

- **Typography**: Clean sans-serif for UI, warm serif for recipe titles
- **Color palette**: Warm earth tones (terracotta, olive, cream) with food-photography-inspired accents
- **Photography style**: Overhead flat-lay and 45-degree angle, natural lighting, rustic surfaces, minimal props
- **Motion**: Subtle transitions, smooth scrolling, satisfying micro-interactions

---

## 11. Monetization (Future Consideration)

### Potential Models

1. **Freemium** — Free: browse + 3 meals/week planned. Premium ($5/mo): unlimited planning, advanced suggestions, budget optimization, seasonal collections
2. **Grocery affiliate** — Link to online grocery delivery (Instacart, Walmart) with affiliate commission on ingredient purchases
3. **Sponsored content** — Featured meals from food brands (clearly labeled), ingredient brand partnerships
4. **Premium content** — Chef collaborations, exclusive seasonal collections, video content

### MVP: No monetization. Focus on product-market fit.

---

## 12. Phased Roadmap

### Phase 0: Foundation — Pipeline First (Weeks 1-4)
- [ ] Set up repo, CI/CD, project structure (Next.js on Vercel)
- [ ] Design graph schema and implement in PostgreSQL (Neon)
- [ ] Build offline generation pipeline (Python + Claude API → structured JSON)
- [ ] Build grounding pipeline (web search verification)
- [ ] Build cost estimation pipeline (Canadian grocery prices)
- [ ] Generate first 200 meals, grounded and costed
- [ ] Generate images for all meals (DALL-E 3 or Flux)
- [ ] Build and populate the graph
- [ ] Validate pipeline output quality (cook-test 10 recipes)

### Phase 1: MVP Web App (Weeks 5-10)
- [ ] Meal feed — Instagram-style card grid (Next.js + Vercel)
- [ ] Meal detail page with full recipe
- [ ] Weekly planner (manual selection)
- [ ] Grocery list generation (deduplicated, grouped by section)
- [ ] Basic budget filtering
- [ ] Deploy to Vercel
- [ ] Scale to 500+ meals

### Phase 2: Intelligence (Weeks 11-16)
- [ ] Meal suggestion engine (ingredient overlap, budget optimization)
- [ ] "What can I make with..." ingredient-based search
- [ ] Pantry management (mark what you have)
- [ ] Substitution suggestions
- [ ] Seasonal recommendations
- [ ] Scale to 1000+ meals

### Phase 3: Rich Media (Weeks 17-22)
- [ ] Voice-over for recipe steps (TTS)
- [ ] Short video generation for key techniques
- [ ] Step-by-step photo mode
- [ ] Cooking timer integration

### Phase 4: Social + Community (Weeks 23+)
- [ ] User accounts and sync
- [ ] Save favorites, rate meals
- [ ] Share meal plans
- [ ] User-submitted recipes (with grounding/validation)
- [ ] Chef profiles and curated collections
- [ ] Local ingredient sourcing

### Phase 5: Native Mobile (Parallel or post-web)
- [ ] iOS app (SwiftUI)
- [ ] Android app (Compose)
- [ ] Offline support (download meal data for cooking without internet)
- [ ] Cooking mode (screen stays on, large text, step-by-step)

---

## 13. Data Quality & Grounding Strategy

### Why Grounding Matters

LLM-generated recipes can:
- Hallucinate ingredient combinations that taste bad
- Get proportions wrong (2 cups of salt instead of 2 tsp)
- Suggest impossible techniques (deep fry without oil temp guidance)
- Miss critical safety steps (pork internal temperature)

### Grounding Process

For each generated meal:

1. **Search verification** — Find 2+ real recipes for the same or very similar dish
2. **Ingredient validation** — Compare ingredient lists; flag if our recipe has unusual additions or missing staples
3. **Proportion check** — Validate quantities against real recipes; flag deviations >50%
4. **Technique feasibility** — Ensure step sequence is physically possible and safe
5. **Cultural accuracy** — Verify dish names and descriptions are culturally respectful and accurate
6. **Confidence scoring** — Aggregate checks into a 0-1 confidence score; only publish meals ≥0.7

### Continuous Quality

- User feedback loop: "This recipe didn't work" → flag for review
- A/B test recipe variants (post-MVP)
- Expert chef review for top-performing meals

---

## 14. Decisions Made

1. **Platform**: Web-first (Next.js on Vercel). Native mobile in Phase 5.
2. **Build order**: Pipeline first — generate and validate content before building UI.
3. **Market focus**: Canada-first (Toronto). Prices grounded in Canadian grocers (Loblaws, Walmart, Metro).
4. **Graph database**: PostgreSQL for MVP, migrate to Neo4j when traversal complexity demands it.
5. **Images**: AI-generated for MVP, replace with real photography over time.

## 15. Open Questions (Remaining)

1. **Content licensing** — Can we reference existing recipes as "inspired by" with source links, or do we need fully original content? Need legal review.
2. **Pricing data legality** — Scraping grocery store prices may violate ToS. Need to investigate grocery APIs or manual data collection alternatives.

---

## 15. Verification Plan

Before shipping MVP:

1. **Content quality** — Have 10 people cook 3 random meals each. Success if ≥80% rate the recipe "easy to follow" and "tasted good"
2. **Cost accuracy** — Spot-check 20 meals against actual grocery receipts. Success if ≥80% within 20% of estimate
3. **Graph quality** — Verify ingredient overlap suggestions make culinary sense (not just data matches)
4. **Planning UX** — Time 10 users planning a week. Success if ≤5 minutes average
5. **Grocery list accuracy** — Have 5 users shop from generated lists. Success if no missing items and quantities are right
6. **Performance** — Feed loads in <1s, search results in <500ms, grocery list generation in <2s

---

## Summary

MiseEnPlace's competitive moat is the meal-ingredient graph. No competitor models meals as connected nodes in a rich graph. This graph, populated offline with LLM-generated and web-grounded content, enables cost-optimized weekly planning, zero-waste grocery lists, and intelligent meal suggestions that improve over time.

The MVP is deliberately constrained: a beautiful feed, detailed recipe pages, a weekly planner, and a grocery list. No AI chat, no social features, no videos. Get the core loop right — discover → plan → shop → cook — and the graph powers everything underneath.

Build the graph. Everything else follows.
