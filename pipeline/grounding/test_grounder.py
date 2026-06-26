"""Offline tests for the recipe grounder — no API key needed."""

import json
import tempfile
from pathlib import Path

from grounding.recipe_grounder import (
    validate_grounding_result,
    load_meals,
    ground_batch,
)

VALID_RESULT = {
    "ingredient_score": 0.9,
    "ingredient_issues": [],
    "proportion_score": 0.85,
    "proportion_issues": [],
    "technique_score": 0.95,
    "technique_issues": [],
    "time_score": 0.8,
    "time_issues": ["Prep time slightly underestimated"],
    "safety_score": 1.0,
    "safety_issues": [],
    "cultural_score": 0.9,
    "cultural_issues": [],
    "real_world_references": ["Serious Eats Chicken Shawarma", "NYT Cooking Shawarma"],
    "suggested_fixes": [],
    "overall_confidence": 0.9,
    "verdict": "pass",
}

SAMPLE_BATCH = {
    "generated_at": "2026-06-25T00:00:00Z",
    "count": 2,
    "meals": [
        {
            "name": "Test Meal A",
            "cuisine": "Italian",
            "ingredients": [
                {"name": "pasta", "quantity": 400, "unit": "g", "category": "grain"},
                {"name": "olive oil", "quantity": 2, "unit": "tbsp", "category": "oil-fat"},
            ],
        },
        {
            "name": "Test Meal B",
            "cuisine": "Japanese",
            "ingredients": [
                {"name": "rice", "quantity": 2, "unit": "cup", "category": "grain"},
                {"name": "soy sauce", "quantity": 3, "unit": "tbsp", "category": "sauce-condiment"},
            ],
        },
    ],
}


def test_valid_grounding_result():
    valid, error = validate_grounding_result(VALID_RESULT)
    assert valid, f"Valid result failed: {error}"
    print("[PASS] Valid grounding result passes validation")


def test_missing_field():
    result = {k: v for k, v in VALID_RESULT.items() if k != "overall_confidence"}
    valid, error = validate_grounding_result(result)
    assert not valid
    assert "Missing field" in error
    print("[PASS] Missing field correctly rejected")


def test_invalid_score_range():
    result = {**VALID_RESULT, "ingredient_score": 1.5}
    valid, error = validate_grounding_result(result)
    assert not valid
    assert "ingredient_score" in error
    print("[PASS] Out-of-range score correctly rejected")


def test_invalid_verdict():
    result = {**VALID_RESULT, "verdict": "maybe"}
    valid, error = validate_grounding_result(result)
    assert not valid
    assert "Invalid verdict" in error
    print("[PASS] Invalid verdict correctly rejected")


def test_load_meals_from_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(SAMPLE_BATCH, f)
        f.flush()
        meals = load_meals(f.name)
    assert len(meals) == 2
    assert meals[0][1]["name"] == "Test Meal A"
    assert meals[1][1]["name"] == "Test Meal B"
    Path(f.name).unlink()
    print("[PASS] Load meals from file works correctly")


def test_load_meals_from_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "batch1.json"
        with open(path, "w") as f:
            json.dump(SAMPLE_BATCH, f)
        meals = load_meals(tmpdir)
    assert len(meals) == 2
    print("[PASS] Load meals from directory works correctly")


def test_dry_run():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(SAMPLE_BATCH, f)
        f.flush()
        meals = load_meals(f.name)

    results, stats = ground_batch(None, meals, dry_run=True)
    assert len(results) == 2
    assert results[0]["grounding"]["status"] == "dry_run"
    assert results[1]["grounding"]["status"] == "dry_run"
    Path(f.name).unlink()
    print("[PASS] Dry run mode works correctly")


if __name__ == "__main__":
    test_valid_grounding_result()
    test_missing_field()
    test_invalid_score_range()
    test_invalid_verdict()
    test_load_meals_from_file()
    test_load_meals_from_directory()
    test_dry_run()
    print(f"\nAll tests passed")
