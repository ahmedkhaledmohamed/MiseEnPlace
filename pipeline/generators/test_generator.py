"""Offline tests for the meal generator — no API key needed."""

import json
from pathlib import Path

from generators.meal_generator import load_schema, validate_meal

SAMPLE_MEAL = {
    "name": "Chicken Shawarma Bowl",
    "description": "Spiced chicken thighs over basmati rice with pickled vegetables and garlic sauce",
    "cuisine": "Middle Eastern",
    "difficulty": "medium",
    "prep_time_minutes": 20,
    "cook_time_minutes": 25,
    "total_time_minutes": 45,
    "servings": 4,
    "seasons": ["all"],
    "dietary_tags": ["halal", "gluten-free", "dairy-free"],
    "meal_type": "dinner",
    "ingredients": [
        {"name": "chicken thighs", "quantity": 680, "unit": "g", "is_optional": False, "category": "protein", "prep_note": "boneless, skinless"},
        {"name": "basmati rice", "quantity": 2, "unit": "cup", "is_optional": False, "category": "grain"},
        {"name": "cumin", "quantity": 1, "unit": "tsp", "is_optional": False, "category": "spice"},
        {"name": "paprika", "quantity": 1, "unit": "tsp", "is_optional": False, "category": "spice"},
        {"name": "turmeric", "quantity": 0.5, "unit": "tsp", "is_optional": False, "category": "spice"},
        {"name": "olive oil", "quantity": 2, "unit": "tbsp", "is_optional": False, "category": "oil-fat"},
        {"name": "lemon", "quantity": 1, "unit": "each", "is_optional": False, "category": "fruit"},
        {"name": "garlic", "quantity": 4, "unit": "clove", "is_optional": False, "category": "vegetable", "prep_note": "minced"},
        {"name": "pickled turnips", "quantity": 100, "unit": "g", "is_optional": True, "category": "vegetable"},
    ],
    "steps": [
        {"order": 1, "instruction": "Mix cumin, paprika, turmeric, salt, and pepper in a bowl", "duration_minutes": 3},
        {"order": 2, "instruction": "Coat chicken thighs with spice mixture and olive oil, let marinate 15 minutes", "duration_minutes": 15},
        {"order": 3, "instruction": "Cook basmati rice according to package directions", "duration_minutes": 20},
        {"order": 4, "instruction": "Heat a cast iron skillet over medium-high heat and cook chicken 5-6 minutes per side until charred and cooked through", "duration_minutes": 12},
        {"order": 5, "instruction": "Slice chicken and serve over rice with pickled vegetables and a squeeze of lemon", "duration_minutes": 3},
    ],
    "equipment": ["cast iron skillet", "mixing bowl", "rice cooker or pot"],
    "tips": [
        "Marinate overnight for deeper flavor",
        "Use a meat thermometer — chicken is done at 165°F / 74°C",
    ],
    "variations": [
        "Swap chicken for lamb shoulder for a richer flavor",
        "Make it vegan with roasted cauliflower and chickpeas",
    ],
    "source_inspiration": "Traditional Levantine shawarma, adapted for home cooking without a vertical spit",
}


def test_valid_meal():
    schema = load_schema()
    valid, error = validate_meal(SAMPLE_MEAL, schema)
    assert valid, f"Valid meal failed validation: {error}"
    print("[PASS] Valid meal passes schema validation")


def test_invalid_meal_missing_name():
    schema = load_schema()
    meal = {k: v for k, v in SAMPLE_MEAL.items() if k != "name"}
    valid, error = validate_meal(meal, schema)
    assert not valid, "Meal without name should fail validation"
    print("[PASS] Meal without name correctly rejected")


def test_invalid_meal_bad_cuisine():
    schema = load_schema()
    meal = {**SAMPLE_MEAL, "cuisine": "Martian"}
    valid, error = validate_meal(meal, schema)
    assert not valid, "Meal with invalid cuisine should fail validation"
    print("[PASS] Meal with invalid cuisine correctly rejected")


def test_invalid_meal_no_ingredients():
    schema = load_schema()
    meal = {**SAMPLE_MEAL, "ingredients": []}
    valid, error = validate_meal(meal, schema)
    assert not valid, "Meal with empty ingredients should fail validation"
    print("[PASS] Meal with empty ingredients correctly rejected")


def test_invalid_meal_bad_unit():
    schema = load_schema()
    meal = {**SAMPLE_MEAL, "ingredients": [
        {"name": "chicken", "quantity": 1, "unit": "handful", "category": "protein"},
    ]}
    valid, error = validate_meal(meal, schema)
    assert not valid, "Meal with invalid unit should fail validation"
    print("[PASS] Meal with invalid unit correctly rejected")


def test_schema_loads():
    schema = load_schema()
    assert schema["title"] == "Meal"
    assert "ingredients" in schema["properties"]
    print("[PASS] Schema loads correctly")


if __name__ == "__main__":
    test_schema_loads()
    test_valid_meal()
    test_invalid_meal_missing_name()
    test_invalid_meal_bad_cuisine()
    test_invalid_meal_no_ingredients()
    test_invalid_meal_bad_unit()
    print(f"\nAll tests passed")
