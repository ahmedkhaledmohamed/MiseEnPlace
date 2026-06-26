"""
MiseEnPlace Meal Generator — Stage 1 of the offline pipeline.

Generates structured meal records using Together AI, validated against
the meal JSON schema. Outputs one JSON file per batch into pipeline/output/meals/.

Usage:
    python -m generators.meal_generator --cuisine "Middle Eastern" --count 5
    python -m generators.meal_generator --batch-file generators/batches/sample.json
    python -m generators.meal_generator --diverse --count 20

Requires TOGETHER_API_KEY environment variable.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import jsonschema
from openai import OpenAI

SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "meal.json"
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "meals"

CUISINES = [
    "Middle Eastern", "Mediterranean", "East Asian", "South Asian",
    "Southeast Asian", "Latin American", "Mexican", "Italian", "French",
    "American", "African", "Caribbean", "Eastern European", "Scandinavian",
    "British", "Korean", "Japanese", "Chinese", "Thai", "Vietnamese",
    "Indian", "Turkish", "Greek", "Spanish", "Fusion",
]

MEAL_TYPES = ["breakfast", "lunch", "dinner", "snack", "dessert", "side"]

DIFFICULTIES = ["easy", "medium", "advanced", "project"]

DIFFICULTY_DISTRIBUTION = {"easy": 0.3, "medium": 0.4, "advanced": 0.2, "project": 0.1}

SYSTEM_PROMPT = """You are a professional chef and recipe developer for MiseEnPlace, a home cooking app.
Your job is to generate detailed, accurate, and diverse meal recipes as structured JSON.

Rules:
- Every recipe must be cookable by a home cook with standard kitchen equipment.
- Ingredient quantities must be realistic and precise. Never hallucinate proportions.
- Steps must be in logical order and each step must be actionable.
- Cooking times must be realistic for the technique described.
- total_time_minutes = prep_time_minutes + cook_time_minutes (approximately).
- Tag seasonal ingredients correctly. "all" means available year-round.
- Dietary tags must be accurate — don't tag something "vegan" if it contains dairy.
- Include at least 1-2 tips that genuinely help a home cook.
- Include at least 1 variation for accessibility or dietary preference.
- source_inspiration should reference the cultural or culinary tradition the dish comes from.
- Use metric-compatible units where possible (g, kg, ml, L) but cups/tbsp/tsp are fine for small quantities.
"""


def build_generation_prompt(cuisine, meal_type, difficulty, count):
    return f"""Generate exactly {count} unique {cuisine} {meal_type} recipe(s) at "{difficulty}" difficulty level.

Return a JSON array of meal objects. Each meal must conform exactly to this schema:

- name: string (the dish name)
- description: string (1-2 sentence appetizing description, min 10 chars)
- cuisine: "{cuisine}"
- difficulty: "{difficulty}"
- prep_time_minutes: integer (realistic prep time)
- cook_time_minutes: integer (realistic cook time)
- total_time_minutes: integer (should ≈ prep + cook)
- servings: integer (typical home serving size, usually 2-6)
- seasons: array of "spring"|"summer"|"fall"|"winter"|"all"
- dietary_tags: array from ["vegan","vegetarian","gluten-free","dairy-free","nut-free","keto","paleo","halal","kosher","low-carb","high-protein"] — only include tags that are genuinely true
- meal_type: "{meal_type}"
- ingredients: array of objects with:
  - name: string
  - quantity: number
  - unit: one of "g"|"kg"|"ml"|"L"|"cup"|"tbsp"|"tsp"|"oz"|"lb"|"each"|"bunch"|"clove"|"slice"|"pinch"|"to taste"|"head"|"sprig"|"stalk"|"piece"|"can"|"package"|"sheet"|"stick"|"fillet"|"rack"|"loaf"|"block"|"cm"|"inch"
  - is_optional: boolean
  - category: one of "protein"|"vegetable"|"fruit"|"grain"|"dairy"|"spice"|"oil-fat"|"sauce-condiment"|"herb"|"legume"|"nut-seed"|"sweetener"|"liquid"|"other"
  - prep_note: string (optional, e.g. "diced", "minced")
