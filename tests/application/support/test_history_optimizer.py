from unittest.mock import MagicMock

from app.application.support.ports.chat_model import ChatMessage, Role
from app.application.support.services.history_optimizer import ConversationHistoryOptimizer


def _msg(role: Role, content: str = "x") -> ChatMessage:
    return ChatMessage(role=role, content=content)


def test_returns_empty_list_unchanged() -> None:
    optimizer = ConversationHistoryOptimizer(policies=[])
    assert optimizer.optimize_history([]) == []


def test_applies_no_policies_returns_original() -> None:
    optimizer = ConversationHistoryOptimizer(policies=[])
    messages = [_msg(Role.USER, "hi"), _msg(Role.ASSISTANT, "hello")]
    assert optimizer.optimize_history(messages) == messages


def test_applies_single_policy() -> None:
    policy = MagicMock()
    policy.apply.return_value = [_msg(Role.USER, "trimmed")]
    optimizer = ConversationHistoryOptimizer(policies=[policy])
    messages = [_msg(Role.USER, "hi"), _msg(Role.ASSISTANT, "hello")]
    result = optimizer.optimize_history(messages)
    policy.apply.assert_called_once_with(messages)
    assert result == [_msg(Role.USER, "trimmed")]


def test_applies_policies_in_order() -> None:
    call_order: list[str] = []

    def make_policy(name: str) -> MagicMock:
        p = MagicMock()
        def side_effect(msgs: list[ChatMessage]) -> list[ChatMessage]:
            call_order.append(name)
            return msgs
        p.apply.side_effect = side_effect
        return p

    p1 = make_policy("first")
    p2 = make_policy("second")
    optimizer = ConversationHistoryOptimizer(policies=[p1, p2])
    optimizer.optimize_history([_msg(Role.USER)])
    assert call_order == ["first", "second"]


def test_each_policy_receives_output_of_previous() -> None:
    msg_a = _msg(Role.USER, "a")
    msg_b = _msg(Role.ASSISTANT, "b")

    p1 = MagicMock()
    p1.apply.return_value = [msg_b]
    p2 = MagicMock()
    p2.apply.return_value = [msg_b]

    optimizer = ConversationHistoryOptimizer(policies=[p1, p2])
    optimizer.optimize_history([msg_a])
    p2.apply.assert_called_once_with([msg_b])
