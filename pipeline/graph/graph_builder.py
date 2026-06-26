"""
MiseEnPlace Graph Builder — Stage 5 of the offline pipeline.

Takes processed meal records (costed, grounded, imaged) and builds the
meal-ingredient graph in SQLite. This graph is the core data structure
that powers the entire product.

The graph models:
  - Meals and their metadata
  - Ingredients (deduplicated, normalized)
  - Meal→Ingredient edges with quantities
  - Meal↔Meal similarity edges (computed from ingredient overlap)
  - Cuisine, dietary tag, and season associations

Usage:
    python -m graph.graph_builder --input output/costed/costed_batch_20260625.json
    python -m graph.graph_builder --input output/costed/ --all
    python -m graph.graph_builder --input output/meals/sample.json --dry-run
    python -m graph.graph_builder --db output/miseenplace.db --input output/costed/ --all

No API key needed.
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "output"
DEFAULT_DB = OUTPUT_DIR / "miseenplace.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS meals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    cuisine TEXT,
    difficulty TEXT,
    meal_type TEXT,
    prep_time_minutes INTEGER,
    cook_time_minutes INTEGER,
    total_time_minutes INTEGER,
    servings INTEGER,
    total_cost REAL,
    cost_per_serving REAL,
    currency TEXT DEFAULT 'CAD',
    image_id TEXT,
    image_path TEXT,
    grounding_status TEXT,
    grounding_confidence REAL,
    source_inspiration TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT,
    is_pantry_staple INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS meal_ingredients (
    meal_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    quantity REAL,
    unit TEXT,
    is_optional INTEGER DEFAULT 0,
    prep_note TEXT,
    cost REAL,
    PRIMARY KEY (meal_id, ingredient_id),
    FOREIGN KEY (meal_id) REFERENCES meals(id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
);

CREATE TABLE IF NOT EXISTS meal_seasons (
    meal_id INTEGER NOT NULL,
    season TEXT NOT NULL,
    PRIMARY KEY (meal_id, season),
    FOREIGN KEY (meal_id) REFERENCES meals(id)
);

CREATE TABLE IF NOT EXISTS meal_dietary_tags (
    meal_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (meal_id, tag),
    FOREIGN KEY (meal_id) REFERENCES meals(id)
);

CREATE TABLE IF NOT EXISTS meal_steps (
    meal_id INTEGER NOT NULL,
    step_order INTEGER NOT NULL,
    instruction TEXT NOT NULL,
    duration_minutes INTEGER,
    PRIMARY KEY (meal_id, step_order),
    FOREIGN KEY (meal_id) REFERENCES meals(id)
);

CREATE TABLE IF NOT EXISTS meal_equipment (
    meal_id INTEGER NOT NULL,
    equipment TEXT NOT NULL,
    PRIMARY KEY (meal_id, equipment),
    FOREIGN KEY (meal_id) REFERENCES meals(id)
);

CREATE TABLE IF NOT EXISTS meal_tips (
    meal_id INTEGER NOT NULL,
    tip TEXT NOT NULL,
    FOREIGN KEY (meal_id) REFERENCES meals(id)
);

CREATE TABLE IF NOT EXISTS meal_variations (
    meal_id INTEGER NOT NULL,
    variation TEXT NOT NULL,
    FOREIGN KEY (meal_id) REFERENCES meals(id)
);

CREATE TABLE IF NOT EXISTS meal_similarity (
    meal_a_id INTEGER NOT NULL,
    meal_b_id INTEGER NOT NULL,
    shared_ingredient_count INTEGER NOT NULL,
    overlap_ratio REAL NOT NULL,
    shared_ingredients TEXT,
    PRIMARY KEY (meal_a_id, meal_b_id),
    FOREIGN KEY (meal_a_id) REFERENCES meals(id),
    FOREIGN KEY (meal_b_id) REFERENCES meals(id)
);

CREATE INDEX IF NOT EXISTS idx_meal_cuisine ON meals(cuisine);
CREATE INDEX IF NOT EXISTS idx_meal_type ON meals(meal_type);
CREATE INDEX IF NOT EXISTS idx_meal_difficulty ON meals(difficulty);
CREATE INDEX IF NOT EXISTS idx_meal_cost ON meals(cost_per_serving);
CREATE INDEX IF NOT EXISTS idx_meal_time ON meals(total_time_minutes);
CREATE INDEX IF NOT EXISTS idx_ingredient_category ON ingredients(category);
CREATE INDEX IF NOT EXISTS idx_similarity_overlap ON meal_similarity(overlap_ratio DESC);
"""

