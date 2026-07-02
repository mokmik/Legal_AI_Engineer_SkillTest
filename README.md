# T&C Cross-Border Impact Analyzer

A prototype for a legal team's cross-border Terms & Conditions change-management workflow.

## What it does

Given a T&C clause, a change description, and a source/target country, it:

1. **Impact Detector (LLM)** decides whether the clause is affected by the change.
2. **Legal Adapter (LLM)** proposes an adapted clause for the target country and flags every point of local legal uncertainty, each with a confidence level.
3. **Report builder (code)** prioritises the flags, writes a recommendation, and renders a lawyer-readable report (original vs proposed clause, points to validate).

## Riskiest assumption

Can an LLM reliably flag where its own cross-border adaptation is uncertain and needs a human expert, rather than producing something that reads correctly but is wrong in the target jurisdiction? A confident-but-wrong clause is the failure mode that matters, so the design favours surfacing uncertainty over a polished answer.

## Evaluation

The built-in cases (`tc_analyzer/cases.py`) span the EU instrument types. I expected confidence to track the instrument (Regulation → HIGH, Directive → MEDIUM, national law → LOW). Running them **partially refutes** that: for consumer-facing fintech clauses the model surfaces material national-law points on almost every clause, so confidence often lands lower than predicted. See `sample_output.txt` for a captured run.

## Trade-offs

- **No regulatory knowledge base.** Populating one correctly needs a legal domain expert, not an engineer working alone; hardcoding a handful of rules would be worse than not building it, because it would look authoritative while being wrong. The system leans on the model's knowledge and, crucially, on flagging where that knowledge is uncertain.
- **Two agents, not three.** The report, prioritising flags, warnings, recommendation, is deterministic, so it lives in code where it is auditable and can't hallucinate, rather than in a third LLM call.
- **Adapted clause in the target country's language.** The proposed clause is written in the target country's official language (so the German cases come out in German, etc.), on the assumption that the market's Terms & Conditions will most likely need to be in that language. This is a deliberate choice rather than keeping the source language. A more advanced version would add a dedicated translation module/agent so the lawyer gets both the source-language reasoning and a clean localised clause, with translation treated as its own reviewable step.
- **LOW-confidence feedback loop.** When Agent 2's clamped confidence is LOW, it gets one reconsideration pass focused on its material flags; the higher-confidence pass wins. It is capped at one retry so cost and latency stay bounded and it can never loop.
- **Time spent:** approximately 2 hours.

## How to run

```
pip install -r requirements.txt
python tc_impact_analyzer.py        # runs 4 built-in test cases
```

The script needs an Anthropic API key: copy `.env.example` to `.env` and add yours.

Just run the script: it writes the lawyer-facing reports to `output.txt` (one compact report per case: impact decision, original vs proposed clause, the points to validate, and the recommendation), while the audit trace streams to the terminal so the file stays clean and readable. Nothing else to do. The committed `sample_output.txt` is one representative run kept in the repo.

## Layout

```
tc_impact_analyzer.py   entry point (runs the eval cases)
tc_analyzer/
  config.py             constants (model, token budget, temperature, confidence order)
  prompts.py            the two agent system prompts
  llm.py                Anthropic client + Pydantic-validated agent output
  confidence.py         materiality, confidence clamp, flag prioritisation
  report.py             lawyer-readable rendering, warnings, recommendation
  pipeline.py           orchestration, code-enforced guardrails, audit logging
  cases.py              the built-in eval cases
```

## Scope

Model `claude-sonnet-4-6` at `temperature=0`; no UI, DB, or vector store. The model's legal knowledge is not authoritative; the output is always a draft for a human lawyer.
