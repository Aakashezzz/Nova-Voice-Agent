"""Unit tests for the in-memory conversation manager."""
from app.conversation.manager import ConversationManager


def test_new_session_starts_empty():
    manager = ConversationManager()
    assert manager.get_history("session-1") == []


def test_add_turn_appends_history():
    manager = ConversationManager()
    manager.add_turn("session-1", "user", "Hello")
    manager.add_turn("session-1", "assistant", "Hi there!")

    history = manager.get_history("session-1")
    assert history == [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]


def test_sessions_are_isolated():
    manager = ConversationManager()
    manager.add_turn("session-a", "user", "A says hi")
    manager.add_turn("session-b", "user", "B says hi")

    assert manager.get_history("session-a") == [{"role": "user", "content": "A says hi"}]
    assert manager.get_history("session-b") == [{"role": "user", "content": "B says hi"}]


def test_clear_removes_session_history():
    manager = ConversationManager()
    manager.add_turn("session-1", "user", "Hello")
    manager.clear("session-1")

    assert manager.get_history("session-1") == []


def test_history_is_trimmed_to_max_turns(monkeypatch):
    manager = ConversationManager()
    manager._max_turns = 2  # keep at most 2 user/assistant pairs = 4 messages

    for i in range(10):
        manager.add_turn("session-1", "user", f"message {i}")
        manager.add_turn("session-1", "assistant", f"reply {i}")

    history = manager.get_history("session-1")
    assert len(history) == 4
    assert history[0]["content"] == "message 8"
