"""Offline tests for the cost estimator — no API key needed."""

import json
import tempfile
from pathlib import Path

from pricing.cost_estimator import (
    load_price_db,
    normalize_ingredient_name,
    find_price,
    convert_quantity,
    estimate_ingredient_cost,
    estimate_meal_cost,
    load_meals,
    cost_batch,
)

SAMPLE_MEAL = {
    "name": "Chicken Shawarma Bowl",
    "servings": 4,
    "ingredients": [
        {"name": "chicken thighs", "quantity": 680, "unit": "g", "category": "protein"},
        {"name": "basmati rice", "quantity": 2, "unit": "cup", "category": "grain"},
        {"name": "cumin", "quantity": 1, "unit": "tsp", "category": "spice"},
        {"name": "paprika", "quantity": 1, "unit": "tsp", "category": "spice"},
        {"name": "turmeric", "quantity": 0.5, "unit": "tsp", "category": "spice"},
        {"name": "olive oil", "quantity": 2, "unit": "tbsp", "category": "oil-fat"},
        {"name": "lemon", "quantity": 1, "unit": "each", "category": "fruit"},
        {"name": "garlic", "quantity": 4, "unit": "clove", "category": "vegetable"},
    ],
}


def test_price_db_loads():
    prices, meta = load_price_db()
    assert len(prices) > 50
    assert meta["region"] == "Ontario-CA"
    assert meta["currency"] == "CAD"
    print(f"[PASS] Price DB loads: {len(prices)} ingredients")


def test_normalize_ingredient():
    assert normalize_ingredient_name("Fresh Basil") == "basil"
    assert normalize_ingredient_name("Boneless Skinless Chicken Breast") == "chicken breast"
    assert normalize_ingredient_name("Extra-Virgin Olive Oil") == "olive oil"
    assert normalize_ingredient_name("  garlic  ") == "garlic"
    print("[PASS] Ingredient name normalization works")


def test_find_price_exact():
    prices, _ = load_price_db()
    entry, matched = find_price("chicken thighs", prices)
    assert entry is not None
    assert entry["unit"] == "kg"
    assert entry["price"] > 0
    print(f"[PASS] Exact match: chicken thighs @ ${entry['price']}/kg")


def test_find_price_fuzzy():
    prices, _ = load_price_db()
    entry, matched = find_price("fresh basil leaves", prices)
    assert entry is not None
    assert matched == "basil"
    print(f"[PASS] Fuzzy match: 'fresh basil leaves' → '{matched}'")


def test_find_price_not_found():
    prices, _ = load_price_db()
    entry, matched = find_price("dragon fruit caviar", prices)
    assert entry is None
    print("[PASS] Unknown ingredient returns None")


def test_unit_conversion():
    assert convert_quantity(500, "g", "kg") == 0.5
    assert convert_quantity(2, "lb", "kg") - 0.9072 < 0.001
    assert convert_quantity(1, "cup", "L") == 0.237
    assert convert_quantity(1, "tsp", "kg") - 0.00493 < 0.0001
    assert convert_quantity(1, "each", "each") == 1
    print("[PASS] Unit conversions are correct")


def test_estimate_ingredient_cost():
    prices, _ = load_price_db()
    result = estimate_ingredient_cost(
        {"name": "chicken thighs", "quantity": 680, "unit": "g", "category": "protein"},
        prices,
    )
    assert result["matched"]
    assert result["cost"] > 0
    # 680g = 0.68kg * $11/kg = $7.48
    assert abs(result["cost"] - 7.48) < 0.01
    print(f"[PASS] Chicken thighs 680g = ${result['cost']:.2f}")


def test_estimate_meal_cost():
    prices, _ = load_price_db()
    result = estimate_meal_cost(SAMPLE_MEAL, prices)
    assert result["total_cost"] > 0
    assert result["cost_per_serving"] > 0
    assert result["coverage"]["percentage"] == 100
    assert result["currency"] == "CAD"
    assert len(result["unmatched_ingredients"]) == 0
    print(f"[PASS] Shawarma bowl: ${result['total_cost']:.2f} total, ${result['cost_per_serving']:.2f}/serving")


def test_meal_with_unmatched():
    prices, _ = load_price_db()
    meal = {
        "name": "Exotic Dish",
        "servings": 2,
        "ingredients": [
            {"name": "rice", "quantity": 1, "unit": "cup", "category": "grain"},
            {"name": "zzz exotic spice", "quantity": 1, "unit": "tbsp", "category": "other"},
        ],
    }
    result = estimate_meal_cost(meal, prices)
    assert len(result["unmatched_ingredients"]) == 1
    assert "zzz exotic spice" in result["unmatched_ingredients"]
    assert result["coverage"]["percentage"] == 50
    print("[PASS] Unmatched ingredients correctly flagged")


def test_dry_run():
    batch = {"meals": [SAMPLE_MEAL]}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(batch, f)
        f.flush()
        meals = load_meals(f.name)

    results, stats = cost_batch(meals, {}, dry_run=True)
    assert len(results) == 1
    assert results[0]["cost_estimate"]["status"] == "dry_run"
    Path(f.name).unlink()
    print("[PASS] Dry run mode works correctly")


def test_to_taste_handling():
    prices, _ = load_price_db()
    result = estimate_ingredient_cost(
        {"name": "salt", "quantity": 1, "unit": "to taste", "category": "spice"},
        prices,
    )
    assert result["matched"]
    assert result["cost"] is not None
    assert result["cost"] < 0.01
    print(f"[PASS] 'to taste' handled correctly: ${result['cost']:.4f}")


if __name__ == "__main__":
    test_price_db_loads()
    test_normalize_ingredient()
    test_find_price_exact()
    test_find_price_fuzzy()
    test_find_price_not_found()
    test_unit_conversion()
    test_estimate_ingredient_cost()
    test_estimate_meal_cost()
    test_meal_with_unmatched()
    test_dry_run()
    test_to_taste_handling()
    print(f"\nAll tests passed")
