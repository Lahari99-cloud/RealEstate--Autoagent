from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any
from uuid import uuid4

from .data import LISTINGS
from .workflow import get_state, start_run


PROJECT_ROOT = Path(__file__).resolve().parents[2]
GOLDEN_DATASET_PATH = PROJECT_ROOT / "evals" / "golden_inquiries.json"


def load_golden_dataset(path: Path = GOLDEN_DATASET_PATH) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def _score_extraction(lead: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "area": expected["area"] in lead.get("preferred_areas", []),
        "bedrooms": lead.get("bedrooms") == expected["bedrooms"],
        "budget_aed": lead.get("budget_aed") == expected["budget_aed"],
        "language": lead.get("language") == expected["language"],
        "purpose": lead.get("purpose") == expected["purpose"],
    }
    return {"score": round(sum(checks.values()) / len(checks), 3), "checks": checks}


def _score_groundedness(state: dict[str, Any]) -> dict[str, Any]:
    listing_ids = {listing.id for listing in LISTINGS}
    recommendations = state.get("recommendations", [])
    checks = {
        "all_recommendations_from_inventory": all(rec["listing"]["id"] in listing_ids for rec in recommendations),
        "no_empty_area_rationale": all(bool(rec.get("area_rationale")) for rec in recommendations),
        "compliance_disclaimer_present": bool(state.get("compliance", {}).get("disclaimers")),
        "no_guaranteed_return_language": not any(
            "guaranteed" in " ".join([
                rec.get("affordability_note", ""),
                " ".join(rec.get("risk_flags", [])),
                rec.get("area_rationale", ""),
            ]).lower()
            for rec in recommendations
        ),
    }
    return {"score": round(sum(checks.values()) / len(checks), 3), "checks": checks}


def _score_tool_selection(trace: list[dict[str, Any]], expected_agents: list[str]) -> dict[str, Any]:
    actual = [event.get("agent") for event in trace]
    required_present = {agent: agent in actual for agent in expected_agents}
    order_ok = [agent for agent in actual if agent in expected_agents] == expected_agents
    checks = {**required_present, "expected_order": order_ok}
    return {"score": round(sum(checks.values()) / len(checks), 3), "checks": checks, "actual_agents": actual}


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    run_id = f"eval-{uuid4().hex[:8]}"
    start_run(run_id, case["inquiry"], True, f"eval-{case['id']}", [])
    state = get_state(run_id)
    expected = case["expected"]
    extraction = _score_extraction(state["lead"], expected)
    groundedness = _score_groundedness(state)
    tool_selection = _score_tool_selection(state["trace"], expected["required_agents"])
    overall = round(mean([extraction["score"], groundedness["score"], tool_selection["score"]]), 3)
    return {
        "id": case["id"],
        "run_id": run_id,
        "overall_score": overall,
        "extraction": extraction,
        "groundedness": groundedness,
        "tool_selection": tool_selection,
    }


def run_evaluation_suite() -> dict[str, Any]:
    cases = load_golden_dataset()
    results = [evaluate_case(case) for case in cases]
    return {
        "status": "passed" if all(result["overall_score"] >= 0.85 for result in results) else "review_required",
        "case_count": len(results),
        "overall_score": round(mean(result["overall_score"] for result in results), 3),
        "extraction_score": round(mean(result["extraction"]["score"] for result in results), 3),
        "groundedness_score": round(mean(result["groundedness"]["score"] for result in results), 3),
        "tool_selection_score": round(mean(result["tool_selection"]["score"] for result in results), 3),
        "results": results,
    }
