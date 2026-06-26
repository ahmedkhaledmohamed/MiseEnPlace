"""
MiseEnPlace Cost Estimator — Stage 3 of the offline pipeline.

Takes grounded (or raw) meal records and estimates cost per meal and
cost per serving using the ingredient price database.

Usage:
    python -m pricing.cost_estimator --input output/grounded/grounded_batch_20260625.json
    python -m pricing.cost_estimator --input output/meals/italian_dinner_20260625.json
    python -m pricing.cost_estimator --input output/grounded/ --all
    python -m pricing.cost_estimator --input output/meals/sample.json --dry-run

No API key needed — uses local price database.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PRICE_DB_PATH = Path(__file__).parent / "price_db.json"
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "costed"

UNIT_CONVERSIONS = {
    ("g", "kg"): 0.001,
    ("kg", "g"): 1000,
    ("ml", "L"): 0.001,
    ("L", "ml"): 1000,
    ("oz", "kg"): 0.02835,
    ("lb", "kg"): 0.4536,
    ("cup", "L"): 0.237,
    ("cup", "kg"): 0.237,
    ("tbsp", "L"): 0.0148,
    ("tbsp", "kg"): 0.0148,
    ("tsp", "L"): 0.00493,
    ("tsp", "kg"): 0.00493,
    ("pinch", "kg"): 0.0003,
    ("pinch", "L"): 0.0003,
    ("slice", "each"): 1,
    ("clove", "clove"): 1,
    ("bunch", "bunch"): 1,
    ("each", "each"): 1,
}


def load_price_db():
    with open(PRICE_DB_PATH) as f:
        db = json.load(f)
    return db["ingredients"], db["_meta"]


def normalize_ingredient_name(name):
    """Normalize ingredient name for fuzzy matching against price DB."""
    name = name.lower().strip()
    # Remove common qualifiers
    for qualifier in [
        "fresh ", "dried ", "ground ", "whole ", "large ", "small ",
        "medium ", "organic ", "frozen ", "canned ", "boneless ",
        "skinless ", "bone-in ", "skin-on ", "extra-virgin ",
        "all-purpose ", "granulated ",
    ]:
        name = name.replace(qualifier, "")
    return name.strip()


def find_price(ingredient_name, prices):
    """Find the best price match for an ingredient."""
    normalized = normalize_ingredient_name(ingredient_name)

    if normalized in prices:
        return prices[normalized], normalized

    for db_name in prices:
        if normalized in db_name or db_name in normalized:
            return prices[db_name], db_name

    return None, None


def convert_quantity(quantity, from_unit, to_unit):
    """Convert ingredient quantity to price DB unit."""
    if from_unit == to_unit:
        return quantity

    if from_unit == "to taste":
        return 0.001

    key = (from_unit, to_unit)
    if key in UNIT_CONVERSIONS:
        return quantity * UNIT_CONVERSIONS[key]

    return None


def estimate_ingredient_cost(ingredient, prices):
    """Estimate cost for a single ingredient."""
    name = ingredient["name"]
    quantity = ingredient["quantity"]
    unit = ingredient["unit"]

    price_entry, matched_name = find_price(name, prices)

    if price_entry is None:
        return {
            "name": name,
            "matched": False,
            "cost": None,
            "note": "No price found in database",
        }

    db_unit = price_entry["unit"]
    db_price = price_entry["price"]

    converted_qty = convert_quantity(quantity, unit, db_unit)

    if converted_qty is None:
        return {
            "name": name,
            "matched": True,
            "matched_as": matched_name,
            "cost": None,
            "note": f"Cannot convert {unit} to {db_unit}",
        }

    cost = round(converted_qty * db_price, 2)

    return {
        "name": name,
        "matched": True,
        "matched_as": matched_name,
        "quantity": quantity,
        "unit": unit,
        "converted_quantity": round(converted_qty, 4),
        "price_unit": db_unit,
        "unit_price": db_price,
        "cost": cost,
    }


def estimate_meal_cost(meal, prices):
    """Estimate total cost and cost per serving for a meal."""
    ingredients = meal.get("ingredients", [])
    servings = meal.get("servings", 4)

    ingredient_costs = []
    total_cost = 0.0
    unmatched = []
    unconvertible = []

    for ing in ingredients:
        result = estimate_ingredient_cost(ing, prices)
        ingredient_costs.append(result)

        if not result["matched"]:
            unmatched.append(result["name"])
        elif result["cost"] is None:
            unconvertible.append(result["name"])
        else:
            total_cost += result["cost"]

    cost_per_serving = round(total_cost / servings, 2) if servings > 0 else 0

    coverage = len([c for c in ingredient_costs if c.get("cost") is not None])
    total_ingredients = len(ingredient_costs)
    coverage_pct = round(coverage / total_ingredients * 100) if total_ingredients > 0 else 0

    return {
        "total_cost": round(total_cost, 2),
        "cost_per_serving": cost_per_serving,
        "servings": servings,
        "currency": "CAD",
        "ingredient_costs": ingredient_costs,
        "coverage": {
            "matched": coverage,
            "total": total_ingredients,
            "percentage": coverage_pct,
        },
        "unmatched_ingredients": unmatched,
        "unconvertible_ingredients": unconvertible,
    }


def load_meals(input_path):
    """Load meals from a batch file (raw or grounded) or directory."""
    path = Path(input_path)
    meals = []

    if path.is_dir():
        for f in sorted(path.glob("*.json")):
            with open(f) as fh:
                batch = json.load(fh)
                for meal in batch.get("meals", []):
                    meals.append((f.name, meal))
    else:
        with open(path) as f:
            batch = json.load(f)
            for meal in batch.get("meals", []):
                meals.append((path.name, meal))

    return meals


def cost_batch(meals, prices, dry_run=False):
    """Estimate costs for a batch of meals."""
    results = []
    stats = {"total": 0, "fully_costed": 0, "partial": 0, "failed": 0}

    for i, (source_file, meal) in enumerate(meals):
        name = meal.get("name", f"Meal {i + 1}")
        print(f"\n[{i + 1}/{len(meals)}] Costing: {name}")

        if dry_run:
            print(f"  [DRY RUN] Would estimate cost from {len(meal.get('ingredients', []))} ingredients")
            results.append({**meal, "cost_estimate": {"status": "dry_run"}})
            stats["total"] += 1
            continue

        cost_data = estimate_meal_cost(meal, prices)
        stats["total"] += 1

        coverage_pct = cost_data["coverage"]["percentage"]
        if coverage_pct == 100:
            stats["fully_costed"] += 1
            icon = "OK"
        elif coverage_pct >= 70:
            stats["partial"] += 1
            icon = "PARTIAL"
        else:
            stats["failed"] += 1
            icon = "LOW"

        print(f"  [{icon}] ${cost_data['total_cost']:.2f} total, ${cost_data['cost_per_serving']:.2f}/serving ({coverage_pct}% coverage)")

        if cost_data["unmatched_ingredients"]:
            print(f"    Unmatched: {', '.join(cost_data['unmatched_ingredients'])}")

        costed_meal = {**meal, "cost_estimate": cost_data}
        results.append(costed_meal)

    return results, stats


def save_results(results, stats, label):
    """Save costed results to output directory."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"costed_{label}_{timestamp}.json"
    path = OUTPUT_DIR / filename

    output = {
        "costed_at": datetime.now(timezone.utc).isoformat(),
        "region": "Ontario-CA",
        "currency": "CAD",
        "total": len(results),
        "stats": stats,
        "meals": results,
    }

    with open(path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved {len(results)} costed meals to {path}")
    return path


def print_summary(stats):
    """Print a summary of costing results."""
    print(f"\n{'=' * 50}")
    print(f"COST ESTIMATION SUMMARY")
    print(f"{'=' * 50}")
    print(f"Total meals:     {stats['total']}")
    print(f"  Fully costed:  {stats['fully_costed']}")
    print(f"  Partial (70%+):{stats['partial']}")
    print(f"  Low coverage:  {stats['failed']}")
    rate = (stats["fully_costed"] / stats["total"] * 100) if stats["total"] > 0 else 0
    print(f"  Full coverage: {rate:.0f}%")
    print(f"{'=' * 50}")


def main():
    parser = argparse.ArgumentParser(description="Estimate meal costs from ingredient price database")
    parser.add_argument("--input", type=str, required=True, help="Path to meal batch file or directory")
    parser.add_argument("--all", action="store_true", help="Process all JSON files in directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be processed without costing")
    parser.add_argument("--limit", type=int, help="Max number of meals to process")
    args = parser.parse_args()

    prices, meta = load_price_db()
    print(f"Loaded price DB: {len(prices)} ingredients ({meta['region']}, updated {meta['last_updated']})")

    meals = load_meals(args.input)

    if not meals:
        print("No meals found in input", file=sys.stderr)
        sys.exit(1)

    if args.limit:
        meals = meals[:args.limit]

    print(f"Found {len(meals)} meals to cost")

    results, stats = cost_batch(meals, prices, dry_run=args.dry_run)

    label = Path(args.input).stem if not Path(args.input).is_dir() else "batch"
    save_results(results, stats, label)
    print_summary(stats)


if __name__ == "__main__":
    main()
