# RealEstate AutoAgent

**AI Assistant for UAE Property Search, Valuation, Affordability, and Lead Qualification**

An AI-powered real estate assistant designed for UAE property workflows. It supports property search, buyer qualification, multilingual conversations, valuation guidance, mortgage affordability estimates, proposal generation, and broker handoff.

Built with Python, FastAPI, LangGraph agents, structured tool-style orchestration, local RAG-style ranking, conversation memory, observability endpoints, PDF generation, and evaluation-first agent design.

## Why this project matters

Real estate agents often spend 45-90 minutes turning one raw buyer message into a useful investment proposal: reading the inquiry, qualifying intent, searching listings, checking prices, estimating ROI, checking affordability, writing the proposal, and preparing a PDF.

RealEstate AutoAgent compresses that workflow into an auditable backend pipeline with a human approval gate before client-facing output.

## Agent workflow

```text
Buyer Inquiry
  -> Buyer Agent / Lead Parser
  -> Lead Qualification Agent
  -> Property Search Agent
  -> Valuation Agent
  -> Mortgage & Affordability Agent
  -> Area Intelligence Agent
  -> RERA / Compliance Agent
  -> Broker Handoff Approval Gate
  -> Proposal Writer
  -> JSON response + PDF proposal
```

## Repository structure

```text
backend/        FastAPI app, LangGraph workflow, domain models, proposal builder
agents/         Agent responsibility and orchestration notes
data/           UAE/PSI-style property listing inventory
evals/          API and workflow regression tests
docs/           Demo script and interview notes
frontend/       Placeholder for future broker-facing UI
artifacts/      Generated proposal PDFs, ignored except .gitkeep
scripts/        Local demo utilities
```

## Enterprise-grade features

- LangGraph state-machine orchestration.
- Buyer qualification from raw inquiry text.
- CRM-ready lead score, stage, handoff summary, and next-best action.
- Multilingual-aware parsing for English, Arabic, Hindi, and mixed-language WhatsApp leads.
- Property matching against `data/psi_listings.json`.
- AVM-style market value, yield, cash flow, and risk flag calculation.
- Mortgage affordability estimates with down payment, loan amount, monthly payment, and income requirement.
- Area context and investment rationale.
- UAE/RERA-style compliance checklist and disclaimer generation.
- Conversation memory via `conversation_id` and `/v1/conversations/{conversation_id}`.
- Observability metrics via `/v1/observability/metrics`.
- Evaluation dashboard via `/v1/evaluations/dashboard`.
- Golden dataset quality suite via `/v1/evaluations/run`.
- Groundedness checks to confirm recommendations are sourced from inventory.
- Tool-selection accuracy scoring for the LangGraph agent sequence.
- Human approval gate before PDF generation.
- Safe observability traces for each agent step.
- Client-ready PDF proposal output.
- API and workflow tests as the foundation of an evaluation framework.

## Tech stack

- Python
- FastAPI
- LangGraph
- Pydantic
- ReportLab
- Pytest
- Docker / Docker Compose

## Run locally

```powershell
git clone https://github.com/Lahari99-cloud/RealEstate--Autoagent.git
cd RealEstate--Autoagent
python -m pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/healthz
```

## Run with Docker

```powershell
docker compose up --build
```

Then open `http://127.0.0.1:8000/docs`.

## Demo request

Use `POST /v1/proposals`:

```json
{
  "inquiry": "Looking for a 2 bedroom investment on Yas Island under AED 1.8M with good ROI",
  "conversation_id": "demo-buyer-1",
  "require_approval": true
}
```

The response should show:

- parsed budget, bedrooms, area, purpose, language, and timeline
- CRM lead score and broker handoff guidance
- three ranked recommendations from the connected listing inventory
- yield, cash-flow, and risk calculations
- mortgage affordability and income requirement estimates
- area rationale and nearby landmarks
- compliance checklist and risk level
- safe agent trace events
- `status: pending_approval`
- `approval_url`

Approve the run with `POST /v1/runs/{run_id}/approval`:

```json
{
  "approved": true,
  "reviewer": "Demo Agent",
  "note": "Approved after reviewing budget fit, area match, affordability, and ROI."
}
```

The completed response returns a `pdf_url` for the generated investment proposal.

Useful production-readiness endpoints:

```text
GET /v1/conversations/{conversation_id}
GET /v1/observability/metrics
GET /v1/evaluations/dashboard
POST /v1/evaluations/run
```

## Test

```powershell
python -m pytest -v
```
## Evaluation layer

The repository includes a concrete evaluation foundation:

- `evals/golden_inquiries.json` stores golden buyer inquiries and expected outputs.
- `backend/app/evaluator.py` runs regression scoring against the real workflow.
- extraction scoring checks area, bedrooms, budget, language, and purpose.
- groundedness scoring checks that recommendations come from the connected inventory and include compliance disclaimers.
- tool-selection scoring checks that required agents ran in the expected order.
- `POST /v1/evaluations/run` returns a suite report with overall, extraction, groundedness, and tool-selection scores.

Production-grade extensions such as LLM-as-judge review, historical trend tracking, CI quality gates, latency metrics, and cost dashboards are planned for the next iteration.


