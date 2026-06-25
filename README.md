# RealEstate AutoAgent

**AI Assistant for UAE Property Search, Valuation, and Lead Qualification**

An AI-powered real estate assistant designed for UAE property workflows. It supports property search, buyer qualification, multilingual conversations, valuation guidance, proposal generation, and broker handoff.

Built with Python, FastAPI, LangGraph agents, structured tool-style orchestration, local RAG-style ranking, PDF generation, and evaluation-first agent design.

## Why this project matters

Real estate agents often spend 45-90 minutes turning one raw buyer message into a useful investment proposal: reading the inquiry, qualifying intent, searching listings, checking prices, estimating ROI, writing the proposal, and preparing a PDF.

RealEstate AutoAgent compresses that workflow into an auditable backend pipeline with a human approval gate before client-facing output.

## Agent workflow

```text
Buyer Inquiry
  -> Buyer Agent / Lead Parser
  -> Property Search Agent
  -> Valuation Agent
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
- Multilingual-aware parsing for Arabic/English-style WhatsApp leads.
- Property matching against `data/psi_listings.json`.
- AVM-style market value, yield, cash flow, and risk flag calculation.
- Area context and investment rationale.
- Human approval gate before PDF generation.
- Safe observability traces for each agent step.
- Client-ready PDF proposal output.
- Evaluation tests for parsing, rejection, approval, and data loading.

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
- three ranked recommendations from the connected listing inventory
- yield, cash-flow, and risk calculations
- area rationale and nearby landmarks
- safe agent trace events
- `status: pending_approval`
- `approval_url`

Approve the run with `POST /v1/runs/{run_id}/approval`:

```json
{
  "approved": true,
  "reviewer": "Demo Agent",
  "note": "Approved after reviewing budget fit, area match, and ROI."
}
```

The completed response returns a `pdf_url` for the generated investment proposal.

## Test

```powershell
python -m pytest -v
```


- AVM timeout and circuit-breaker policies
