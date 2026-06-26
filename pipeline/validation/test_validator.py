"""Offline tests for the validator — builds a test graph and validates it."""

import json
import sqlite3
import tempfile
from pathlib import Path

from graph.graph_builder import init_db, insert_meal, compute_similarity
from validation.validator import (
    run_validation,
    check_minimum_ingredients,
    check_cost_coverage,
    check_cost_range,
    check_orphan_ingredients,
    check_unique_names,
    check_steps_integrity,
    check_similarity_connectivity,
    check_distribution,
    ValidationResult,
)

GOOD_MEAL_A = {
    "name": "Chicken Shawarma Bowl",
    "description": "Spiced chicken over rice",
    "cuisine": "Middle Eastern",
    "difficulty": "medium",
    "meal_type": "dinner",
    "prep_time_minutes": 20,
    "cook_time_minutes": 25,
    "total_time_minutes": 45,
    "servings": 4,
    "seasons": ["all"],
    "dietary_tags": ["halal"],
    "ingredients": [
        {"name": "chicken thighs", "quantity": 680, "unit": "g", "category": "protein"},
        {"name": "basmati rice", "quantity": 2, "unit": "cup", "category": "grain"},
        {"name": "cumin", "quantity": 1, "unit": "tsp", "category": "spice"},
        {"name": "olive oil", "quantity": 2, "unit": "tbsp", "category": "oil-fat"},
        {"name": "garlic", "quantity": 4, "unit": "clove", "category": "vegetable"},
    ],
    "steps": [
        {"order": 1, "instruction": "Mix spices", "duration_minutes": 3},
        {"order": 2, "instruction": "Cook chicken", "duration_minutes": 12},
        {"order": 3, "instruction": "Serve over rice", "duration_minutes": 2},
    ],
    "equipment": ["skillet"],
    "tips": ["Marinate overnight"],
    "variations": ["Use lamb"],
    "source_inspiration": "Levantine",
    "cost_estimate": {"total_cost": 11.65, "cost_per_serving": 2.91, "currency": "CAD", "ingredient_costs": []},
    "grounding": {"status": "pass", "confidence": 0.9},
}

GOOD_MEAL_B = {
    "name": "Chicken Biryani",
    "description": "Layered rice and chicken",
    "cuisine": "Indian",
    "difficulty": "advanced",
    "meal_type": "dinner",
    "prep_time_minutes": 30,
    "cook_time_minutes": 45,
    "total_time_minutes": 75,
    "servings": 6,
    "seasons": ["all"],
    "dietary_tags": ["halal"],
    "ingredients": [
        {"name": "chicken thighs", "quantity": 900, "unit": "g", "category": "protein"},
        {"name": "basmati rice", "quantity": 3, "unit": "cup", "category": "grain"},
        {"name": "cumin", "quantity": 2, "unit": "tsp", "category": "spice"},
        {"name": "yogurt", "quantity": 1, "unit": "cup", "category": "dairy"},
        {"name": "onion", "quantity": 3, "unit": "each", "category": "vegetable"},
        {"name": "garlic", "quantity": 6, "unit": "clove", "category": "vegetable"},
    ],
    "steps": [
        {"order": 1, "instruction": "Marinate chicken", "duration_minutes": 30},
        {"order": 2, "instruction": "Layer and cook", "duration_minutes": 45},
    ],
    "equipment": ["large pot"],
    "tips": ["Use saffron"],
    "variations": ["Vegetable version"],
    "source_inspiration": "Hyderabadi",
    "cost_estimate": {"total_cost": 18.50, "cost_per_serving": 3.08, "currency": "CAD", "ingredient_costs": []},
    "grounding": {"status": "pass", "confidence": 0.85},
}

GOOD_MEAL_C = {
    "name": "Margherita Pizza",
    "description": "Classic Italian pizza",
    "cuisine": "Italian",
    "difficulty": "easy",
    "meal_type": "lunch",
    "prep_time_minutes": 20,
    "cook_time_minutes": 15,
    "total_time_minutes": 35,
    "servings": 4,
    "seasons": ["all"],
    "dietary_tags": ["vegetarian"],
    "ingredients": [
        {"name": "flour", "quantity": 500, "unit": "g", "category": "grain"},
        {"name": "mozzarella", "quantity": 250, "unit": "g", "category": "dairy"},
        {"name": "tomato sauce", "quantity": 200, "unit": "ml", "category": "sauce-condiment"},
        {"name": "basil", "quantity": 1, "unit": "bunch", "category": "herb"},
    ],
    "steps": [
        {"order": 1, "instruction": "Make dough", "duration_minutes": 10},
        {"order": 2, "instruction": "Top and bake", "duration_minutes": 15},
    ],
    "equipment": ["oven"],
    "tips": ["Use 00 flour"],
    "variations": ["Add prosciutto"],
    "source_inspiration": "Neapolitan",
    "cost_estimate": {"total_cost": 7.20, "cost_per_serving": 1.80, "currency": "CAD", "ingredient_costs": []},
    "grounding": {"status": "pass", "confidence": 0.95},
}


