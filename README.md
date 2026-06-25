# RealEstate AutoAgent

**AI Assistant for UAE Property Search, Valuation, Affordability, and Lead Qualification**

An AI-powered real estate assistant designed for UAE property workflows. It supports property search, buyer qualification, multilingual conversations, valuation guidance, mortgage affordability estimates, proposal generation, and broker handoff.

Built with Python, FastAPI, LangGraph agents, structured tool-style orchestration, local RAG-style ranking, PDF generation, and evaluation-first agent design.

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
  -> Area / Compliance Context Agent
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
- Multilingual-aware parsing for Arabic/English-style WhatsApp leads.
- Property matching against `data/psi_listings.json`.
- AVM-style market value, yield, cash flow, and risk flag calculation.
- Mortgage affordability estimates with down payment, loan amount, monthly payment, and income requirement.
- Area context and investment rationale.
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

## Test

```powershell
python -m pytest -v
```

## Interview positioning

This repository is an MVP focused on the core property recommendation workflow. It currently implements lead parsing, CRM lead qualification, property matching, valuation, mortgage affordability estimates, area intelligence, human approval, and proposal generation.

The architecture is intentionally modular so additional production agents, such as RERA/compliance guidance, Redis conversation memory, production observability, and evaluation dashboards, can be added without changing the orchestration layer.

## Evaluation status

The repository includes API and workflow tests as the foundation of an evaluation framework. Production-grade agent evaluation, including golden datasets, LLM-as-judge checks, regression tracking, latency metrics, and cost dashboards, is planned for the next iteration.

## Production evolution

This MVP uses LangGraph `MemorySaver`, so run state is in memory. In production, replace it with a durable checkpoint store such as Postgres or Redis so approvals survive restarts.

Recommended production upgrades:

- ChromaDB, OpenSearch, or pgvector for production-scale semantic search
- durable LangGraph checkpointing
- RERA/compliance guidance agent
- Redis conversation memory
- OpenTelemetry or Langfuse observability
- full evaluation framework with golden datasets, LLM-as-judge checks, regression tracking, latency dashboards, and cost metrics
- OAuth/RBAC
- tenant isolation
- signed object-storage URLs for PDFs
- PII redaction
- prompt/version registry
- AVM timeout and circuit-breaker policies
