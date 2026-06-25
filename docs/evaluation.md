# Evaluation Layer

The project includes a lightweight but real evaluation system for agent quality.

## Golden dataset

`evals/golden_inquiries.json` contains representative buyer inquiries with expected:

- target area
- bedroom count
- budget
- language
- purpose
- required agent sequence

## Regression scoring

`backend/app/evaluator.py` runs each golden case through the same LangGraph workflow used by the API.

It reports:

- extraction score
- hallucination/groundedness score
- tool-selection accuracy
- overall score

## Groundedness

The groundedness scorer verifies that:

- all recommendations come from `data/psi_listings.json`
- area rationale is present
- compliance disclaimers are present
- proposal text does not use guaranteed-return language

## Tool-selection accuracy

The tool-selection scorer verifies that the expected agent sequence ran:

```text
Lead Parser
Lead Qualification Agent
Property Matcher
AVM Pricer
Mortgage & Affordability Agent
Area Researcher
RERA / Compliance Agent
```

## API

```text
GET /v1/evaluations/dashboard
POST /v1/evaluations/run
```