def _build_test_db(meals):
    f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    f.close()
    db_path = Path(f.name)
    conn = init_db(db_path)
    for meal in meals:
        insert_meal(conn, meal)
    conn.commit()
    compute_similarity(conn)
    conn.close()
    return db_path


def test_all_pass_on_good_data():
    db_path = _build_test_db([GOOD_MEAL_A, GOOD_MEAL_B, GOOD_MEAL_C])
    results = run_validation(db_path)

    failures = [r for r in results if r.status == "fail"]
    for f in failures:
        print(f"  UNEXPECTED FAIL: {f.name} — {f.message}")

    assert len(failures) == 0, f"{len(failures)} unexpected failures"
    db_path.unlink()
    print("[PASS] All checks pass on good data")


def test_minimum_ingredients_fail():
    bad_meal = {**GOOD_MEAL_A, "name": "Empty Meal", "ingredients": [
        {"name": "salt", "quantity": 1, "unit": "pinch", "category": "spice"},
    ]}
    db_path = _build_test_db([bad_meal])
    conn = sqlite3.connect(str(db_path))
    result = check_minimum_ingredients(conn)
    conn.close()
    assert result.status == "fail"
    db_path.unlink()
    print("[PASS] Minimum ingredients check catches meals with <2 ingredients")


def test_cost_range_warn():
    expensive = {**GOOD_MEAL_A, "name": "Expensive Meal",
                 "cost_estimate": {"total_cost": 200, "cost_per_serving": 50, "currency": "CAD", "ingredient_costs": []}}
    db_path = _build_test_db([expensive])
    conn = sqlite3.connect(str(db_path))
    result = check_cost_range(conn)
    conn.close()
    assert result.status == "warn"
    db_path.unlink()
    print("[PASS] Cost range check warns on $50/serving meal")


def test_unique_names():
    db_path = _build_test_db([GOOD_MEAL_A, GOOD_MEAL_B])
    conn = sqlite3.connect(str(db_path))
    result = check_unique_names(conn)
    conn.close()
    assert result.status == "pass"
    db_path.unlink()
    print("[PASS] Unique names check passes on unique meals")


def test_steps_integrity():
    db_path = _build_test_db([GOOD_MEAL_A])
    conn = sqlite3.connect(str(db_path))
    result = check_steps_integrity(conn)
    conn.close()
    assert result.status == "pass"
    db_path.unlink()
    print("[PASS] Steps integrity check passes on sequential steps")


def test_similarity_connectivity():
    db_path = _build_test_db([GOOD_MEAL_A, GOOD_MEAL_B, GOOD_MEAL_C])
    conn = sqlite3.connect(str(db_path))
    result = check_similarity_connectivity(conn)
    conn.close()
    assert result.status in ("pass", "warn")
    assert "pairs" in result.details[0]
    db_path.unlink()
    print(f"[PASS] Similarity connectivity: {result.message}")


def test_distribution():
    db_path = _build_test_db([GOOD_MEAL_A, GOOD_MEAL_B, GOOD_MEAL_C])
    conn = sqlite3.connect(str(db_path))
    result = check_distribution(conn)
    conn.close()
    assert result.status == "pass"
    db_path.unlink()
    print(f"[PASS] Distribution check: {result.message}")


def test_validation_result_to_dict():
    r = ValidationResult("test", "pass", "all good", ["detail1"])
    d = r.to_dict()
    assert d["name"] == "test"
    assert d["status"] == "pass"
    assert d["details"] == ["detail1"]
    print("[PASS] ValidationResult serializes to dict")


def test_json_output():
    db_path = _build_test_db([GOOD_MEAL_A, GOOD_MEAL_B])
    results = run_validation(db_path)
    output = {
        "checks": [r.to_dict() for r in results],
        "summary": {
            "pass": sum(1 for r in results if r.status == "pass"),
            "warn": sum(1 for r in results if r.status == "warn"),
            "fail": sum(1 for r in results if r.status == "fail"),
        },
    }
    json_str = json.dumps(output)
    parsed = json.loads(json_str)
    assert "checks" in parsed
    assert "summary" in parsed
    db_path.unlink()
    print("[PASS] JSON output serializes correctly")


if __name__ == "__main__":
    test_validation_result_to_dict()
    test_all_pass_on_good_data()
    test_minimum_ingredients_fail()
    test_cost_range_warn()
    test_unique_names()
    test_steps_integrity()
    test_similarity_connectivity()
    test_distribution()
    test_json_output()
    print(f"\nAll tests passed")
