"""Two-agent orchestration. Guardrails live in code here, not in the prompts."""

import logging

from .confidence import clamp_confidence
from .config import CONFIDENCE_RANK
from .llm import AdaptationResult, ImpactResult, call_agent
from .prompts import AGENT1_SYSTEM_PROMPT, AGENT2_SYSTEM_PROMPT

# Appended to Agent 2's input for the single reconsideration pass when the first clamp is LOW.
AGENT2_RECONSIDER_ADDENDUM = """\
Agent 2 returned LOW confidence on the first pass.
Please reconsider your adaptation with this in mind:
- Focus specifically on the material flags you identified
- If your assessment remains LOW, explain precisely why local law cannot be worked around
- If you can raise confidence to MEDIUM with targeted changes to the proposed clause, do so"""


def _adapt(step: str, agent2_input: str):
    """Run Agent 2 once; return (result, flags-as-dicts, clamped_confidence)."""
    agent2 = call_agent(step, AGENT2_SYSTEM_PROMPT, agent2_input, AdaptationResult)
    flags = [flag.model_dump() for flag in agent2.uncertainty_flags]
    clamped = clamp_confidence(agent2.overall_confidence, flags)
    if clamped != agent2.overall_confidence:
        logging.info(f"[{step}] Overall confidence clamped from {agent2.overall_confidence} to {clamped} (lowest material flag).")
    return agent2, flags, clamped


def run_pipeline(clause: str, change: str, source_country: str, target_country: str) -> dict:
    """Run the two agents, apply the guardrails, and return a structured result dict."""
    logging.info(f"[PIPELINE] Started: adapting a clause from {source_country} to {target_country}.")

    result = {
        "impacted": None,
        "original_clause": clause,
        "proposed_clause": None,
        "confidence": None,
        "uncertainty_flags": [],
        "reasoning": None,
        "source_country": source_country,
        "target_country": target_country,
    }

    # Agent 1: impact detection
    agent1_input = (
        f"SOURCE COUNTRY: {source_country}\n"
        f"TARGET COUNTRY: {target_country}\n\n"
        f"T&C CLAUSE:\n{clause}\n\n"
        f"CHANGE DESCRIPTION:\n{change}"
    )
    agent1 = call_agent("AGENT 1 - Impact Detector", AGENT1_SYSTEM_PROMPT, agent1_input, ImpactResult)
    result["impacted"] = agent1.impacted
    result["reasoning"] = agent1.impact_reasoning

    # not impacted: stop before Agent 2, no point spending tokens on an adaptation we don't need
    if not agent1.impacted:
        logging.info("[PIPELINE] Agent 1 returned impacted=false -> stopping early. Agent 2 NOT called.")
        result["confidence"] = "N/A"
        return result

    logging.info("[PIPELINE] Agent 1 returned impacted=true -> proceeding to Agent 2.")

    # Agent 2: adaptation
    agent2_input = (
        f"SOURCE COUNTRY: {source_country}\n"
        f"TARGET COUNTRY: {target_country}\n\n"
        f"ORIGINAL T&C CLAUSE:\n{clause}\n\n"
        f"CHANGE DESCRIPTION:\n{change}\n\n"
        f"Agent 1 confirmed this clause IS impacted, with this reasoning:\n"
        f"{result['reasoning']}"
    )
    agent2, flags, clamped = _adapt("AGENT 2 - Legal Adapter", agent2_input)

    # a LOW clamp buys exactly one reconsideration pass; keep whichever pass clamps higher
    if clamped == "LOW":
        logging.info("[PIPELINE] Agent 2 clamped to LOW -> running one reconsideration pass.")
        retry_input = f"{agent2_input}\n\n{AGENT2_RECONSIDER_ADDENDUM}"
        retry, retry_flags, retry_clamped = _adapt("AGENT 2 - Legal Adapter (reconsider)", retry_input)
        logging.info(f"[PIPELINE] Reconsideration returned {retry_clamped} (first pass was {clamped}).")
        if CONFIDENCE_RANK[retry_clamped] > CONFIDENCE_RANK[clamped]:
            agent2, flags, clamped = retry, retry_flags, retry_clamped
            logging.info("[PIPELINE] Using the reconsideration pass (higher confidence).")
        else:
            logging.info("[PIPELINE] Keeping the first pass (reconsideration did not improve confidence).")

    result["proposed_clause"] = agent2.proposed_clause
    result["reasoning"] = agent2.reasoning
    result["uncertainty_flags"] = flags
    result["confidence"] = clamped

    logging.info(f"[PIPELINE] Agent 2 returned overall confidence={clamped} with {len(flags)} uncertainty flag(s).")
    logging.info("[PIPELINE] Completed successfully.")
    return result
