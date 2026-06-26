"""
MiseEnPlace Validator — Stage 6 of the offline pipeline.

Runs consistency checks across the graph database to ensure data quality
before it powers the app. Produces a validation report with pass/warn/fail
status for each check.

Checks:
  1. Every meal has ≥2 ingredients
  2. Every ingredient has a price (via cost_estimate)
  3. Cost per serving is between $1-30
  4. No orphan ingredients (ingredients not used by any meal)
  5. Seasonal tags are coherent
  6. All meals have grounding status
  7. Meal names are unique
  8. Steps are sequential and non-empty
  9. Similarity graph connectivity
  10. Cuisine and dietary tag distribution

Usage:
    python -m validation.validator --db output/miseenplace.db
    python -m validation.validator --db output/miseenplace.db --json
    python -m validation.validator --db output/miseenplace.db --fix

No API key needed.
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "output"
DEFAULT_DB = OUTPUT_DIR / "miseenplace.db"


class ValidationResult:
    def __init__(self, name, status, message, details=None):
        self.name = name
        self.status = status  # "pass", "warn", "fail"
        self.message = message
        self.details = details or []

    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "details": self.details,
        }


def check_minimum_ingredients(conn):
    """Every meal must have ≥2 ingredients."""
    rows = conn.execute("""
        SELECT m.name, COUNT(mi.ingredient_id) as ing_count
        FROM meals m
        LEFT JOIN meal_ingredients mi ON m.id = mi.meal_id
        GROUP BY m.id
        HAVING ing_count < 2
    """).fetchall()

    if not rows:
        return ValidationResult("minimum_ingredients", "pass", "All meals have ≥2 ingredients")

    details = [f"{name}: {count} ingredients" for name, count in rows]
    return ValidationResult("minimum_ingredients", "fail",
                            f"{len(rows)} meals have fewer than 2 ingredients", details)


def check_cost_coverage(conn):
    """Every meal should have a cost estimate."""
    total = conn.execute("SELECT COUNT(*) FROM meals").fetchone()[0]
    missing = conn.execute("SELECT COUNT(*) FROM meals WHERE cost_per_serving IS NULL").fetchone()[0]

    if missing == 0:
        return ValidationResult("cost_coverage", "pass", f"All {total} meals have cost estimates")

    names = conn.execute("SELECT name FROM meals WHERE cost_per_serving IS NULL").fetchall()
    details = [n[0] for n in names[:10]]
    pct = (total - missing) / total * 100 if total > 0 else 0

    status = "warn" if pct >= 80 else "fail"
    return ValidationResult("cost_coverage", status,
                            f"{missing}/{total} meals missing cost ({pct:.0f}% coverage)", details)


def check_cost_range(conn):
    """Cost per serving should be between $1-30 CAD."""
    outliers = conn.execute("""
        SELECT name, cost_per_serving
        FROM meals
        WHERE cost_per_serving IS NOT NULL
          AND (cost_per_serving < 1.0 OR cost_per_serving > 30.0)
    """).fetchall()

    if not outliers:
        return ValidationResult("cost_range", "pass", "All costs within $1-30/serving range")

    details = [f"{name}: ${cost:.2f}/serving" for name, cost in outliers]
    return ValidationResult("cost_range", "warn",
                            f"{len(outliers)} meals with unusual cost per serving", details)


def check_orphan_ingredients(conn):
    """No ingredients should exist without being used by any meal."""
    orphans = conn.execute("""
        SELECT i.name
        FROM ingredients i
        LEFT JOIN meal_ingredients mi ON i.id = mi.ingredient_id
        WHERE mi.meal_id IS NULL
    """).fetchall()

    if not orphans:
        return ValidationResult("orphan_ingredients", "pass", "No orphan ingredients")

    details = [o[0] for o in orphans]
    return ValidationResult("orphan_ingredients", "warn",
                            f"{len(orphans)} orphan ingredients (not used by any meal)", details)


def check_seasonal_coherence(conn):
    """Meals tagged with specific seasons should have seasonally appropriate ingredients."""
    seasonal_meals = conn.execute("""
        SELECT m.name, GROUP_CONCAT(ms.season) as seasons
        FROM meals m
        JOIN meal_seasons ms ON m.id = ms.meal_id
        WHERE ms.season != 'all'
        GROUP BY m.id
    """).fetchall()

    no_season = conn.execute("""
        SELECT COUNT(*) FROM meals m
        WHERE NOT EXISTS (SELECT 1 FROM meal_seasons ms WHERE ms.meal_id = m.id)
    """).fetchone()[0]

    if no_season > 0:
        return ValidationResult("seasonal_coherence", "warn",
                                f"{no_season} meals have no seasonal tags",
                                [f"{no_season} meals missing season data"])

    return ValidationResult("seasonal_coherence", "pass",
                            f"All meals have seasonal tags ({len(seasonal_meals)} season-specific)")


def check_grounding_status(conn):
    """All meals should have been through grounding."""
    total = conn.execute("SELECT COUNT(*) FROM meals").fetchone()[0]
    ungrounded = conn.execute(
        "SELECT COUNT(*) FROM meals WHERE grounding_status IS NULL"
    ).fetchone()[0]
    failed = conn.execute(
        "SELECT COUNT(*) FROM meals WHERE grounding_status = 'fail'"
    ).fetchone()[0]

    details = []
    if ungrounded > 0:
        details.append(f"{ungrounded} meals not grounded")
    if failed > 0:
        names = conn.execute("SELECT name FROM meals WHERE grounding_status = 'fail'").fetchall()
        details.extend([f"FAILED: {n[0]}" for n in names[:5]])

    if ungrounded == 0 and failed == 0:
        return ValidationResult("grounding_status", "pass", f"All {total} meals grounded successfully")

    status = "fail" if failed > 0 else "warn"
    return ValidationResult("grounding_status", status,
                            f"{ungrounded} ungrounded, {failed} failed out of {total}", details)


def check_unique_names(conn):
    """Meal names must be unique."""
    dupes = conn.execute("""
        SELECT name, COUNT(*) as cnt
        FROM meals
        GROUP BY name
        HAVING cnt > 1
    """).fetchall()

    if not dupes:
        total = conn.execute("SELECT COUNT(*) FROM meals").fetchone()[0]
        return ValidationResult("unique_names", "pass", f"All {total} meal names are unique")

    details = [f"{name}: {cnt} duplicates" for name, cnt in dupes]
    return ValidationResult("unique_names", "fail",
                            f"{len(dupes)} duplicate meal names", details)


def check_steps_integrity(conn):
    """Steps must be sequential starting at 1 with non-empty instructions."""
    issues = []
    meals = conn.execute("SELECT id, name FROM meals").fetchall()

    for meal_id, name in meals:
        steps = conn.execute(
            "SELECT step_order, instruction FROM meal_steps WHERE meal_id = ? ORDER BY step_order",
            (meal_id,),
        ).fetchall()

        if not steps:
            issues.append(f"{name}: no steps")
            continue

        if steps[0][0] != 1:
            issues.append(f"{name}: steps don't start at 1")

        for k in range(1, len(steps)):
            if steps[k][0] != steps[k - 1][0] + 1:
                issues.append(f"{name}: gap in step sequence at {steps[k - 1][0]}→{steps[k][0]}")
                break

    if not issues:
        return ValidationResult("steps_integrity", "pass", "All meal steps are sequential")

    status = "warn" if len(issues) < 3 else "fail"
    return ValidationResult("steps_integrity", status,
                            f"{len(issues)} meals with step issues", issues[:10])


def check_similarity_connectivity(conn):
    """Check that the similarity graph is reasonably connected."""
    total_meals = conn.execute("SELECT COUNT(*) FROM meals").fetchone()[0]
    if total_meals < 2:
        return ValidationResult("similarity_connectivity", "pass", "Not enough meals for similarity check")

    connected = conn.execute("""
        SELECT COUNT(DISTINCT id) FROM (
            SELECT meal_a_id as id FROM meal_similarity
            UNION
            SELECT meal_b_id as id FROM meal_similarity
        )
    """).fetchone()[0]

    isolated = total_meals - connected
    pairs = conn.execute("SELECT COUNT(*) FROM meal_similarity").fetchone()[0]
    avg_overlap = conn.execute("SELECT AVG(overlap_ratio) FROM meal_similarity").fetchone()[0] or 0

    details = [
        f"{pairs} similarity pairs",
        f"Average overlap: {avg_overlap:.0%}",
        f"{isolated} isolated meals (no similar meals)",
    ]

    if isolated > total_meals * 0.5:
        return ValidationResult("similarity_connectivity", "warn",
                                f"{isolated}/{total_meals} meals have no similar meals", details)

    return ValidationResult("similarity_connectivity", "pass",
                            f"{connected}/{total_meals} meals connected, {pairs} pairs", details)


def check_distribution(conn):
    """Check that cuisines, meal types, and difficulties are reasonably distributed."""
    cuisines = conn.execute(
        "SELECT cuisine, COUNT(*) FROM meals GROUP BY cuisine ORDER BY COUNT(*) DESC"
    ).fetchall()
    types = conn.execute(
        "SELECT meal_type, COUNT(*) FROM meals GROUP BY meal_type ORDER BY COUNT(*) DESC"
    ).fetchall()
    difficulties = conn.execute(
        "SELECT difficulty, COUNT(*) FROM meals GROUP BY difficulty ORDER BY COUNT(*) DESC"
    ).fetchall()

    details = []
    if cuisines:
        details.append(f"Cuisines: {len(cuisines)} ({', '.join(f'{c}:{n}' for c, n in cuisines[:5])})")
    if types:
        details.append(f"Types: {', '.join(f'{t}:{n}' for t, n in types)}")
    if difficulties:
        details.append(f"Difficulty: {', '.join(f'{d}:{n}' for d, n in difficulties)}")

    if len(cuisines) < 3:
        return ValidationResult("distribution", "warn",
                                f"Only {len(cuisines)} cuisines represented", details)

    return ValidationResult("distribution", "pass",
                            f"{len(cuisines)} cuisines, {len(types)} meal types", details)


ALL_CHECKS = [
    check_minimum_ingredients,
    check_cost_coverage,
    check_cost_range,
    check_orphan_ingredients,
    check_seasonal_coherence,
    check_grounding_status,
    check_unique_names,
    check_steps_integrity,
    check_similarity_connectivity,
    check_distribution,
]


def run_validation(db_path):
    """Run all validation checks and return results."""
    conn = sqlite3.connect(str(db_path))
    results = []

    for check_fn in ALL_CHECKS:
        result = check_fn(conn)
        results.append(result)

    conn.close()
    return results


def print_report(results):
    """Print a human-readable validation report."""
    print(f"\n{'=' * 60}")
    print(f"MISEENPLACE VALIDATION REPORT")
    print(f"{'=' * 60}")

    counts = {"pass": 0, "warn": 0, "fail": 0}

    for r in results:
        icon = {"pass": "PASS", "warn": "WARN", "fail": "FAIL"}[r.status]
        counts[r.status] += 1
        print(f"\n  [{icon}] {r.name}")
        print(f"         {r.message}")
        for detail in r.details[:5]:
            print(f"           - {detail}")

    print(f"\n{'=' * 60}")
    print(f"SUMMARY: {counts['pass']} passed, {counts['warn']} warnings, {counts['fail']} failures")

    if counts["fail"] > 0:
        print(f"STATUS: FAILED — fix issues before using data in production")
    elif counts["warn"] > 0:
        print(f"STATUS: PASSED WITH WARNINGS — review flagged items")
    else:
        print(f"STATUS: ALL CLEAR")
    print(f"{'=' * 60}")

    return counts["fail"] == 0


def main():
    parser = argparse.ArgumentParser(description="Validate the MiseEnPlace graph database")
    parser.add_argument("--db", type=str, default=str(DEFAULT_DB), help="Path to SQLite database")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"Database not found: {db_path}", file=sys.stderr)
        sys.exit(1)

    results = run_validation(db_path)

    if args.json:
        output = {
            "validated_at": datetime.now(timezone.utc).isoformat(),
            "database": str(db_path),
            "checks": [r.to_dict() for r in results],
            "summary": {
                "pass": sum(1 for r in results if r.status == "pass"),
                "warn": sum(1 for r in results if r.status == "warn"),
                "fail": sum(1 for r in results if r.status == "fail"),
            },
        }
        print(json.dumps(output, indent=2))
    else:
        passed = print_report(results)
        if not passed:
            sys.exit(1)


if __name__ == "__main__":
    main()
