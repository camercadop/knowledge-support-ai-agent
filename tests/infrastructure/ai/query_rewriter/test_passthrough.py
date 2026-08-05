
from app.application.support.ports.query_rewriter import QueryRewriter
from app.infrastructure.ai.query_rewriter.passthrough import PassthroughQueryRewriter


def test_passthrough_returns_query_unchanged() -> None:
    rewriter = PassthroughQueryRewriter()
    result = rewriter.rewrite("hello world", history=[])
    assert result == "hello world"


def test_passthrough_returns_query_unchanged_with_history() -> None:
    rewriter = PassthroughQueryRewriter()
    result = rewriter.rewrite("hello world", history=["previous message"])
    assert result == "hello world"


def test_passthrough_is_query_rewriter_port() -> None:
    assert isinstance(PassthroughQueryRewriter(), QueryRewriter)
