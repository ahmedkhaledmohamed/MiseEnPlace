"""
MiseEnPlace Recipe Grounder — Stage 2 of the offline pipeline.

Takes generated meal records and verifies them against real recipes using
Together AI for analysis. Produces grounded records with confidence scores,
source references, and flagged issues.

Usage:
    python -m grounding.recipe_grounder --input output/meals/italian_dinner_20260625.json
    python -m grounding.recipe_grounder --input output/meals/ --all
    python -m grounding.recipe_grounder --input output/meals/sample.json --dry-run

Requires TOGETHER_API_KEY environment variable.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

OUTPUT_DIR = Path(__file__).parent.parent / "output" / "grounded"

GROUNDING_SYSTEM_PROMPT = """You are a professional chef and food scientist reviewing AI-generated recipes for accuracy and feasibility.

Your job is to evaluate whether a recipe is realistic, safe, and well-proportioned by comparing it against your knowledge of real-world cooking.

You must be strict but fair. A recipe doesn't need to be identical to a famous version — home cooking variations are fine — but it must be:
1. Physically feasible (steps must work in sequence)
2. Safe (no missing critical safety steps like meat temperatures)
3. Well-proportioned (ingredient quantities must produce edible results)
4. Culturally respectful (dish names and descriptions should be accurate)
5. Time-realistic (prep and cook times should match the steps described)
"""

GROUNDING_PROMPT_TEMPLATE = """Evaluate this AI-generated recipe for accuracy and feasibility.

Recipe to evaluate:
```json
{recipe_json}
```

Analyze the recipe across these dimensions and return a JSON object:

1. **ingredient_check**: Are all ingredients appropriate for this dish? Are any critical ingredients missing? Are any ingredients unusual or wrong?
2. **proportion_check**: Are the quantities realistic? Would these proportions produce a well-balanced dish for the stated number of servings?
3. **technique_check**: Are the cooking steps in logical order? Is each step feasible? Are any critical steps missing (e.g., preheating, resting meat)?
4. **time_check**: Are prep_time, cook_time, and total_time realistic for the steps described?
5. **safety_check**: Are there any food safety concerns? Missing temperature guidelines? Raw meat handling issues?
6. **cultural_check**: Is the dish name accurate? Is the cuisine classification correct? Is the description culturally respectful?
7. **real_world_match**: Does this recipe closely match known real-world versions of this dish? Name 1-3 well-known versions or sources it resembles.

Return ONLY a JSON object with this structure:
{{
    "ingredient_score": <0.0-1.0>,
    "ingredient_issues": ["list of specific issues, empty if none"],
    "proportion_score": <0.0-1.0>,
    "proportion_issues": ["list of specific issues"],
    "technique_score": <0.0-1.0>,
    "technique_issues": ["list of specific issues"],
    "time_score": <0.0-1.0>,
    "time_issues": ["list of specific issues"],
    "safety_score": <0.0-1.0>,
    "safety_issues": ["list of specific issues"],
    "cultural_score": <0.0-1.0>,
    "cultural_issues": ["list of specific issues"],
    "real_world_references": ["1-3 real recipes or sources this resembles"],
    "suggested_fixes": ["specific actionable fixes, empty if recipe is good"],
    "overall_confidence": <0.0-1.0>,
    "verdict": "pass" | "needs_review" | "fail"
}}

Scoring guide:
- 0.9-1.0: Excellent, matches real-world recipes closely
- 0.7-0.89: Good, minor issues that don't affect cookability
- 0.5-0.69: Needs review, some issues that could affect results
- Below 0.5: Fail, significant issues that would make the dish unsuccessful

overall_confidence = weighted average:
  ingredient_score * 0.25 + proportion_score * 0.20 + technique_score * 0.20 +
  time_score * 0.10 + safety_score * 0.15 + cultural_score * 0.10

verdict rules:
- "pass": overall_confidence >= 0.7 AND no safety_score < 0.5
- "needs_review": overall_confidence >= 0.5 OR any single score < 0.5
- "fail": overall_confidence < 0.5 OR safety_score < 0.3

