# PSI AutoAgent

An interview-ready, production-shaped MVP that turns a raw UAE property inquiry into an approved investment proposal PDF.

## What makes the demo enterprise-grade

- **LangGraph orchestration:** five bounded agents with typed shared state.
- **Human approval gate:** execution is checkpointed before document generation and resumes after approval or rejection.
- **Safe observability:** the API and SSE feed expose agent, duration, confidence and decision summaries—not private chain-of-thought.
- **UAE-aware parsing:** handles mixed Arabic/English, `3BHK`, `1.5M`, chiller-free and payment-plan language.
- **Investment math:** market-value comparison, gross/net yield, annual cash flow and risk flags.
- **Executive PDF:** PSI-style slate/gold layout with scannable cards and a commercial disclaimer.
- **Reliable demo mode:** runs locally without an LLM key. The matcher uses deterministic semantic token vectors; a Chroma adapter can replace it without changing graph state.

> ChromaDB's native `hnswlib` dependency does not ship a compatible wheel for this machine's Python 3.12 setup. The MVP therefore uses the same vector-ranking boundary with a deterministic local backend. For deployment, enable the `chroma` extra in a Python 3.11 container.

## Run

```powershell
cd "C:\Users\lahar\Documents\New project\psi-autoagent"
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## Best live-demo flow

1. POST `/v1/proposals` with:

```json
{
  "inquiry": "مرحبا, I am looking for a 3BHK on Al Reem Island. My budget is 1.5M. Ready to move in. Shukran.",
  "require_approval": true
}
```

2. Point out the normalized lead, three ranked recommendations and four audit trace events.
3. Show that status is `pending_approval` and no PDF exists yet.
4. POST the returned `approval_url` with `{"approved":true,"reviewer":"Lahari"}`.
5. Open the returned `pdf_url` and highlight net yield, risk flags and the disclaimer.
6. Run `python scripts/demo_batch.py` to produce three contrasting proposals.

## Test

```powershell
python -m pytest -q
```

## Production evolution

Swap the deterministic parser for a strict structured-output LLM, the matcher for Chroma/OpenSearch, `MemorySaver` for a durable Postgres checkpointer, and the curated area context for approved data providers. Add OAuth/RBAC, tenant isolation, signed object-storage URLs, PII redaction, prompt/version registry, AVM timeouts/circuit breakers and OpenTelemetry export before external launch.

