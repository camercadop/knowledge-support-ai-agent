import json
from unittest.mock import MagicMock

from app.application.support.ports.chat_model import ChatMessage, ChatModelOverrides, Role
from app.application.support.ports.tool_registry import ToolDefinition, ToolParameter
from app.infrastructure.ai.chat.openai import (
    ChatModelSettings,
    OpenAIChatModel,
    _to_function_tool,
    _to_input,
)
from app.infrastructure.ai.mock.tool_registry import MockToolRegistry

_DEFAULT_OVERRIDES = ChatModelOverrides(model="gpt-4o-mini", max_tokens=512, temperature=1.0)


def _make_model() -> OpenAIChatModel:
    model = OpenAIChatModel.__new__(OpenAIChatModel)
    model._client = MagicMock()
    model._settings = ChatModelSettings(
        api_key="test",
        model="gpt-4o-mini",
        max_tokens=512,
        temperature=1.0,
    )
    model._prompt_builder = MagicMock()
    return model


def _make_response(text: str, total: int = 0, input: int = 0, output: int = 0) -> MagicMock:
    response = MagicMock()
    response.output_text = text
    response.output = []
    response.usage.total_tokens = total
    response.usage.input_tokens = input
    response.usage.output_tokens = output
    return response


# --- _to_input ---


def test_to_input_converts_known_roles() -> None:
    messages = [
        ChatMessage(role=Role.USER, content="hi"),
        ChatMessage(role=Role.ASSISTANT, content="hello"),
    ]
    result = _to_input(messages)
    assert len(result) == 2
    assert result[0]["role"] == "user"
    assert result[1]["role"] == "assistant"


def test_to_input_preserves_all_known_roles() -> None:
    messages = [
        ChatMessage(role=Role.USER, content="hi"),
        ChatMessage(role=Role.ASSISTANT, content="hello"),
        ChatMessage(role=Role.SYSTEM, content="sys"),
        ChatMessage(role=Role.DEVELOPER, content="dev"),
    ]
    result = _to_input(messages)
    assert len(result) == 4


# --- _to_function_tool ---


def test_to_function_tool_maps_name_and_description() -> None:
    definition = ToolDefinition(name="my_tool", description="does something", parameters=[])
    result = _to_function_tool(definition)
    assert result["name"] == "my_tool"
    assert result["description"] == "does something"


def test_to_function_tool_marks_required_parameters() -> None:
    definition = ToolDefinition(
        name="my_tool",
        description="",
        parameters=[
            ToolParameter(name="q", type="string", description="query", required=True),
            ToolParameter(name="limit", type="integer", description="max", required=False),
        ],
    )
    result = _to_function_tool(definition)
    assert result["parameters"]["required"] == ["q"]
    assert "limit" in result["parameters"]["properties"]


# --- OpenAIChatModel.generate ---


def test_generate_returns_reply_and_token_usage() -> None:
    model = _make_model()
    model._client.responses.create.return_value = _make_response(
        "hello", total=10, input=6, output=4
    )
    messages = [ChatMessage(role=Role.USER, content="hi")]
    response = model.generate(messages, overrides=_DEFAULT_OVERRIDES)
    assert response.message.content == "hello"
    assert response.usage.total == 10
    assert response.usage.input_tokens == 6
    assert response.usage.output_tokens == 4


def test_generate_without_tool_registry_sends_no_tools() -> None:
    model = _make_model()
    model._client.responses.create.return_value = _make_response("ok")
    model.generate([ChatMessage(role=Role.USER, content="hi")], overrides=_DEFAULT_OVERRIDES)
    call_kwargs = model._client.responses.create.call_args.kwargs
    assert "tools" not in call_kwargs


def test_generate_with_tool_registry_sends_tool_definitions() -> None:
    model = _make_model()
    model._client.responses.create.return_value = _make_response("ok")
    registry = MockToolRegistry(handlers={"get_current_date": lambda _: "2025-01-01"})
    model.generate([ChatMessage(role=Role.USER, content="hi")], tool_registry=registry, overrides=_DEFAULT_OVERRIDES)
    call_kwargs = model._client.responses.create.call_args.kwargs
    assert any(t["name"] == "get_current_date" for t in call_kwargs["tools"])


def test_generate_executes_tool_call_and_loops_to_final_reply() -> None:
    model = _make_model()

    tool_call = MagicMock()
    tool_call.type = "function_call"
    tool_call.name = "get_current_date"
    tool_call.call_id = "call_1"
    tool_call.arguments = json.dumps({})

    first_response = MagicMock()
    first_response.output = [tool_call]
    first_response.usage.total_tokens = 5
    first_response.usage.input_tokens = 3
    first_response.usage.output_tokens = 2

    second_response = _make_response("today is 2025-01-01", total=8, input=5, output=3)

    model._client.responses.create.side_effect = [first_response, second_response]

    registry = MockToolRegistry(handlers={"get_current_date": lambda _: "2025-01-01"})
    response = model.generate(
        [ChatMessage(role=Role.USER, content="what day is it?")],
        tool_registry=registry,
        overrides=_DEFAULT_OVERRIDES,
    )

    assert response.message.content == "today is 2025-01-01"
    assert model._client.responses.create.call_count == 2
    assert response.usage.total == 13
