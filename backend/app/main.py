from __future__ import annotations

import asyncio
import json
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse

from .domain import ApprovalRequest, InquiryRequest, RunResponse
from .workflow import OUTPUT_DIR, get_state, resume_run, start_run


app = FastAPI(title="RealEstate AutoAgent", version="0.1.0",
              description="Observable, human-governed investment proposal automation")


def serialize(run_id: str, state: dict) -> RunResponse:
    status = state.get("status", "pending_approval")
    pdf_url = f"/v1/runs/{run_id}/proposal.pdf" if status == "completed" else None
    return RunResponse(run_id=run_id, status=status, lead=state.get("lead"), qualification=state.get("qualification"),
                       recommendations=state.get("recommendations", []), trace=state.get("trace", []),
                       approval_url=f"/v1/runs/{run_id}/approval" if status == "pending_approval" else None,
                       pdf_url=pdf_url)


@app.get("/healthz")
def health() -> dict:
    return {"status": "ok", "service": "real-estate-autoagent"}


@app.post("/v1/proposals", response_model=RunResponse, status_code=202)
def create_proposal(body: InquiryRequest) -> RunResponse:
    run_id = uuid4().hex[:12]
    result = start_run(run_id, body.inquiry, body.require_approval)
    state = get_state(run_id)
    if result.get("__interrupt__"):
        state["status"] = "pending_approval"
    return serialize(run_id, state)


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
    return serialize(run_id, get_state(run_id))


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
