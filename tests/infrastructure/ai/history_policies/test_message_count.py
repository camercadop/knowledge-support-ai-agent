from app.application.support.ports.chat_model import ChatMessage, Role
from app.infrastructure.ai.history_policies.message_count import MessageCountPolicy


def _msg(role: Role, content: str = "x") -> ChatMessage:
    return ChatMessage(role=role, content=content)


def test_returns_all_messages_when_under_limit() -> None:
    policy = MessageCountPolicy(max_messages=10)
    messages = [_msg(Role.USER), _msg(Role.ASSISTANT)]
    assert policy.apply(messages) == messages


def test_trims_oldest_messages_when_over_limit() -> None:
    policy = MessageCountPolicy(max_messages=3)
    messages = [
        _msg(Role.ASSISTANT, "a"),
        _msg(Role.ASSISTANT, "b"),
        _msg(Role.ASSISTANT, "c"),
        _msg(Role.USER, "d"),
    ]
    result = policy.apply(messages)
    assert len(result) == 3


def test_protects_last_user_message() -> None:
    policy = MessageCountPolicy(max_messages=2)
    messages = [
        _msg(Role.ASSISTANT, "a"),
        _msg(Role.ASSISTANT, "b"),
        _msg(Role.USER, "keep"),
    ]
    result = policy.apply(messages)
    assert result[-1].content == "keep"


def test_protects_user_and_following_assistant_message() -> None:
    policy = MessageCountPolicy(max_messages=2)
    messages = [
        _msg(Role.ASSISTANT, "old1"),
        _msg(Role.ASSISTANT, "old2"),
        _msg(Role.USER, "keep_user"),
        _msg(Role.ASSISTANT, "keep_assistant"),
    ]
    result = policy.apply(messages)
    assert result[-2].content == "keep_user"
    assert result[-1].content == "keep_assistant"


def test_returns_messages_unchanged_when_max_messages_is_zero() -> None:
    policy = MessageCountPolicy(max_messages=0)
    messages = [_msg(Role.USER), _msg(Role.ASSISTANT)]
    assert policy.apply(messages) == messages


def test_returns_empty_list_unchanged() -> None:
    policy = MessageCountPolicy(max_messages=5)
    assert policy.apply([]) == []
