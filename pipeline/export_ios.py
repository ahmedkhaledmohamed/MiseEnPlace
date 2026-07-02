"""
Export MiseEnPlace data for the iOS app bundle.

Produces meals.json with all meal data, ingredients, steps, and similarity
relationships in a format that maps directly to the SwiftData models.

Usage:
    python -m export_ios
    python -m export_ios --db output/miseenplace.db --out ../ios/MiseEnPlace/Resources/meals.json
"""

import argparse
import json
import sqlite3
from pathlib import Path

DEFAULT_DB = Path(__file__).parent / "output" / "miseenplace.db"
DEFAULT_OUT = Path(__file__).parent.parent / "ios" / "MiseEnPlace" / "Resources" / "meals.json"


def export(db_path, out_path, images_dir=None):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    meals_raw = [dict(r) for r in conn.execute("SELECT * FROM meals").fetchall()]

    meal_ingredients = {}
    for row in conn.execute("""
        SELECT mi.meal_id, mi.quantity, mi.unit, mi.is_optional, mi.prep_note, mi.cost,
               i.name, i.category
        FROM meal_ingredients mi JOIN ingredients i ON mi.ingredient_id = i.id
        ORDER BY mi.meal_id
    """):
        meal_ingredients.setdefault(row["meal_id"], []).append({
            "name": row["name"],
            "category": row["category"],
            "quantity": row["quantity"],
            "unit": row["unit"],
            "isOptional": bool(row["is_optional"]),
            "prepNote": row["prep_note"],
            "cost": row["cost"],
        })

    steps = {}
    for row in conn.execute("SELECT * FROM meal_steps ORDER BY meal_id, step_order"):
        steps.setdefault(row["meal_id"], []).append({
            "order": row["step_order"],
            "instruction": row["instruction"],
            "duration": row["duration_minutes"],
        })

    seasons = {}
    for row in conn.execute("SELECT meal_id, season FROM meal_seasons"):
        seasons.setdefault(row["meal_id"], []).append(row["season"])

    dietary = {}
    for row in conn.execute("SELECT meal_id, tag FROM meal_dietary_tags"):
        dietary.setdefault(row["meal_id"], []).append(row["tag"])

    equipment = {}
    for row in conn.execute("SELECT meal_id, equipment FROM meal_equipment"):
        equipment.setdefault(row["meal_id"], []).append(row["equipment"])

    tips = {}
    for row in conn.execute("SELECT meal_id, tip FROM meal_tips"):
        tips.setdefault(row["meal_id"], []).append(row["tip"])

    variations = {}
    for row in conn.execute("SELECT meal_id, variation FROM meal_variations"):
        variations.setdefault(row["meal_id"], []).append(row["variation"])

    import hashlib
    images_path = Path(images_dir) if images_dir else Path(__file__).parent / "output" / "images"
    image_base_url = "https://mealgraph.vercel.app/images"

    meals = []
    for m in meals_raw:
        mid = m["id"]
        key = f"{m['name']}:{m['cuisine']}".lower()
        image_id = hashlib.md5(key.encode()).hexdigest()[:12]
        image_url = None
        if (images_path / f"{image_id}.png").exists():
            image_url = f"{image_base_url}/{image_id}.png"

        meals.append({
            "id": f"meal-{mid}",
            "name": m["name"],
            "description": m["description"],
            "cuisine": m["cuisine"],
            "mealType": m["meal_type"],
            "difficulty": m["difficulty"],
            "prepTime": m["prep_time_minutes"],
            "cookTime": m["cook_time_minutes"],
            "totalTime": m["total_time_minutes"],
            "servings": m["servings"],
            "costPerServing": m["cost_per_serving"],
            "totalCost": m["total_cost"],
            "sourceInspiration": m["source_inspiration"],
            "imageUrl": image_url,
            "dietaryTags": dietary.get(mid, []),
            "seasons": seasons.get(mid, []),
            "equipment": equipment.get(mid, []),
            "tips": tips.get(mid, []),
            "variations": variations.get(mid, []),
            "ingredients": meal_ingredients.get(mid, []),
            "steps": steps.get(mid, []),
        })

    similarities = []
    for row in conn.execute("SELECT * FROM meal_similarity"):
        shared = json.loads(row["shared_ingredients"]) if row["shared_ingredients"] else []
        similarities.append({
            "mealAId": f"meal-{row['meal_a_id']}",
            "mealBId": f"meal-{row['meal_b_id']}",
            "sharedCount": row["shared_ingredient_count"],
            "overlapRatio": row["overlap_ratio"],
            "sharedIngredients": shared,
        })

    import random
    random.seed(len(meals) * 7919)
    random.shuffle(meals)

    output = {
        "meals": meals,
        "similarities": similarities,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(output, f)

    size_kb = out_path.stat().st_size / 1024
    print(f"Exported {len(meals)} meals, {len(similarities)} similarities")
    print(f"Output: {out_path} ({size_kb:.0f} KB)")

    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Export MiseEnPlace data for iOS")
    parser.add_argument("--db", type=str, default=str(DEFAULT_DB))
    parser.add_argument("--out", type=str, default=str(DEFAULT_OUT))
    parser.add_argument("--images-dir", type=str, default=None)
    args = parser.parse_args()
    export(Path(args.db), Path(args.out), args.images_dir)


if __name__ == "__main__":
    main()
