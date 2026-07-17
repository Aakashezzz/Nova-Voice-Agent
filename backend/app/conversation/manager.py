"""
Conversation Manager.

Keeps a sliding-window, in-memory history per session. A database is
deliberately not used here: conversation memory only needs to live for
the duration of a session, and SQLite would add complexity without a
real benefit for this use case (per the "keep it simple" requirement).
"""
import logging
import threading
import time
from dataclasses import dataclass, field

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class Session:
    session_id: str
    history: list[dict[str, str]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)


class ConversationManager:
    """Thread-safe, in-memory store of per-session chat history."""

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        self._lock = threading.Lock()
        self._max_turns = get_settings().llm_max_history_turns

    def get_or_create(self, session_id: str) -> Session:
        with self._lock:
            if session_id not in self._sessions:
                logger.info("Creating new conversation session: %s", session_id)
                self._sessions[session_id] = Session(session_id=session_id)
            session = self._sessions[session_id]
            session.last_active = time.time()
            return session

    def add_turn(self, session_id: str, role: str, content: str) -> None:
        session = self.get_or_create(session_id)
        with self._lock:
            session.history.append({"role": role, "content": content})
            # Keep only the most recent N turns to bound prompt size/latency.
            max_messages = self._max_turns * 2  # user+assistant pairs
            if len(session.history) > max_messages:
                session.history = session.history[-max_messages:]

    def get_history(self, session_id: str) -> list[dict[str, str]]:
        return list(self.get_or_create(session_id).history)

    def clear(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)
            logger.info("Cleared conversation session: %s", session_id)


_manager_instance: ConversationManager | None = None


def get_conversation_manager() -> ConversationManager:
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = ConversationManager()
    return _manager_instance
