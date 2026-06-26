"""Offline tests for the graph builder — no API key needed."""

import json
import sqlite3
import tempfile
from pathlib import Path

from graph.graph_builder import (
    normalize_ingredient_name,
    init_db,
    insert_meal,
    compute_similarity,
    load_meals,
    build_graph,
)

MEAL_A = {
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
    "dietary_tags": ["halal", "gluten-free"],
    "ingredients": [
        {"name": "chicken thighs", "quantity": 680, "unit": "g", "category": "protein"},
        {"name": "basmati rice", "quantity": 2, "unit": "cup", "category": "grain"},
        {"name": "cumin", "quantity": 1, "unit": "tsp", "category": "spice"},
        {"name": "olive oil", "quantity": 2, "unit": "tbsp", "category": "oil-fat"},
        {"name": "lemon", "quantity": 1, "unit": "each", "category": "fruit"},
        {"name": "garlic", "quantity": 4, "unit": "clove", "category": "vegetable"},
    ],
    "steps": [
        {"order": 1, "instruction": "Mix spices", "duration_minutes": 3},
        {"order": 2, "instruction": "Cook chicken", "duration_minutes": 12},
    ],
    "equipment": ["skillet", "pot"],
    "tips": ["Marinate overnight"],
    "variations": ["Use lamb instead"],
    "source_inspiration": "Levantine shawarma",
    "cost_estimate": {
        "total_cost": 11.65,
        "cost_per_serving": 2.91,
        "currency": "CAD",
        "ingredient_costs": [
            {"name": "chicken thighs", "cost": 7.48},
            {"name": "basmati rice", "cost": 2.09},
        ],
    },
    "image": {"id": "abc123", "path": "/images/abc123.png"},
    "grounding": {"status": "pass", "confidence": 0.9},
}

MEAL_B = {
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
        {"name": "ginger", "quantity": 30, "unit": "g", "category": "vegetable"},
    ],
    "steps": [
        {"order": 1, "instruction": "Marinate chicken", "duration_minutes": 30},
        {"order": 2, "instruction": "Layer and cook", "duration_minutes": 45},
    ],
    "equipment": ["large pot"],
    "tips": ["Use saffron for color"],
    "variations": ["Vegetable biryani"],
    "source_inspiration": "Hyderabadi biryani",
}

MEAL_C = {
    "name": "Margherita Pizza",
    "description": "Classic tomato and mozzarella",
    "cuisine": "Italian",
    "difficulty": "medium",
    "meal_type": "dinner",
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
        {"name": "olive oil", "quantity": 2, "unit": "tbsp", "category": "oil-fat"},
    ],
    "steps": [
        {"order": 1, "instruction": "Make dough", "duration_minutes": 10},
        {"order": 2, "instruction": "Top and bake", "duration_minutes": 15},
    ],
    "equipment": ["oven", "baking stone"],
    "tips": ["Use 00 flour"],
    "variations": ["Add prosciutto"],
    "source_inspiration": "Neapolitan pizza",
}


def _temp_db():
    f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    f.close()
    return Path(f.name)


def test_normalize_ingredient():
    assert normalize_ingredient_name("Fresh Basil") == "basil"
    assert normalize_ingredient_name("Boneless Skinless Chicken Breast") == "chicken breast"
    print("[PASS] Ingredient normalization")


def test_init_db():
    db_path = _temp_db()
    conn = init_db(db_path)
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    table_names = {t[0] for t in tables}
    assert "meals" in table_names
    assert "ingredients" in table_names
    assert "meal_ingredients" in table_names
    assert "meal_similarity" in table_names
    conn.close()
    db_path.unlink()
    print("[PASS] Database initialization creates all tables")


def test_insert_meal():
    db_path = _temp_db()
    conn = init_db(db_path)
    meal_id = insert_meal(conn, MEAL_A)
    conn.commit()
    assert meal_id is not None

    row = conn.execute("SELECT name, cuisine, cost_per_serving FROM meals WHERE id = ?", (meal_id,)).fetchone()
    assert row[0] == "Chicken Shawarma Bowl"
    assert row[1] == "Middle Eastern"
    assert row[2] == 2.91

    ings = conn.execute("SELECT COUNT(*) FROM meal_ingredients WHERE meal_id = ?", (meal_id,)).fetchone()[0]
    assert ings == 6

    seasons = conn.execute("SELECT season FROM meal_seasons WHERE meal_id = ?", (meal_id,)).fetchall()
    assert ("all",) in seasons

    tags = conn.execute("SELECT tag FROM meal_dietary_tags WHERE meal_id = ?", (meal_id,)).fetchall()
    assert ("halal",) in tags
    assert ("gluten-free",) in tags

    steps = conn.execute("SELECT COUNT(*) FROM meal_steps WHERE meal_id = ?", (meal_id,)).fetchone()[0]
    assert steps == 2

    conn.close()
    db_path.unlink()
    print("[PASS] Insert meal with all relationships")


