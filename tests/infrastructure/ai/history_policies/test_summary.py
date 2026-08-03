from app.application.support.ports.chat_model import ChatMessage, Role
from app.infrastructure.ai.history_policies.summary import SummaryPolicy
from app.infrastructure.ai.mock.chat import MockChatModel


def _msg(role: Role, content: str = "x") -> ChatMessage:
    return ChatMessage(role=role, content=content)


def _policy(max_messages: int = 3, reply: str = "summary") -> SummaryPolicy:
    return SummaryPolicy(
        chat_model=MockChatModel(reply=reply),
        max_summary_tokens=1000,
        max_summary_messages=max_messages,
    )


def test_returns_messages_unchanged_when_under_limit() -> None:
    policy = _policy(max_messages=5)
    messages = [_msg(Role.USER, "a"), _msg(Role.ASSISTANT, "b")]
    assert policy.apply(messages) == messages


def test_summarizes_when_over_limit() -> None:
    policy = _policy(max_messages=2)
    messages = [
        _msg(Role.USER, "msg1"),
        _msg(Role.ASSISTANT, "msg2"),
        _msg(Role.USER, "msg3"),
    ]
    result = policy.apply(messages)
    assert len(result) < len(messages)


def test_summary_message_has_assistant_role() -> None:
    policy = _policy(max_messages=2, reply="summarized")
    messages = [
        _msg(Role.USER, "a"),
        _msg(Role.ASSISTANT, "b"),
        _msg(Role.USER, "c"),
    ]
    result = policy.apply(messages)
    assert any(m.role == Role.ASSISTANT for m in result)


def test_handles_chat_model_failure_gracefully() -> None:
    class FailingChatModel(MockChatModel):
        def generate(self, messages, tool_registry=None):  # type: ignore[override]
            raise RuntimeError("provider down")

    policy = SummaryPolicy(
        chat_model=FailingChatModel(),
        max_summary_tokens=1000,
        max_summary_messages=2,
    )
    messages = [_msg(Role.USER, "a"), _msg(Role.ASSISTANT, "b"), _msg(Role.USER, "c")]
    result = policy.apply(messages)
    assert isinstance(result, list)
