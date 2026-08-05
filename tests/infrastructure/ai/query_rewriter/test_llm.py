from unittest.mock import MagicMock

from app.application.support.ports.chat_model import (
    ChatMessage,
    ChatModel,
    ChatResponse,
    Role,
    TokenUsage,
)
from app.application.support.ports.query_rewriter import QueryRewriter
from app.infrastructure.ai.query_rewriter.llm import LLMQueryRewriter


def test_llm_rewriter_returns_model_response() -> None:
    mock_model = MagicMock(spec=ChatModel)
    mock_model.generate.return_value = ChatResponse(
        message=ChatMessage(role=Role.ASSISTANT, content="rewritten query"),
        usage=TokenUsage(total=10, input_tokens=5, output_tokens=5),
        model_used="gpt-4o-mini",
    )
    rewriter = LLMQueryRewriter(chat_model=mock_model, prompt="Rewrite this.")
    result = rewriter.rewrite("original query", history=[])
    assert result == "rewritten query"


def test_llm_rewriter_passes_correct_messages() -> None:
    mock_model = MagicMock(spec=ChatModel)
    mock_model.generate.return_value = ChatResponse(
        message=ChatMessage(role=Role.ASSISTANT, content="rewritten"),
        usage=TokenUsage(total=10),
        model_used="gpt-4o-mini",
    )
    rewriter = LLMQueryRewriter(chat_model=mock_model, prompt="Rewrite this.")
    rewriter.rewrite("user query", history=["prev user", "prev assistant"])
    call_args = mock_model.generate.call_args
    messages = call_args.kwargs.get("messages") or call_args.args[0]
    assert messages[0] == ChatMessage(role=Role.SYSTEM, content="Rewrite this.")
    assert messages[1] == ChatMessage(role=Role.USER, content="prev user")
    assert messages[2] == ChatMessage(role=Role.ASSISTANT, content="prev user")
    assert messages[3] == ChatMessage(role=Role.USER, content="prev assistant")
    assert messages[4] == ChatMessage(role=Role.ASSISTANT, content="prev assistant")
    assert messages[5] == ChatMessage(role=Role.USER, content="user query")


def test_llm_rewriter_is_query_rewriter_port() -> None:
    mock_model = MagicMock(spec=ChatModel)
    rewriter = LLMQueryRewriter(chat_model=mock_model, prompt="Rewrite this.")
    assert isinstance(rewriter, QueryRewriter)
