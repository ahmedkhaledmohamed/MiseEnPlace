"""
MiseEnPlace Image Generator — Stage 4 of the offline pipeline.

Generates food photography-style hero images for meals using Together AI's
FLUX.1 model. Builds rich prompts from meal metadata to produce
appetizing, consistent imagery.

Usage:
    python -m images.image_generator --input output/costed/costed_batch_20260625.json
    python -m images.image_generator --input output/meals/sample.json --dry-run
    python -m images.image_generator --input output/costed/ --all --limit 10

Requires TOGETHER_API_KEY environment variable.
"""

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "output" / "images"
MANIFEST_DIR = Path(__file__).parent.parent / "output" / "imaged"

CUISINE_STYLING = {
    "Middle Eastern": "rustic wooden board, warm golden lighting, mezze-style spread",
    "Mediterranean": "terracotta plate, olive branch garnish, sun-drenched natural light",
    "East Asian": "dark ceramic bowl, chopsticks, minimalist presentation",
    "South Asian": "brass thali plate, vibrant colors, rich warm tones",
    "Southeast Asian": "banana leaf, tropical garnish, bright natural light",
    "Latin American": "colorful Talavera plate, lime wedges, festive presentation",
    "Mexican": "cast iron skillet, lime and cilantro, rustic cantina table",
    "Italian": "white ceramic plate, fresh herbs, marble countertop",
    "French": "fine white porcelain, elegant plating, soft diffused light",
    "American": "rustic stoneware plate, hearty portions, farmhouse table",
    "African": "handcrafted bowl, bold spices visible, warm earth tones",
    "Caribbean": "bright tropical plate, scotch bonnet garnish, outdoor light",
    "Eastern European": "enamel plate, hearty rustic presentation, wooden table",
    "Scandinavian": "minimalist white plate, clean lines, natural nordic light",
    "British": "classic white plate, proper garnish, warm pub lighting",
    "Korean": "dolsot stone bowl, banchan sides, dark wood table",
    "Japanese": "lacquer tray, zen presentation, precise arrangement",
    "Chinese": "blue and white porcelain, family-style serving, round table",
    "Thai": "woven plate, fresh herbs, street food energy",
    "Vietnamese": "ceramic bowl, fresh herbs and bean sprouts, light and bright",
    "Indian": "copper serving dish, naan on side, rich spice colors",
    "Turkish": "ornate copper plate, pide bread, bazaar ambiance",
    "Greek": "blue-rimmed white plate, feta crumbles, Mediterranean sun",
    "Spanish": "terra cotta cazuela, tapas style, warm evening light",
    "Fusion": "modern slate plate, artistic drizzle, contemporary plating",
}

DEFAULT_STYLING = "ceramic plate, natural lighting, overhead flat-lay angle"


def build_image_prompt(meal):
    """Build an image generation prompt from meal metadata."""
    name = meal.get("name", "dish")
    description = meal.get("description", "")
    cuisine = meal.get("cuisine", "")
    meal_type = meal.get("meal_type", "dinner")

    key_ingredients = []
    for ing in meal.get("ingredients", [])[:6]:
        if not ing.get("is_optional", False) and ing["category"] not in ("spice", "oil-fat", "liquid"):
            key_ingredients.append(ing["name"])

    styling = CUISINE_STYLING.get(cuisine, DEFAULT_STYLING)

    ingredient_text = ", ".join(key_ingredients[:4]) if key_ingredients else ""

    prompt = (
        f"Professional food photography of {name}. "
        f"{description}. "
        f"Styled on {styling}. "
    )

    if ingredient_text:
        prompt += f"Key visible ingredients: {ingredient_text}. "

    prompt += (
        "Shot from 45-degree angle with shallow depth of field. "
        "Warm, appetizing color grading. Natural window light with soft shadows. "
        "No text, no watermarks, no hands, no people. "
        "Magazine-quality editorial food photography."
    )

    return prompt


def meal_id(meal):
    """Generate a stable ID for a meal based on its name and cuisine."""
    key = f"{meal.get('name', '')}:{meal.get('cuisine', '')}".lower()
    return hashlib.md5(key.encode()).hexdigest()[:12]


