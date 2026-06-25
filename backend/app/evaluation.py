from __future__ import annotations

from typing import Any


EVALUATION_DASHBOARD: dict[str, Any] = {
    "status": "foundation",
    "summary": "API and workflow tests currently act as the evaluation foundation.",
    "implemented_checks": [
        "real listing inventory loads from data/psi_listings.json",
        "mixed-language lead parsing",
        "approval produces PDF",
        "rejection prevents PDF",
        "budget and bedroom parsing regression",
        "agent trace order includes qualification and affordability",
    ],
    "planned_checks": [
        "golden inquiry dataset",
        "LLM-as-judge hallucination checks",
        "tool-calling accuracy",
        "latency and cost dashboards",
        "multilingual Arabic/Hindi regression suite",
    ],
}