PANTRY_STAPLES = {
    "salt", "black pepper", "olive oil", "vegetable oil", "water",
    "sugar", "flour", "butter", "garlic",
}


def normalize_ingredient_name(name):
    """Normalize for deduplication."""
    name = name.lower().strip()
    for q in ["fresh ", "dried ", "ground ", "whole ", "large ", "small ",
              "medium ", "organic ", "frozen ", "canned ", "boneless ",
              "skinless ", "bone-in ", "skin-on ", "extra-virgin ", "all-purpose "]:
        name = name.replace(q, "")
    return name.strip()


def init_db(db_path):
    """Initialize the database with schema."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


def insert_meal(conn, meal):
    """Insert a single meal and its relationships into the graph."""
    cost_est = meal.get("cost_estimate", {})
    grounding = meal.get("grounding", {})
    image = meal.get("image", {})

    try:
        cursor = conn.execute("""
            INSERT OR IGNORE INTO meals (
                name, description, cuisine, difficulty, meal_type,
                prep_time_minutes, cook_time_minutes, total_time_minutes,
                servings, total_cost, cost_per_serving, currency,
                image_id, image_path, grounding_status, grounding_confidence,
                source_inspiration
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            meal.get("name"),
            meal.get("description"),
            meal.get("cuisine"),
            meal.get("difficulty"),
            meal.get("meal_type"),
            meal.get("prep_time_minutes"),
            meal.get("cook_time_minutes"),
            meal.get("total_time_minutes"),
            meal.get("servings"),
            cost_est.get("total_cost"),
            cost_est.get("cost_per_serving"),
            cost_est.get("currency", "CAD"),
            image.get("id"),
            image.get("path"),
            grounding.get("status"),
            grounding.get("confidence"),
            meal.get("source_inspiration"),
        ))

        if cursor.rowcount == 0:
            return None

        meal_id = cursor.lastrowid

        for ing in meal.get("ingredients", []):
            normalized = normalize_ingredient_name(ing["name"])
            is_staple = 1 if normalized in PANTRY_STAPLES else 0

            conn.execute(
                "INSERT OR IGNORE INTO ingredients (name, category, is_pantry_staple) VALUES (?, ?, ?)",
                (normalized, ing.get("category"), is_staple),
            )
            ing_row = conn.execute("SELECT id FROM ingredients WHERE name = ?", (normalized,)).fetchone()
            ing_id = ing_row[0]

            ing_cost = None
            for ic in cost_est.get("ingredient_costs", []):
                if normalize_ingredient_name(ic["name"]) == normalized and ic.get("cost") is not None:
                    ing_cost = ic["cost"]
                    break

            conn.execute("""
                INSERT OR IGNORE INTO meal_ingredients (meal_id, ingredient_id, quantity, unit, is_optional, prep_note, cost)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                meal_id, ing_id, ing.get("quantity"), ing.get("unit"),
                1 if ing.get("is_optional") else 0, ing.get("prep_note"), ing_cost,
            ))

        for season in meal.get("seasons", []):
            conn.execute("INSERT OR IGNORE INTO meal_seasons (meal_id, season) VALUES (?, ?)", (meal_id, season))

        for tag in meal.get("dietary_tags", []):
            conn.execute("INSERT OR IGNORE INTO meal_dietary_tags (meal_id, tag) VALUES (?, ?)", (meal_id, tag))

        for step in meal.get("steps", []):
            conn.execute("""
                INSERT OR IGNORE INTO meal_steps (meal_id, step_order, instruction, duration_minutes)
                VALUES (?, ?, ?, ?)
            """, (meal_id, step["order"], step["instruction"], step.get("duration_minutes")))

        for equip in meal.get("equipment", []):
            conn.execute("INSERT OR IGNORE INTO meal_equipment (meal_id, equipment) VALUES (?, ?)", (meal_id, equip))

        for tip in meal.get("tips", []):
            conn.execute("INSERT INTO meal_tips (meal_id, tip) VALUES (?, ?)", (meal_id, tip))

        for var in meal.get("variations", []):
            conn.execute("INSERT INTO meal_variations (meal_id, variation) VALUES (?, ?)", (meal_id, var))

        return meal_id

    except sqlite3.IntegrityError:
        return None


def compute_similarity(conn):
    """Compute ingredient overlap between all meal pairs."""
    conn.execute("DELETE FROM meal_similarity")

    meals = conn.execute("SELECT id, name FROM meals").fetchall()
    meal_ingredients = {}

    for meal_id, name in meals:
        ings = conn.execute(
            "SELECT i.name FROM meal_ingredients mi JOIN ingredients i ON mi.ingredient_id = i.id WHERE mi.meal_id = ? AND mi.is_optional = 0",
            (meal_id,),
        ).fetchall()
        meal_ingredients[meal_id] = set(row[0] for row in ings)

    pairs_inserted = 0
    meal_ids = list(meal_ingredients.keys())

    for i in range(len(meal_ids)):
        for j in range(i + 1, len(meal_ids)):
            a_id, b_id = meal_ids[i], meal_ids[j]
            a_ings, b_ings = meal_ingredients[a_id], meal_ingredients[b_id]

            shared = a_ings & b_ings
            if not shared:
                continue

            union = a_ings | b_ings
            overlap = len(shared) / len(union) if union else 0

            if len(shared) >= 2:
                conn.execute("""
                    INSERT OR REPLACE INTO meal_similarity (meal_a_id, meal_b_id, shared_ingredient_count, overlap_ratio, shared_ingredients)
                    VALUES (?, ?, ?, ?, ?)
                """, (a_id, b_id, len(shared), round(overlap, 3), json.dumps(sorted(shared))))
                pairs_inserted += 1

    conn.commit()
    return pairs_inserted


def load_meals(input_path):
    """Load meals from a batch file or directory."""
    path = Path(input_path)
    meals = []

    if path.is_dir():
        for f in sorted(path.glob("*.json")):
            with open(f) as fh:
                batch = json.load(fh)
                for meal in batch.get("meals", []):
                    meals.append(meal)
    else:
        with open(path) as f:
            batch = json.load(f)
            for meal in batch.get("meals", []):
                meals.append(meal)

    return meals


def build_graph(meals, db_path, dry_run=False):
    """Build the complete meal-ingredient graph."""
    stats = {"total": 0, "inserted": 0, "skipped": 0, "similarity_pairs": 0}

    if dry_run:
        for meal in meals:
            name = meal.get("name", "?")
            ing_count = len(meal.get("ingredients", []))
            print(f"  [DRY RUN] Would insert: {name} ({ing_count} ingredients)")
            stats["total"] += 1
        return stats

    conn = init_db(db_path)

    for i, meal in enumerate(meals):
        name = meal.get("name", f"Meal {i + 1}")
        stats["total"] += 1

        meal_id = insert_meal(conn, meal)
        if meal_id:
            stats["inserted"] += 1
            print(f"  [OK] {name} (id={meal_id})")
        else:
            stats["skipped"] += 1
            print(f"  [SKIP] {name} (already exists)")

    conn.commit()

    print("\nComputing meal similarity...")
    stats["similarity_pairs"] = compute_similarity(conn)
    print(f"  Computed {stats['similarity_pairs']} similarity pairs")

    conn.close()
    return stats


def query_stats(db_path):
    """Print graph statistics."""
    conn = sqlite3.connect(str(db_path))
    meals = conn.execute("SELECT COUNT(*) FROM meals").fetchone()[0]
    ingredients = conn.execute("SELECT COUNT(*) FROM ingredients").fetchone()[0]
    edges = conn.execute("SELECT COUNT(*) FROM meal_ingredients").fetchone()[0]
    similarities = conn.execute("SELECT COUNT(*) FROM meal_similarity").fetchone()[0]
    cuisines = conn.execute("SELECT COUNT(DISTINCT cuisine) FROM meals").fetchone()[0]

    avg_ings = conn.execute("SELECT AVG(cnt) FROM (SELECT COUNT(*) as cnt FROM meal_ingredients GROUP BY meal_id)").fetchone()[0]
    avg_cost = conn.execute("SELECT AVG(cost_per_serving) FROM meals WHERE cost_per_serving IS NOT NULL").fetchone()[0]

    top_shared = conn.execute("""
        SELECT m1.name, m2.name, ms.shared_ingredient_count, ms.overlap_ratio
        FROM meal_similarity ms
        JOIN meals m1 ON ms.meal_a_id = m1.id
        JOIN meals m2 ON ms.meal_b_id = m2.id
        ORDER BY ms.overlap_ratio DESC
        LIMIT 5
    """).fetchall()

    top_ingredients = conn.execute("""
        SELECT i.name, COUNT(*) as meal_count
        FROM meal_ingredients mi
        JOIN ingredients i ON mi.ingredient_id = i.id
        WHERE i.is_pantry_staple = 0
        GROUP BY i.name
        ORDER BY meal_count DESC
        LIMIT 10
    """).fetchall()

    conn.close()

    print(f"\n{'=' * 60}")
    print(f"GRAPH STATISTICS")
    print(f"{'=' * 60}")
    print(f"Meals:              {meals}")
    print(f"Unique ingredients: {ingredients}")
    print(f"Meal→Ingredient:    {edges} edges")
    print(f"Meal↔Meal similar:  {similarities} pairs")
    print(f"Cuisines:           {cuisines}")
    if avg_ings:
        print(f"Avg ingredients:    {avg_ings:.1f} per meal")
    if avg_cost:
        print(f"Avg cost/serving:   ${avg_cost:.2f}")

    if top_ingredients:
        print(f"\nMost used ingredients (non-staple):")
        for name, count in top_ingredients:
            print(f"  {name}: {count} meals")

    if top_shared:
        print(f"\nMost similar meal pairs:")
        for m1, m2, shared, ratio in top_shared:
            print(f"  {m1} ↔ {m2}: {shared} shared ({ratio:.0%} overlap)")

    print(f"{'=' * 60}")


def print_summary(stats):
    print(f"\n{'=' * 50}")
    print(f"GRAPH BUILD SUMMARY")
    print(f"{'=' * 50}")
    print(f"Total meals:       {stats['total']}")
    print(f"  Inserted:        {stats['inserted']}")
    print(f"  Skipped:         {stats['skipped']}")
    print(f"  Similarity pairs:{stats['similarity_pairs']}")
    print(f"{'=' * 50}")


def main():
    parser = argparse.ArgumentParser(description="Build the meal-ingredient graph from processed meals")
    parser.add_argument("--input", type=str, required=True, help="Path to meal batch file or directory")
    parser.add_argument("--all", action="store_true", help="Process all JSON files in directory")
    parser.add_argument("--db", type=str, default=str(DEFAULT_DB), help="Path to SQLite database")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be inserted without building")
    parser.add_argument("--stats", action="store_true", help="Print graph statistics and exit")
    parser.add_argument("--limit", type=int, help="Max number of meals to process")
    args = parser.parse_args()

    db_path = Path(args.db)

    if args.stats:
        if not db_path.exists():
            print(f"Database not found: {db_path}", file=sys.stderr)
            sys.exit(1)
        query_stats(db_path)
        return

    meals = load_meals(args.input)

    if not meals:
        print("No meals found in input", file=sys.stderr)
        sys.exit(1)

    if args.limit:
        meals = meals[:args.limit]

    print(f"Found {len(meals)} meals to insert into graph")
    print(f"Database: {db_path}")

    stats = build_graph(meals, db_path, dry_run=args.dry_run)
    print_summary(stats)

    if not args.dry_run and db_path.exists():
        query_stats(db_path)


if __name__ == "__main__":
    main()
