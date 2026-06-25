from __future__ import annotations

from pathlib import Path
from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from .agents import match_properties, parse_lead, price_properties, research_areas
from .domain import AgentState, Lead, Recommendation, TraceEvent
from .proposal import build_pdf


OUTPUT_DIR = Path(__file__).resolve().parents[2] / "artifacts"


def approval_gate(state: AgentState) -> dict[str, Any]:
    if not state.get("require_approval", True):
        return {"approval": {"approved": True, "reviewer": "auto-policy", "note": "Approval bypass explicitly requested"}}
    decision = interrupt({"run_id": state["run_id"], "message": "Review recommendations before PDF generation",
                          "recommendations": state["recommendations"]})
    if not decision.get("approved"):
        return {"approval": decision, "status": "rejected"}
    return {"approval": decision, "status": "approved"}


def write_proposal(state: AgentState) -> dict[str, Any]:
    if not state.get("approval", {}).get("approved"):
        return {"status": "rejected"}
    path = build_pdf(state["run_id"], Lead.model_validate(state["lead"]),
                     [Recommendation.model_validate(x) for x in state["recommendations"]], OUTPUT_DIR)
    trace = list(state.get("trace", []))
    trace.append(TraceEvent(sequence=len(trace)+1, agent="Proposal Writer", summary="Rendered approved executive PDF with commercial disclaimer.", duration_ms=1, confidence=1.0).model_dump(mode="json"))
    return {"pdf_path": str(path), "status": "completed", "trace": trace}


def route_after_approval(state: AgentState) -> str:
    return "writer" if state.get("approval", {}).get("approved") else END


builder = StateGraph(AgentState)
builder.add_node("parser", parse_lead)
builder.add_node("matcher", match_properties)
builder.add_node("pricer", price_properties)
builder.add_node("researcher", research_areas)
builder.add_node("approval_gate", approval_gate)
builder.add_node("writer", write_proposal)
builder.add_edge(START, "parser")
builder.add_edge("parser", "matcher")
builder.add_edge("matcher", "pricer")
builder.add_edge("pricer", "researcher")
builder.add_edge("researcher", "approval_gate")
builder.add_conditional_edges("approval_gate", route_after_approval, {"writer": "writer", END: END})
builder.add_edge("writer", END)
graph = builder.compile(checkpointer=MemorySaver())


def config(run_id: str) -> dict[str, Any]:
    return {"configurable": {"thread_id": run_id}}


def start_run(run_id: str, inquiry: str, require_approval: bool) -> dict[str, Any]:
    return graph.invoke({"run_id": run_id, "inquiry": inquiry, "require_approval": require_approval,
                         "trace": [], "status": "running"}, config(run_id))


def resume_run(run_id: str, decision: dict[str, Any]) -> dict[str, Any]:
    return graph.invoke(Command(resume=decision), config(run_id))


def get_state(run_id: str) -> dict[str, Any]:
    return dict(graph.get_state(config(run_id)).values)
