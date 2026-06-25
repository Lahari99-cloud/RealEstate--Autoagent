# Real Estate AutoAgent

An interview-ready, production-shaped backend that turns a raw UAE property buyer inquiry into an approved investment proposal PDF.

The project demonstrates how a real estate company can compress a manual 45-90 minute agent workflow into an auditable, human-governed automation pipeline.

## What it does

```text
Raw buyer inquiry
  -> Lead Parser
  -> Property Matcher
  -> AVM Pricer
  -> Area Researcher
  -> Human Approval Gate
  -> Proposal Writer
  -> JSON response + PDF proposal
```

## Why it is enterprise-grade

- LangGraph orchestration with typed shared state.
- Human approval gate before client-facing PDF generation.
- Safe observability traces showing agent name, status, duration, confidence, and summaries.
- UAE-aware parsing for mixed Arabic/English, `3BHK`, `AED 1.8M`, and area names.
- Real listing inventory loaded from `data/psi_listings.json`.
- Investment calculations for estimated market value, gross yield, net yield, cash flow, and risk flags.
- Polished proposal PDF generated with ReportLab.
- Local demo mode that runs without an LLM key.

## Tech stack

- FastAPI
- LangGraph
- Pydantic
- ReportLab
- Pytest

## Run locally

```powershell
git clone https://github.com/Lahari99-cloud/RealEstate--Autoagent.git
cd RealEstate--Autoagent
python -m pip install -e ".[dev]"
python -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/healthz
```

## Demo request

Use `POST /v1/proposals` with:

```json
{
  "inquiry": "مرحبا, I am looking for a 3BHK on Al Reem Island. My budget is 1.5M. Ready to move in. Shukran.",
  "require_approval": true
}
```

Check that the response includes:

- parsed budget, bedrooms, area, language, and timeline
- three ranked property recommendations
- safe trace events from the parser, matcher, pricer, and researcher
- `status: pending_approval`
- an `approval_url`

Then approve the run with `POST /v1/runs/{run_id}/approval`:

```json
{
  "approved": true,
  "reviewer": "Demo Agent",
  "note": "Approved after reviewing budget fit, area match, and ROI."
}
```

The completed response returns a `pdf_url` for the generated proposal.

## Test

```powershell
python -m pytest -v
```

## Notes for production

This MVP uses LangGraph `MemorySaver`, so run state is in memory. In production, replace it with a durable checkpoint store such as Postgres or Redis so approvals survive restarts.

The matcher currently uses a deterministic local vector-style ranking boundary. ChromaDB or OpenSearch can be added behind the same matcher interface for production-scale semantic search.

Recommended production upgrades:

- persistent LangGraph checkpointing
- OAuth/RBAC
- tenant isolation
- signed object-storage URLs for PDFs
- PII redaction
- prompt/version registry
- OpenTelemetry tracing
- AVM timeout and circuit-breaker policies