Return ONLY the JSON object, no markdown fences, no explanation."""


DEFAULT_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"


def ground_meal(client, meal, model=None):
    """Evaluate a single meal record against real-world recipes."""
    recipe_json = json.dumps(meal, indent=2)
    prompt = GROUNDING_PROMPT_TEMPLATE.format(recipe_json=recipe_json)

    response = client.chat.completions.create(
        model=model or DEFAULT_MODEL,
        max_tokens=4096,
        messages=[
            {"role": "system", "content": GROUNDING_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )

    text = response.choices[0].message.content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    return json.loads(text)


def validate_grounding_result(result):
    """Basic validation that the grounding result has expected fields."""
    required = [
        "ingredient_score", "proportion_score", "technique_score",
        "time_score", "safety_score", "cultural_score",
        "overall_confidence", "verdict",
    ]
    for field in required:
        if field not in result:
            return False, f"Missing field: {field}"

    for field in required[:-1]:
        val = result[field]
        if not isinstance(val, (int, float)) or val < 0 or val > 1:
            return False, f"{field} must be a number between 0 and 1, got {val}"

    if result["verdict"] not in ("pass", "needs_review", "fail"):
        return False, f"Invalid verdict: {result['verdict']}"

    return True, None


def load_meals(input_path):
    """Load meals from a batch file or directory of batch files."""
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


def ground_batch(client, meals, dry_run=False):
    """Ground a batch of meals, returning results with grounding metadata."""
    results = []
    stats = {"pass": 0, "needs_review": 0, "fail": 0, "error": 0}

    for i, (source_file, meal) in enumerate(meals):
        name = meal.get("name", f"Meal {i + 1}")
        print(f"\n[{i + 1}/{len(meals)}] Grounding: {name}")

        if dry_run:
            print(f"  [DRY RUN] Would evaluate against real-world recipes")
            grounded = {
                **meal,
                "grounding": {
                    "status": "dry_run",
                    "source_file": source_file,
                },
            }
            results.append(grounded)
            continue

        try:
            evaluation = ground_meal(client, meal)
            valid, error = validate_grounding_result(evaluation)

            if not valid:
                print(f"  [ERROR] Invalid grounding result: {error}", file=sys.stderr)
                stats["error"] += 1
                grounded = {
                    **meal,
                    "grounding": {
                        "status": "error",
                        "error": error,
                        "source_file": source_file,
                    },
                }
            else:
                verdict = evaluation["verdict"]
                confidence = evaluation["overall_confidence"]
                stats[verdict] += 1

                icon = {"pass": "OK", "needs_review": "REVIEW", "fail": "FAIL"}[verdict]
                print(f"  [{icon}] confidence={confidence:.2f} verdict={verdict}")

                if evaluation.get("suggested_fixes"):
                    for fix in evaluation["suggested_fixes"]:
                        print(f"    - {fix}")

                grounded = {
                    **meal,
                    "grounding": {
                        "status": verdict,
                        "confidence": confidence,
                        "scores": {
                            "ingredient": evaluation["ingredient_score"],
                            "proportion": evaluation["proportion_score"],
                            "technique": evaluation["technique_score"],
                            "time": evaluation["time_score"],
                            "safety": evaluation["safety_score"],
                            "cultural": evaluation["cultural_score"],
                        },
                        "issues": {
                            k: evaluation.get(f"{k}_issues", [])
                            for k in ["ingredient", "proportion", "technique", "time", "safety", "cultural"]
                            if evaluation.get(f"{k}_issues")
                        },
                        "real_world_references": evaluation.get("real_world_references", []),
                        "suggested_fixes": evaluation.get("suggested_fixes", []),
                        "source_file": source_file,
                    },
                }

            results.append(grounded)
            time.sleep(0.5)

        except (json.JSONDecodeError, KeyError) as e:
            print(f"  [ERROR] {e}", file=sys.stderr)
            stats["error"] += 1
            results.append({
                **meal,
                "grounding": {
                    "status": "error",
                    "error": str(e),
                    "source_file": source_file,
                },
            })

    return results, stats


def save_results(results, stats, label):
    """Save grounded results to output directory."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"grounded_{label}_{timestamp}.json"
    path = OUTPUT_DIR / filename

    output = {
        "grounded_at": datetime.now(timezone.utc).isoformat(),
        "total": len(results),
        "stats": stats,
        "meals": results,
    }

    with open(path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved {len(results)} grounded meals to {path}")
    return path


def print_summary(stats, total):
    """Print a summary of grounding results."""
    print(f"\n{'=' * 50}")
    print(f"GROUNDING SUMMARY")
    print(f"{'=' * 50}")
    print(f"Total meals:    {total}")
    print(f"  Passed:       {stats['pass']}")
    print(f"  Needs review: {stats['needs_review']}")
    print(f"  Failed:       {stats['fail']}")
    print(f"  Errors:       {stats['error']}")
    pass_rate = (stats["pass"] / total * 100) if total > 0 else 0
    print(f"  Pass rate:    {pass_rate:.0f}%")
    print(f"{'=' * 50}")


def main():
    parser = argparse.ArgumentParser(description="Ground generated meals against real recipes")
    parser.add_argument("--input", type=str, required=True, help="Path to meal batch file or directory")
    parser.add_argument("--all", action="store_true", help="Process all JSON files in directory")
    parser.add_argument("--dry-run", action="store_true", help="Skip API calls, show what would be processed")
    parser.add_argument("--limit", type=int, help="Max number of meals to process")
    args = parser.parse_args()

    if not args.dry_run:
        api_key = os.environ.get("TOGETHER_API_KEY")
        if not api_key:
            print("Error: TOGETHER_API_KEY environment variable not set", file=sys.stderr)
            sys.exit(1)
        client = OpenAI(api_key=api_key, base_url="https://api.together.xyz/v1")
    else:
        client = None

    meals = load_meals(args.input)

    if not meals:
        print("No meals found in input", file=sys.stderr)
        sys.exit(1)

    if args.limit:
        meals = meals[:args.limit]

    print(f"Found {len(meals)} meals to ground")

    results, stats = ground_batch(client, meals, dry_run=args.dry_run)

    label = Path(args.input).stem if not Path(args.input).is_dir() else "batch"
    save_results(results, stats, label)
    print_summary(stats, len(results))


if __name__ == "__main__":
    main()
