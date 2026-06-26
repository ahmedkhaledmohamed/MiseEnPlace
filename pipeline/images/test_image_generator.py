"""Offline tests for the image generator — no API key needed."""

import json
import tempfile
from pathlib import Path

from images.image_generator import (
    build_image_prompt,
    meal_id,
    load_meals,
    generate_batch,
    CUISINE_STYLING,
)

SAMPLE_MEAL = {
    "name": "Chicken Shawarma Bowl",
    "description": "Spiced chicken thighs over basmati rice with pickled vegetables and garlic sauce",
    "cuisine": "Middle Eastern",
    "difficulty": "medium",
    "meal_type": "dinner",
    "ingredients": [
        {"name": "chicken thighs", "quantity": 680, "unit": "g", "is_optional": False, "category": "protein"},
        {"name": "basmati rice", "quantity": 2, "unit": "cup", "is_optional": False, "category": "grain"},
        {"name": "cumin", "quantity": 1, "unit": "tsp", "is_optional": False, "category": "spice"},
        {"name": "olive oil", "quantity": 2, "unit": "tbsp", "is_optional": False, "category": "oil-fat"},
        {"name": "lemon", "quantity": 1, "unit": "each", "is_optional": False, "category": "fruit"},
        {"name": "pickled turnips", "quantity": 100, "unit": "g", "is_optional": True, "category": "vegetable"},
    ],
}


def test_build_prompt_includes_name():
    prompt = build_image_prompt(SAMPLE_MEAL)
    assert "Chicken Shawarma Bowl" in prompt
    print("[PASS] Prompt includes meal name")


def test_build_prompt_includes_styling():
    prompt = build_image_prompt(SAMPLE_MEAL)
    assert "rustic wooden board" in prompt
    print("[PASS] Prompt includes cuisine-specific styling")


def test_build_prompt_includes_ingredients():
    prompt = build_image_prompt(SAMPLE_MEAL)
    assert "chicken thighs" in prompt
    assert "basmati rice" in prompt
    # Spices and oils should be excluded from visible ingredients
    assert "cumin" not in prompt.split("Key visible ingredients")[1].split(".")[0]
    print("[PASS] Prompt includes key ingredients, excludes spices/oils")


def test_build_prompt_excludes_optional():
    prompt = build_image_prompt(SAMPLE_MEAL)
    assert "pickled turnips" not in prompt.split("Key visible ingredients")[1].split(".")[0]
    print("[PASS] Optional ingredients excluded from prompt")


def test_build_prompt_no_text_watermark():
    prompt = build_image_prompt(SAMPLE_MEAL)
    assert "No text" in prompt
    assert "no watermarks" in prompt
    print("[PASS] Prompt includes no-text/no-watermark instructions")


def test_build_prompt_unknown_cuisine():
    meal = {**SAMPLE_MEAL, "cuisine": "Atlantean"}
    prompt = build_image_prompt(meal)
    assert "ceramic plate" in prompt
    print("[PASS] Unknown cuisine falls back to default styling")


def test_all_cuisines_have_styling():
    expected_cuisines = [
        "Middle Eastern", "Mediterranean", "Italian", "Japanese",
        "Indian", "Mexican", "Korean", "Chinese", "Thai", "French",
    ]
    for cuisine in expected_cuisines:
        assert cuisine in CUISINE_STYLING, f"Missing styling for {cuisine}"
    print(f"[PASS] All {len(CUISINE_STYLING)} cuisines have styling")


def test_meal_id_stable():
    id1 = meal_id(SAMPLE_MEAL)
    id2 = meal_id(SAMPLE_MEAL)
    assert id1 == id2
    assert len(id1) == 12
    print(f"[PASS] Meal ID is stable: {id1}")


def test_meal_id_unique():
    meal2 = {**SAMPLE_MEAL, "name": "Falafel Plate"}
    id1 = meal_id(SAMPLE_MEAL)
    id2 = meal_id(meal2)
    assert id1 != id2
    print("[PASS] Different meals get different IDs")


def test_dry_run():
    batch = {"meals": [SAMPLE_MEAL]}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(batch, f)
        f.flush()
        meals = load_meals(f.name)

    results, stats = generate_batch(meals, None, dry_run=True)
    assert len(results) == 1
    assert results[0]["image"]["status"] == "dry_run"
    assert "prompt" in results[0]["image"]
    Path(f.name).unlink()
    print("[PASS] Dry run mode works correctly")


if __name__ == "__main__":
    test_build_prompt_includes_name()
    test_build_prompt_includes_styling()
    test_build_prompt_includes_ingredients()
    test_build_prompt_excludes_optional()
    test_build_prompt_no_text_watermark()
    test_build_prompt_unknown_cuisine()
    test_all_cuisines_have_styling()
    test_meal_id_stable()
    test_meal_id_unique()
    test_dry_run()
    print(f"\nAll tests passed")
