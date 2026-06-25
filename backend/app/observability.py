from __future__ import annotations

from collections import Counter
from time import perf_counter
from typing import Any


_STARTED_AT = perf_counter()
_RUN_STATUSES: Counter[str] = Counter()
_AGENT_CALLS: Counter[str] = Counter()
_AGENT_DURATION_MS: Counter[str] = Counter()


def record_run_status(status: str) -> None:
    _RUN_STATUSES[status] += 1


def record_trace(trace: list[dict[str, Any]]) -> None:
    for event in trace:
        agent = str(event.get("agent", "unknown"))
        _AGENT_CALLS[agent] += 1
        _AGENT_DURATION_MS[agent] += int(event.get("duration_ms") or 0)


def metrics() -> dict[str, Any]:
    avg_duration = {
        agent: round(_AGENT_DURATION_MS[agent] / count, 2)
        for agent, count in _AGENT_CALLS.items()
        if count
    }
    return {
        "uptime_seconds": round(perf_counter() - _STARTED_AT, 2),
        "run_status_counts": dict(_RUN_STATUSES),
        "agent_call_counts": dict(_AGENT_CALLS),
        "agent_avg_duration_ms": avg_duration,
    }
