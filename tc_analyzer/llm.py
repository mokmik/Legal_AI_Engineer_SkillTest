"""Anthropic client wrapper: call an agent with the Pydantic schema forced as a tool, so required fields can't be dropped."""

import logging
from typing import Literal, Type, TypeVar

from anthropic import Anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

from .config import MAX_TOKENS, MODEL, TEMPERATURE

load_dotenv()
client = Anthropic()  # reads ANTHROPIC_API_KEY from the environment

T = TypeVar("T", bound=BaseModel)


class UncertaintyFlag(BaseModel):
    point: str
    explanation: str
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    material: bool = True


class ImpactResult(BaseModel):
    impacted: bool
    impact_reasoning: str


class AdaptationResult(BaseModel):
    proposed_clause: str
    reasoning: str
    overall_confidence: Literal["HIGH", "MEDIUM", "LOW"]
    uncertainty_flags: list[UncertaintyFlag] = []


class AgentError(Exception):
    """Raised when an agent's output cannot be used (no structured output or a schema mismatch)."""


def call_agent(step: str, system_prompt: str, user_content: str, schema: Type[T]) -> T:
    """Call one agent and return its output validated against `schema`, or raise AgentError."""
    logging.info(f"[{step}] Calling model...")
    # Force the model to answer through a tool whose schema is `schema`, so the API requires every field.
    tool = {
        "name": "record_result",
        "description": f"Record the result as a {schema.__name__}.",
        "input_schema": schema.model_json_schema(),
    }
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
            tools=[tool],
            tool_choice={"type": "tool", "name": "record_result"},
        )
    except Exception as exc:
        raise AgentError(f"{step}: the language model call failed ({exc}).") from exc

    tool_use = next(
        (block for block in response.content if block.type == "tool_use"), None
    )
    if tool_use is None:
        raise AgentError(f"{step}: the model returned no structured output.")

    # Backstop: the API forces the shape, but we still validate so a bad enum value fails loudly, never silently.
    try:
        validated = schema.model_validate(tool_use.input)
    except ValidationError as exc:
        raise AgentError(
            f"{step}: the model's structured output did not match the expected {schema.__name__} shape ({exc})."
        ) from exc

    logging.info(f"[{step}] Received a valid {schema.__name__}.")
    return validated
