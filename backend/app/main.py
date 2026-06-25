from __future__ import annotations

import asyncio
import json
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse

from .domain import ApprovalRequest, ConversationTurn, InquiryRequest, RunResponse
from .evaluation import EVALUATION_DASHBOARD
from .memory import add_turn, get_conversation, summarize_context, conversation_count
from .observability import metrics, record_run_status, record_trace
from .workflow import OUTPUT_DIR, get_state, resume_run, start_run


app = FastAPI(title="RealEstate AutoAgent", version="0.1.0",
              description="Observable, human-governed investment proposal automation")


def serialize(run_id: str, state: dict) -> RunResponse:
    status = state.get("status", "pending_approval")
    pdf_url = f"/v1/runs/{run_id}/proposal.pdf" if status == "completed" else None
    return RunResponse(run_id=run_id, status=status, conversation_id=state.get("conversation_id"),
                       lead=state.get("lead"), qualification=state.get("qualification"), compliance=state.get("compliance"),
                       recommendations=state.get("recommendations", []), trace=state.get("trace", []),
                       approval_url=f"/v1/runs/{run_id}/approval" if status == "pending_approval" else None,
                       pdf_url=pdf_url)


@app.get("/healthz")
def health() -> dict:
    return {"status": "ok", "service": "real-estate-autoagent"}


@app.post("/v1/proposals", response_model=RunResponse, status_code=202)
def create_proposal(body: InquiryRequest) -> RunResponse:
    run_id = uuid4().hex[:12]
    conversation_id = body.conversation_id or run_id
    add_turn(conversation_id, "buyer", body.inquiry, run_id)
    result = start_run(run_id, body.inquiry, body.require_approval, conversation_id, summarize_context(conversation_id))
    state = get_state(run_id)
    if result.get("__interrupt__"):
        state["status"] = "pending_approval"
    response = serialize(run_id, state)
    add_turn(conversation_id, "assistant", f"Created {response.status} proposal run with {len(response.recommendations)} recommendations.", run_id)
    record_run_status(response.status)
    record_trace(state.get("trace", []))
    return response


@app.get("/v1/runs/{run_id}", response_model=RunResponse)
def read_run(run_id: str) -> RunResponse:
    state = get_state(run_id)
    if not state:
        raise HTTPException(404, "Run not found")
    return serialize(run_id, state)


@app.post("/v1/runs/{run_id}/approval", response_model=RunResponse)
def approve_run(run_id: str, body: ApprovalRequest) -> RunResponse:
    if not get_state(run_id):
        raise HTTPException(404, "Run not found")
    resume_run(run_id, body.model_dump())
    state = get_state(run_id)
    response = serialize(run_id, state)
    if response.conversation_id:
        add_turn(response.conversation_id, "advisor", f"Approval decision by {body.reviewer}: {body.approved}.", run_id)
    record_run_status(response.status)
    record_trace(state.get("trace", []))
    return response


@app.get("/v1/conversations/{conversation_id}", response_model=list[ConversationTurn])
def read_conversation(conversation_id: str) -> list[ConversationTurn]:
    return get_conversation(conversation_id)


@app.get("/v1/observability/metrics")
def read_metrics() -> dict:
    data = metrics()
    data["conversation_count"] = conversation_count()
    return data


@app.get("/v1/evaluations/dashboard")
def evaluation_dashboard() -> dict:
    return EVALUATION_DASHBOARD


@app.get("/v1/runs/{run_id}/proposal.pdf")
def download_pdf(run_id: str) -> FileResponse:
    state = get_state(run_id)
    path = state.get("pdf_path") if state else None
    if not path:
        raise HTTPException(409, "Proposal has not been approved and generated")
    return FileResponse(path, media_type="application/pdf", filename=f"PSI-proposal-{run_id}.pdf")


@app.get("/v1/runs/{run_id}/events")
async def stream_events(run_id: str, request: Request) -> StreamingResponse:
    if not get_state(run_id):
        raise HTTPException(404, "Run not found")
    async def events():
        sent = 0
        for _ in range(60):
            if await request.is_disconnected(): return
            state = get_state(run_id)
            trace = state.get("trace", [])
            while sent < len(trace):
                yield f"event: agent_trace\ndata: {json.dumps(trace[sent])}\n\n"
                sent += 1
            yield f"event: status\ndata: {json.dumps({'status': state.get('status')})}\n\n"
            if state.get("status") in {"completed", "rejected"}: return
            await asyncio.sleep(1)
    return StreamingResponse(events(), media_type="text/event-stream")
