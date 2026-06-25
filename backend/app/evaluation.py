from __future__ import annotations

from typing import Any

from .evaluator import GOLDEN_DATASET_PATH, load_golden_dataset


EVALUATION_DASHBOARD: dict[str, Any] = {
    "status": "implemented_foundation",
    "summary": "Golden inquiry datasets, regression tests, groundedness scoring, and tool-selection scoring are implemented as a local evaluation foundation.",
    "golden_dataset": str(GOLDEN_DATASET_PATH),
    "golden_case_count": len(load_golden_dataset()),
    "implemented_checks": [
        "real listing inventory loads from data/psi_listings.json",
        "mixed-language lead parsing",
        "approval produces PDF",
        "rejection prevents PDF",
        "budget and bedroom parsing regression",
        "agent trace order includes qualification and affordability",
        "golden inquiry dataset regression",
        "hallucination/groundedness scoring",
        "tool-selection accuracy scoring",
    ],
    "planned_checks": [
        "LLM-as-judge groundedness review",
        "historical regression tracking",
        "latency and cost dashboards",
        "CI quality gates",
    ],
}
