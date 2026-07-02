"""Confidence and materiality logic (pure functions)."""

from .config import CONFIDENCE_RANK


def is_material(flag: dict) -> bool:
    # missing "material" defaults to True so unclassified flags still block
    return bool(flag.get("material", True))


def clamp_confidence(overall: str, flags: list) -> str:
    """Lower of the stated confidence and the lowest-confidence material flag."""
    rank = CONFIDENCE_RANK.get(overall.upper(), 0)
    for flag in flags:
        if not is_material(flag):
            continue
        flag_rank = CONFIDENCE_RANK.get(str(flag.get("confidence", "")).upper())
        if flag_rank is not None:
            rank = min(rank, flag_rank)
    return next(label for label, value in CONFIDENCE_RANK.items() if value == rank)


def prioritise_flags(flags: list) -> list:
    """Sort flags for display: least-confident first, material before non-material at the same level."""

    def sort_key(flag):
        confidence_rank = CONFIDENCE_RANK.get(
            str(flag.get("confidence", "")).upper(),
            -1,  # unknown confidence is treated as lowest rank
        )
        material_first = 0 if is_material(flag) else 1
        return (confidence_rank, material_first)

    return sorted(flags, key=sort_key)