- steps: array of objects with:
  - order: integer starting at 1
  - instruction: string (clear, actionable, min 5 chars)
  - duration_minutes: integer (optional)
- equipment: array of strings
- tips: array of strings (1-3 practical tips)
- variations: array of strings (1-2 variations)
- source_inspiration: string (cultural/culinary origin)

Return ONLY the JSON array, no markdown fences, no explanation."""


def load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def validate_meal(meal, schema):
    try:
        jsonschema.validate(instance=meal, schema=schema)
        return True, None
    except jsonschema.ValidationError as e:
        return False, str(e.message)


DEFAULT_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"


MAX_RETRIES = 2


def repair_json(text):
    """Fix common LLM JSON issues: trailing commas, comments, fractions, incomplete arrays."""
    import re
    text = re.sub(r'//[^\n]*', '', text)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    text = re.sub(r',\s*([}\]])', r'\1', text)
    text = re.sub(r':\s*(\d+)\s*/\s*(\d+)', lambda m: f': {int(m.group(1)) / int(m.group(2))}', text)
    text = re.sub(r':\s*(\d+)\s+(\d+)\s*/\s*(\d+)', lambda m: f': {int(m.group(1)) + int(m.group(2)) / int(m.group(3))}', text)
    if text.count('[') > text.count(']'):
        text = text.rstrip().rstrip(',') + ']'
    if text.count('{') > text.count('}'):
        text = text.rstrip().rstrip(',') + '}'
    return text


def generate_meals(client, cuisine, meal_type, difficulty, count, schema, model=None):
    prompt = build_generation_prompt(cuisine, meal_type, difficulty, count)

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=model or DEFAULT_MODEL,
                max_tokens=8192,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )

            text = response.choices[0].message.content.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()

            try:
                meals = json.loads(text)
            except json.JSONDecodeError:
                text = repair_json(text)
                meals = json.loads(text)
            break
        except (json.JSONDecodeError, Exception) as e:
            if attempt < MAX_RETRIES:
                print(f"  [RETRY] Attempt {attempt + 1} failed: {e}", file=sys.stderr)
                time.sleep(1)
                continue
            print(f"  [SKIP] All attempts failed: {e}", file=sys.stderr)
            return []

    if isinstance(meals, dict):
        meals = [meals]

    validated = []
    for i, meal in enumerate(meals):
        normalize_units(meal)
        valid, error = validate_meal(meal, schema)
        if valid:
            validated.append(meal)
            print(f"  [OK] {meal['name']}")
        else:
            print(f"  [FAIL] Meal {i + 1}: {error}", file=sys.stderr)

    return validated


UNIT_ALIASES = {
    "cloves": "clove", "bunches": "bunch", "slices": "slice",
    "pieces": "piece", "sprigs": "sprig", "stalks": "stalk",
    "heads": "head", "cans": "can", "packages": "package",
    "sheets": "sheet", "sticks": "stick", "fillets": "fillet",
    "racks": "rack", "loaves": "loaf", "blocks": "block",
    "inches": "inch", "cups": "cup", "pounds": "lb", "pound": "lb",
    "ounces": "oz", "ounce": "oz", "teaspoon": "tsp", "teaspoons": "tsp",
    "tablespoon": "tbsp", "tablespoons": "tbsp", "grams": "g", "gram": "g",
    "kilograms": "kg", "kilogram": "kg", "liters": "L", "liter": "L",
    "litres": "L", "litre": "L", "milliliters": "ml", "milliliter": "ml",
    "millilitres": "ml", "millilitre": "ml", "whole": "each",
}


def normalize_units(meal):
    for ing in meal.get("ingredients", []):
        unit = ing.get("unit", "")
        if unit in UNIT_ALIASES:
            ing["unit"] = UNIT_ALIASES[unit]


def save_batch(meals, label):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{label}_{timestamp}.json"
    path = OUTPUT_DIR / filename

    batch = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(meals),
        "meals": meals,
    }

    with open(path, "w") as f:
        json.dump(batch, f, indent=2)

    print(f"\nSaved {len(meals)} meals to {path}")
    return path


def run_diverse(client, schema, total_count):
    """Generate a diverse set of meals across cuisines, types, and difficulties."""
    meals = []
    seen_names = set()
    per_batch = 3

    cuisine_idx = 0
    type_idx = 0
    diff_weights = list(DIFFICULTY_DISTRIBUTION.items())

    while len(meals) < total_count:
        cuisine = CUISINES[cuisine_idx % len(CUISINES)]
        meal_type = MEAL_TYPES[type_idx % len(MEAL_TYPES)]

        cumulative = 0
        ratio = (len(meals) / total_count) if total_count > 0 else 0
        difficulty = "medium"
        for diff, weight in diff_weights:
            cumulative += weight
            if ratio < cumulative:
                difficulty = diff
                break

        remaining = total_count - len(meals)
        batch_size = min(per_batch, remaining)

        print(f"\n[{len(meals)}/{total_count}] Generating {batch_size}x {cuisine} {meal_type} ({difficulty})...")
        batch = generate_meals(client, cuisine, meal_type, difficulty, batch_size, schema)

        for meal in batch:
            name = meal.get("name", "")
            if name not in seen_names:
                meals.append(meal)
                seen_names.add(name)

        cuisine_idx += 1
        type_idx += 1

        time.sleep(0.5)

    return meals


def run_batch_file(client, schema, batch_file):
    """Run generation from a batch specification file."""
    with open(batch_file) as f:
        spec = json.load(f)

    meals = []
    for entry in spec["batches"]:
        cuisine = entry["cuisine"]
        meal_type = entry.get("meal_type", "dinner")
        difficulty = entry.get("difficulty", "medium")
        count = entry.get("count", 3)

        print(f"\nGenerating {count}x {cuisine} {meal_type} ({difficulty})...")
        batch = generate_meals(client, cuisine, meal_type, difficulty, count, schema)
        meals.extend(batch)
        time.sleep(0.5)

    return meals


def main():
    parser = argparse.ArgumentParser(description="Generate structured meal recipes using Together AI")
    parser.add_argument("--cuisine", type=str, help="Cuisine to generate (e.g. 'Italian')")
    parser.add_argument("--meal-type", type=str, default="dinner", choices=MEAL_TYPES)
    parser.add_argument("--difficulty", type=str, default="medium", choices=DIFFICULTIES)
    parser.add_argument("--count", type=int, default=5, help="Number of meals to generate")
    parser.add_argument("--diverse", action="store_true", help="Generate diverse meals across all cuisines/types")
    parser.add_argument("--batch-file", type=str, help="Path to batch specification JSON file")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Together AI model to use")
    parser.add_argument("--dry-run", action="store_true", help="Print the prompt without calling the API")
    args = parser.parse_args()

    schema = load_schema()

    if args.dry_run:
        cuisine = args.cuisine or "Italian"
        prompt = build_generation_prompt(cuisine, args.meal_type, args.difficulty, args.count)
        print("=== SYSTEM PROMPT ===")
        print(SYSTEM_PROMPT)
        print("\n=== USER PROMPT ===")
        print(prompt)
        return

    api_key = os.environ.get("TOGETHER_API_KEY")
    if not api_key:
        print("Error: TOGETHER_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url="https://api.together.xyz/v1")

    if args.batch_file:
        meals = run_batch_file(client, schema, args.batch_file)
        label = Path(args.batch_file).stem
    elif args.diverse:
        meals = run_diverse(client, schema, args.count)
        label = "diverse"
    else:
        if not args.cuisine:
            print("Error: --cuisine is required (or use --diverse / --batch-file)", file=sys.stderr)
            sys.exit(1)
        print(f"\nGenerating {args.count}x {args.cuisine} {args.meal_type} ({args.difficulty})...")
        meals = generate_meals(client, args.cuisine, args.meal_type, args.difficulty, args.count, schema)
        label = f"{args.cuisine.lower().replace(' ', '_')}_{args.meal_type}"

    if meals:
        save_batch(meals, label)
        print(f"\nTotal: {len(meals)} meals generated and validated")
    else:
        print("\nNo valid meals generated", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
