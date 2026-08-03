from app.application.support.ports.chat_model import ChatMessage, Role
from app.infrastructure.ai.history_policies.role_filter import RoleFilterPolicy


def _msg(role: Role, content: str = "x") -> ChatMessage:
    return ChatMessage(role=role, content=content)


def test_keeps_messages_with_allowed_roles() -> None:
    policy = RoleFilterPolicy(allowed_roles=["user", "assistant"])
    messages = [_msg(Role.USER, "hi"), _msg(Role.ASSISTANT, "hello")]
    result = policy.apply(messages)
    assert len(result) == 2


def test_removes_messages_with_disallowed_roles() -> None:
    policy = RoleFilterPolicy(allowed_roles=["user", "assistant"])
    messages = [_msg(Role.SYSTEM, "sys"), _msg(Role.USER, "hi")]
    result = policy.apply(messages)
    assert all(m.role != Role.SYSTEM for m in result)


def test_blocks_explicitly_blocked_roles() -> None:
    policy = RoleFilterPolicy(allowed_roles=["user", "assistant"], blocked_roles=["assistant"])
    messages = [_msg(Role.USER, "hi"), _msg(Role.ASSISTANT, "hello")]
    result = policy.apply(messages)
    assert all(m.role != Role.ASSISTANT for m in result)


def test_protects_last_user_message_even_if_role_not_allowed() -> None:
    policy = RoleFilterPolicy(allowed_roles=["assistant"])
    messages = [_msg(Role.ASSISTANT, "a"), _msg(Role.USER, "keep")]
    result = policy.apply(messages)
    assert result[-1].content == "keep"


def test_protects_user_assistant_pair_at_end() -> None:
    policy = RoleFilterPolicy(allowed_roles=["assistant"])
    messages = [
        _msg(Role.SYSTEM, "drop"),
        _msg(Role.USER, "keep_user"),
        _msg(Role.ASSISTANT, "keep_assistant"),
    ]
    result = policy.apply(messages)
    contents = [m.content for m in result]
    assert "keep_user" in contents
    assert "keep_assistant" in contents


def test_returns_empty_list_unchanged() -> None:
    policy = RoleFilterPolicy(allowed_roles=["user"])
    assert policy.apply([]) == []