def test_duplicate_meal_skipped():
    db_path = _temp_db()
    conn = init_db(db_path)
    id1 = insert_meal(conn, MEAL_A)
    conn.commit()
    id2 = insert_meal(conn, MEAL_A)
    conn.commit()
    assert id1 is not None
    assert id2 is None
    conn.close()
    db_path.unlink()
    print("[PASS] Duplicate meal correctly skipped")


def test_ingredient_dedup():
    db_path = _temp_db()
    conn = init_db(db_path)
    insert_meal(conn, MEAL_A)
    insert_meal(conn, MEAL_B)
    conn.commit()

    # Both meals use "chicken thighs", "basmati rice", "cumin", "garlic"
    chicken = conn.execute("SELECT COUNT(*) FROM ingredients WHERE name = 'chicken thighs'").fetchone()[0]
    assert chicken == 1

    garlic = conn.execute("SELECT COUNT(*) FROM ingredients WHERE name = 'garlic'").fetchone()[0]
    assert garlic == 1

    conn.close()
    db_path.unlink()
    print("[PASS] Shared ingredients are deduplicated")


def test_compute_similarity():
    db_path = _temp_db()
    conn = init_db(db_path)
    insert_meal(conn, MEAL_A)
    insert_meal(conn, MEAL_B)
    insert_meal(conn, MEAL_C)
    conn.commit()

    pairs = compute_similarity(conn)
    assert pairs >= 1

    # A and B share chicken thighs, basmati rice, cumin, garlic (4 ingredients)
    sim = conn.execute("""
        SELECT shared_ingredient_count, overlap_ratio, shared_ingredients
        FROM meal_similarity
        WHERE (meal_a_id = 1 AND meal_b_id = 2) OR (meal_a_id = 2 AND meal_b_id = 1)
    """).fetchone()
    assert sim is not None
    assert sim[0] >= 3  # at least chicken, rice, garlic (cumin is a staple via garlic normalization)

    shared_list = json.loads(sim[2])
    assert "chicken thighs" in shared_list
    assert "basmati rice" in shared_list

    conn.close()
    db_path.unlink()
    print(f"[PASS] Similarity computed: {pairs} pairs, A↔B share {sim[0]} ingredients ({sim[1]:.0%} overlap)")


def test_pantry_staples():
    db_path = _temp_db()
    conn = init_db(db_path)
    insert_meal(conn, MEAL_A)
    conn.commit()

    staples = conn.execute("SELECT name FROM ingredients WHERE is_pantry_staple = 1").fetchall()
    staple_names = {s[0] for s in staples}
    assert "olive oil" in staple_names
    assert "garlic" in staple_names

    non_staples = conn.execute("SELECT name FROM ingredients WHERE is_pantry_staple = 0").fetchall()
    non_staple_names = {s[0] for s in non_staples}
    assert "chicken thighs" in non_staple_names

    conn.close()
    db_path.unlink()
    print("[PASS] Pantry staples correctly identified")


def test_build_graph_full():
    db_path = _temp_db()
    batch = {"meals": [MEAL_A, MEAL_B, MEAL_C]}

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(batch, f)
        f.flush()
        meals = load_meals(f.name)

    stats = build_graph(meals, db_path)
    assert stats["inserted"] == 3
    assert stats["skipped"] == 0
    assert stats["similarity_pairs"] >= 1

    conn = sqlite3.connect(str(db_path))
    total_meals = conn.execute("SELECT COUNT(*) FROM meals").fetchone()[0]
    total_ings = conn.execute("SELECT COUNT(*) FROM ingredients").fetchone()[0]
    total_edges = conn.execute("SELECT COUNT(*) FROM meal_ingredients").fetchone()[0]
    conn.close()

    assert total_meals == 3
    assert total_ings > 5
    assert total_edges > 10

    db_path.unlink()
    Path(f.name).unlink()
    print(f"[PASS] Full graph build: {total_meals} meals, {total_ings} ingredients, {total_edges} edges")


def test_dry_run():
    batch = {"meals": [MEAL_A]}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(batch, f)
        f.flush()
        meals = load_meals(f.name)

    stats = build_graph(meals, _temp_db(), dry_run=True)
    assert stats["total"] == 1
    assert stats["inserted"] == 0
    Path(f.name).unlink()
    print("[PASS] Dry run mode works")


if __name__ == "__main__":
    test_normalize_ingredient()
    test_init_db()
    test_insert_meal()
    test_duplicate_meal_skipped()
    test_ingredient_dedup()
    test_compute_similarity()
    test_pantry_staples()
    test_build_graph_full()
    test_dry_run()
    print(f"\nAll tests passed")
