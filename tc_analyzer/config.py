"""Shared constants."""

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 2000
TEMPERATURE = 0  # triage tool, we want reproducible output not creative

# Confidence scale: LOW (0) = least confident / riskiest, HIGH (2) = most confident / lowest risk.
# Clamp keeps the lowest rank (never inflates); reconsideration keeps the higher rank (only real gains raise it).
CONFIDENCE_RANK = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}

LEGAL_FOOTER = (
    "This output is a draft for human legal review only. "
    "It has no legal validity until validated by a qualified lawyer."
)
