from app.application.support.ports.chat_model import ChatMessage, Role
from app.infrastructure.ai.history_policies.token_limit import TokenLimitPolicy


def _msg(role: Role, content: str) -> ChatMessage:
    return ChatMessage(role=role, content=content)


def _policy(max_tokens: int) -> TokenLimitPolicy:
    return TokenLimitPolicy(max_tokens=max_tokens, token_calculator=len)


def test_returns_messages_unchanged_when_under_budget() -> None:
    policy = _policy(max_tokens=1000)
    messages = [_msg(Role.USER, "hi"), _msg(Role.ASSISTANT, "hello")]
    assert policy.apply(messages) == messages


def test_trims_oldest_messages_to_fit_budget() -> None:
    policy = TokenLimitPolicy(max_tokens=10)
    messages = [
        _msg(Role.ASSISTANT, "a" * 500),
        _msg(Role.ASSISTANT, "b" * 500),
        _msg(Role.USER, "hi"),
    ]
    result = policy.apply(messages)
    assert result[-1].content == "hi"
    assert len(result) < len(messages)


def test_protects_last_user_message_from_trimming() -> None:
    policy = _policy(max_tokens=2)
    messages = [
        _msg(Role.ASSISTANT, "long content here"),
        _msg(Role.USER, "hi"),
    ]
    result = policy.apply(messages)
    assert any(m.content == "hi" for m in result)


def test_protects_user_and_assistant_pair_at_end() -> None:
    policy = _policy(max_tokens=4)
    messages = [
        _msg(Role.ASSISTANT, "old long message"),
        _msg(Role.USER, "hi"),
        _msg(Role.ASSISTANT, "ok"),
    ]
    result = policy.apply(messages)
    assert result[-2].content == "hi"
    assert result[-1].content == "ok"


def test_returns_unchanged_when_max_tokens_is_zero() -> None:
    policy = _policy(max_tokens=0)
    messages = [_msg(Role.USER, "hi")]
    assert policy.apply(messages) == messages


def test_returns_empty_list_unchanged() -> None:
    policy = _policy(max_tokens=100)
    assert policy.apply([]) == []
