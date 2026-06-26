"""
Export the MiseEnPlace graph from SQLite to a JSON file for the web visualizer.

Usage:
    python -m export_graph
    python -m export_graph --db output/miseenplace.db --out ../web/public/graph.json
"""

import argparse
import json
import sqlite3
from pathlib import Path

DEFAULT_DB = Path(__file__).parent / "output" / "miseenplace.db"
DEFAULT_OUT = Path(__file__).parent.parent / "web" / "public" / "graph.json"


def export(db_path, out_path):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    meals = [dict(r) for r in conn.execute("SELECT * FROM meals").fetchall()]
    ingredients = [dict(r) for r in conn.execute("SELECT * FROM ingredients").fetchall()]

    meal_ingredients = conn.execute("""
        SELECT mi.meal_id, mi.ingredient_id, mi.quantity, mi.unit,
               mi.is_optional, mi.prep_note, mi.cost, i.name as ingredient_name, i.category
        FROM meal_ingredients mi
        JOIN ingredients i ON mi.ingredient_id = i.id
    """).fetchall()

    similarities = conn.execute("""
        SELECT meal_a_id, meal_b_id, shared_ingredient_count, overlap_ratio, shared_ingredients
        FROM meal_similarity
    """).fetchall()

    seasons = {}
    for row in conn.execute("SELECT meal_id, season FROM meal_seasons"):
        seasons.setdefault(row["meal_id"], []).append(row["season"])

    dietary = {}
    for row in conn.execute("SELECT meal_id, tag FROM meal_dietary_tags"):
        dietary.setdefault(row["meal_id"], []).append(row["tag"])

    steps = {}
    for row in conn.execute("SELECT meal_id, step_order, instruction, duration_minutes FROM meal_steps ORDER BY meal_id, step_order"):
        steps.setdefault(row["meal_id"], []).append({
            "order": row["step_order"],
            "instruction": row["instruction"],
            "duration": row["duration_minutes"],
        })

    equipment = {}
    for row in conn.execute("SELECT meal_id, equipment FROM meal_equipment"):
        equipment.setdefault(row["meal_id"], []).append(row["equipment"])

    tips = {}
    for row in conn.execute("SELECT meal_id, tip FROM meal_tips"):
        tips.setdefault(row["meal_id"], []).append(row["tip"])

    variations = {}
    for row in conn.execute("SELECT meal_id, variation FROM meal_variations"):
        variations.setdefault(row["meal_id"], []).append(row["variation"])

    meal_ing_map = {}
    for row in meal_ingredients:
        meal_ing_map.setdefault(row["meal_id"], []).append({
            "name": row["ingredient_name"],
            "category": row["category"],
            "quantity": row["quantity"],
            "unit": row["unit"],
            "isOptional": bool(row["is_optional"]),
            "prepNote": row["prep_note"],
            "cost": row["cost"],
        })

    ing_usage = {}
    for row in meal_ingredients:
        ing_usage[row["ingredient_id"]] = ing_usage.get(row["ingredient_id"], 0) + 1

    nodes = []
    for m in meals:
        mid = m["id"]
        ings = meal_ing_map.get(mid, [])
        nodes.append({
            "id": f"meal-{mid}",
            "type": "meal",
            "label": m["name"],
            "cuisine": m["cuisine"],
            "mealType": m["meal_type"],
            "difficulty": m["difficulty"],
            "prepTime": m["prep_time_minutes"],
            "cookTime": m["cook_time_minutes"],
            "totalTime": m["total_time_minutes"],
            "servings": m["servings"],
            "costPerServing": m["cost_per_serving"],
            "totalCost": m["total_cost"],
            "description": m["description"],
            "sourceInspiration": m["source_inspiration"],
            "groundingConfidence": m["grounding_confidence"],
            "dietaryTags": dietary.get(mid, []),
            "seasons": seasons.get(mid, []),
            "ingredients": ings,
            "ingredientCount": len(ings),
            "steps": steps.get(mid, []),
            "equipment": equipment.get(mid, []),
            "tips": tips.get(mid, []),
            "variations": variations.get(mid, []),
        })

    for ing in ingredients:
        nodes.append({
            "id": f"ing-{ing['id']}",
            "type": "ingredient",
            "label": ing["name"],
            "category": ing["category"],
            "isPantryStaple": bool(ing["is_pantry_staple"]),
            "usageCount": ing_usage.get(ing["id"], 0),
        })

    edges = []
    for row in similarities:
        shared = json.loads(row["shared_ingredients"]) if row["shared_ingredients"] else []
        edges.append({
            "source": f"meal-{row['meal_a_id']}",
            "target": f"meal-{row['meal_b_id']}",
            "type": "similarity",
            "sharedCount": row["shared_ingredient_count"],
            "overlapRatio": row["overlap_ratio"],
            "sharedIngredients": shared,
        })

    for row in meal_ingredients:
        edges.append({
            "source": f"meal-{row['meal_id']}",
            "target": f"ing-{row['ingredient_id']}",
            "type": "ingredient",
            "quantity": row["quantity"],
            "unit": row["unit"],
            "cost": row["cost"],
        })

    all_cuisines = sorted(set(m["cuisine"] for m in meals if m["cuisine"]))
    all_types = sorted(set(m["meal_type"] for m in meals if m["meal_type"]))
    all_difficulties = sorted(set(m["difficulty"] for m in meals if m["difficulty"]))
    all_dietary = sorted(set(t for tags in dietary.values() for t in tags))
    all_categories = sorted(set(ing["category"] for ing in ingredients if ing["category"]))

    graph = {
        "nodes": nodes,
        "edges": edges,
        "meta": {
            "cuisines": all_cuisines,
            "mealTypes": all_types,
            "difficulties": all_difficulties,
            "dietaryTags": all_dietary,
            "ingredientCategories": all_categories,
            "mealCount": len(meals),
            "ingredientCount": len(ingredients),
            "similarityPairCount": len(similarities),
        },
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(graph, f)

    size_kb = out_path.stat().st_size / 1024
    print(f"Exported {len(meals)} meals, {len(ingredients)} ingredients, {len(edges)} edges")
    print(f"Output: {out_path} ({size_kb:.0f} KB)")

    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Export MiseEnPlace graph to JSON")
    parser.add_argument("--db", type=str, default=str(DEFAULT_DB))
    parser.add_argument("--out", type=str, default=str(DEFAULT_OUT))
    args = parser.parse_args()
    export(Path(args.db), Path(args.out))


if __name__ == "__main__":
    main()
