import pytest

from app.application.support.ports.chat_model import ChatMessage, Role
from app.application.support.ports.prompt_builder import PromptOverrides
from app.infrastructure.ai.prompt_builder.default import DefaultPromptBuilder, PromptConfig

_CONFIG = PromptConfig(
    system_instructions="base system",
    grounded_instructions="base grounded",
    no_context_instructions="base no context",
)

_HISTORY = [ChatMessage(role=Role.USER, content="Hi")]


@pytest.fixture()
def builder() -> DefaultPromptBuilder:
    return DefaultPromptBuilder(config=_CONFIG)


def test_build_without_context_uses_no_context_instructions(
    builder: DefaultPromptBuilder,
) -> None:
    messages = builder.build(_HISTORY, context=None)
    assert messages[0].role == Role.SYSTEM
    assert "base system" in messages[0].content
    assert "base no context" in messages[0].content


def test_build_with_context_uses_grounded_instructions(
    builder: DefaultPromptBuilder,
) -> None:
    messages = builder.build(_HISTORY, context="some context")
    assert "base grounded" in messages[0].content
    assert "some context" in messages[0].content


def test_build_appends_history_after_system_message(
    builder: DefaultPromptBuilder,
) -> None:
    messages = builder.build(_HISTORY, context=None)
    assert len(messages) == 2
    assert messages[1] == _HISTORY[0]


def test_override_system_instructions_replaces_config(
    builder: DefaultPromptBuilder,
) -> None:
    overrides = PromptOverrides(system_instructions="override system")
    messages = builder.build(_HISTORY, context=None, overrides=overrides)
    assert "override system" in messages[0].content
    assert "base system" not in messages[0].content


def test_override_grounded_instructions_replaces_config(
    builder: DefaultPromptBuilder,
) -> None:
    overrides = PromptOverrides(grounded_instructions="override grounded")
    messages = builder.build(_HISTORY, context="ctx", overrides=overrides)
    assert "override grounded" in messages[0].content
    assert "base grounded" not in messages[0].content


def test_override_no_context_instructions_replaces_config(
    builder: DefaultPromptBuilder,
) -> None:
    overrides = PromptOverrides(no_context_instructions="override no context")
    messages = builder.build(_HISTORY, context=None, overrides=overrides)
    assert "override no context" in messages[0].content
    assert "base no context" not in messages[0].content


def test_partial_override_falls_back_to_config_for_missing_keys(
    builder: DefaultPromptBuilder,
) -> None:
    overrides = PromptOverrides(system_instructions="override system")
    messages = builder.build(_HISTORY, context=None, overrides=overrides)
    assert "override system" in messages[0].content
    assert "base no context" in messages[0].content


def test_none_overrides_uses_config(builder: DefaultPromptBuilder) -> None:
    messages = builder.build(_HISTORY, context=None, overrides=None)
    assert "base system" in messages[0].content
    assert "base no context" in messages[0].content
