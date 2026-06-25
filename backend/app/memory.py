from __future__ import annotations

from collections import defaultdict

from .domain import ConversationTurn


_CONVERSATIONS: dict[str, list[ConversationTurn]] = defaultdict(list)


def add_turn(conversation_id: str, role: str, content: str, run_id: str | None = None) -> None:
    _CONVERSATIONS[conversation_id].append(ConversationTurn(role=role, content=content, run_id=run_id))


def get_conversation(conversation_id: str) -> list[ConversationTurn]:
    return list(_CONVERSATIONS.get(conversation_id, []))


def summarize_context(conversation_id: str, limit: int = 6) -> list[dict]:
    return [turn.model_dump(mode="json") for turn in get_conversation(conversation_id)[-limit:]]


def conversation_count() -> int:
    return len(_CONVERSATIONS)
