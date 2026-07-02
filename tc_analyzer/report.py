"""Prints the pipeline result as a plain-text report for the legal team.
Warnings and the recommendation are derived in code, not by the model."""

from .config import LEGAL_FOOTER
from .confidence import is_material, prioritise_flags


def print_report(result: dict) -> None:
    print(f"\n=== T&C adaptation: {result['source_country']} -> {result['target_country']} ===")

    if not result["impacted"]:
        print("Status: NOT IMPACTED - no adaptation required.")
        print(result["reasoning"])
        print(LEGAL_FOOTER)
        return

    flags = prioritise_flags(result["uncertainty_flags"])
    n_material = sum(1 for f in flags if is_material(f))

    print(f"Status: IMPACTED - overall confidence: {result['confidence']}")
    for warning in build_warnings(result["confidence"], n_material):
        print(f"! {warning}")

    print(f"\nOriginal clause:\n  {result['original_clause']}")
    print(f"\nProposed clause:\n  {result['proposed_clause']}")

    print(f"\nPoints requiring legal validation ({len(flags)}, {n_material} material):")
    for i, flag in enumerate(flags, start=1):
        tag = f"{flag['confidence']}, material" if is_material(flag) else flag["confidence"]
        print(f"  {i}. [{tag}] {flag['point']}")

    print(f"\nRecommendation: {build_recommendation(result['confidence'], result['target_country'], n_material)}")
    print(f"\n{LEGAL_FOOTER}")


def build_warnings(confidence: str, n_material: int) -> list:
    """Mandatory warnings, enforced in code so they don't depend on the model remembering them."""
    warnings = []
    if confidence == "LOW":
        warnings.append("Mandatory review by a local legal expert required before any use.")
    if n_material > 3:
        warnings.append("More than three material points of uncertainty - do not use without a full legal review.")
    return warnings


def build_recommendation(confidence: str, target: str, n_material: int) -> str:
    """Recommendation from the confidence level and the material-flag count."""
    if confidence == "LOW" or n_material > 3:
        return f"Do not publish as drafted. A {target}-qualified lawyer must validate every point above first."
    if confidence == "MEDIUM":
        return f"A {target}-qualified lawyer must confirm the points above before publication."
    return f"Low-risk. A light-touch check by {target} counsel on the points above is enough."