def generate_image(meal, api_key):
    """Generate an image for a meal using Together AI's FLUX.1 model."""
    prompt = build_image_prompt(meal)

    request_body = json.dumps({
        "model": "black-forest-labs/FLUX.1-schnell-Free",
        "prompt": prompt,
        "n": 1,
        "width": 1024,
        "height": 1024,
        "steps": 4,
    }).encode()

    req = urllib.request.Request(
        "https://api.together.xyz/v1/images/generations",
        data=request_body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())

    image_data = result["data"][0]
    image_url = image_data.get("url")

    if not image_url and image_data.get("b64_json"):
        import base64
        b64 = image_data["b64_json"]
        return b64, prompt, True

    return image_url, prompt, False


def save_image(data, output_path, is_base64=False):
    """Save an image from URL or base64 data to local path."""
    if is_base64:
        import base64
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(data))
    else:
        urllib.request.urlretrieve(data, output_path)


def load_meals(input_path):
    """Load meals from a batch file or directory."""
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


def generate_batch(meals, api_key, dry_run=False):
    """Generate images for a batch of meals."""
    results = []
    stats = {"total": 0, "generated": 0, "skipped": 0, "error": 0}

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for i, (source_file, meal) in enumerate(meals):
        name = meal.get("name", f"Meal {i + 1}")
        mid = meal_id(meal)
        image_path = OUTPUT_DIR / f"{mid}.png"
        stats["total"] += 1

        print(f"\n[{i + 1}/{len(meals)}] {name} (id: {mid})")

        if image_path.exists() and not dry_run:
            print(f"  [SKIP] Image already exists: {image_path.name}")
            stats["skipped"] += 1
            results.append({
                **meal,
                "image": {
                    "id": mid,
                    "path": str(image_path),
                    "status": "exists",
                },
            })
            continue

        if dry_run:
            prompt = build_image_prompt(meal)
            print(f"  [DRY RUN] Would generate image")
            print(f"  Prompt: {prompt[:120]}...")
            results.append({
                **meal,
                "image": {
                    "id": mid,
                    "prompt": prompt,
                    "status": "dry_run",
                },
            })
            continue

        try:
            image_data, prompt_used, is_base64 = generate_image(meal, api_key)
            save_image(image_data, image_path, is_base64=is_base64)
            stats["generated"] += 1
            print(f"  [OK] Saved: {image_path.name}")

            results.append({
                **meal,
                "image": {
                    "id": mid,
                    "path": str(image_path),
                    "prompt": prompt_used,
                    "status": "generated",
                },
            })

            time.sleep(1)

        except Exception as e:
            stats["error"] += 1
            print(f"  [ERROR] {e}", file=sys.stderr)
            results.append({
                **meal,
                "image": {
                    "id": mid,
                    "status": "error",
                    "error": str(e),
                },
            })

    return results, stats


def save_manifest(results, stats, label):
    """Save image generation manifest."""
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"imaged_{label}_{timestamp}.json"
    path = MANIFEST_DIR / filename

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(results),
        "stats": stats,
        "meals": results,
    }

    with open(path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved manifest for {len(results)} meals to {path}")
    return path


def print_summary(stats):
    print(f"\n{'=' * 50}")
    print(f"IMAGE GENERATION SUMMARY")
    print(f"{'=' * 50}")
    print(f"Total meals:  {stats['total']}")
    print(f"  Generated:  {stats['generated']}")
    print(f"  Skipped:    {stats['skipped']}")
    print(f"  Errors:     {stats['error']}")
    print(f"{'=' * 50}")


def main():
    parser = argparse.ArgumentParser(description="Generate food photography images for meals")
    parser.add_argument("--input", type=str, required=True, help="Path to meal batch file or directory")
    parser.add_argument("--all", action="store_true", help="Process all JSON files in directory")
    parser.add_argument("--dry-run", action="store_true", help="Show prompts without generating images")
    parser.add_argument("--limit", type=int, help="Max number of meals to process")
    args = parser.parse_args()

    api_key = None
    if not args.dry_run:
        api_key = os.environ.get("TOGETHER_API_KEY")
        if not api_key:
            print("Error: TOGETHER_API_KEY environment variable not set", file=sys.stderr)
            sys.exit(1)

    meals = load_meals(args.input)

    if not meals:
        print("No meals found in input", file=sys.stderr)
        sys.exit(1)

    if args.limit:
        meals = meals[:args.limit]

    print(f"Found {len(meals)} meals to generate images for")

    results, stats = generate_batch(meals, api_key, dry_run=args.dry_run)

    label = Path(args.input).stem if not Path(args.input).is_dir() else "batch"
    save_manifest(results, stats, label)
    print_summary(stats)


if __name__ == "__main__":
    main()
