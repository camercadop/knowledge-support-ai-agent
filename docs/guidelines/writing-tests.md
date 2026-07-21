# Writing Tests

## Structure

The `tests/` directory mirrors the production package structure under `app/`.

```
tests/
    api/              # mirrors app/api/
    application/      # mirrors app/application/
    domain/           # mirrors app/domain/
    infrastructure/   # mirrors app/infrastructure/
    conftest.py       # shared fixtures
    factories/        # object factories and builders
    fakes/            # in-memory fake implementations of ports
```

Rules:
- Production code never imports from `tests/`.
- Tests may import any production module.
- Shared utilities (fixtures, fakes, factories) live under `tests/` — never alongside production code in `app/`.

## Unit Tests (`tests/unit/`)

Target: `app/domain/` and `app/application/`.

- Inject all dependencies as mocks or fakes — never use real adapters.
- Do not patch internals (`unittest.mock.patch`). Inject through the constructor instead.
- No database, no HTTP, no filesystem access.
- Fast enough to run on every keystroke.

```python
def test_answer_question_returns_reply() -> None:
    use_case = AnswerQuestion(
        uow=FakeMessagingUnitOfWork(),
        chat_model=MockChatModel(reply="hello"),
        embedding_model=MockEmbeddingModel(),
        vector_store=FakeVectorStore(),
    )
    reply = use_case.handle("+1234567890", "Hi")
    assert reply == "hello"
```

## Integration Tests (`tests/integration/`)

Target: `app/infrastructure/` — repositories, unit of work, vector store.

- Run against a real test database (separate from production).
- Each test must clean up after itself or run in a rolled-back transaction.
- Do not test business logic here — only that the adapter correctly reads and writes data.

## E2E Tests (`tests/e2e/`)

Target: `app/api/` — route handlers.

- Use FastAPI's `TestClient`.
- Override infrastructure dependencies via `app.dependency_overrides` or by replacing module-level singletons with mocks.
- Test HTTP contract: status codes, response shape, and error responses.
- Do not assert on business logic outcomes — that belongs in unit tests.

```python
@pytest.fixture()
def client() -> Generator[TestClient]:
    app.dependency_overrides[get_db] = lambda: None
    chat_module._chat_model = MockChatModel(reply="mock reply")
    chat_module._embedding_model = MockEmbeddingModel()
    with patch("app.api.chat.AnswerQuestion.handle", return_value="mock reply"):
        yield TestClient(app)
    app.dependency_overrides.clear()


def test_chat_returns_200(client: TestClient) -> None:
    response = client.post("/chat", json={"phone": "+1234567890", "message": "Hi"})
    assert response.status_code == 200
    assert "reply" in response.json()
```

## Naming

- Test files: `test_<module>.py`
- Test functions: `test_<what>_<expected_outcome>` — e.g. `test_chat_returns_reply`, `test_chat_missing_fields_returns_422`

## What to Test

| Layer | What | Where |
|---|---|---|
| Domain | Business rules, value objects | `tests/unit/` |
| Application | Use case orchestration with mock ports | `tests/unit/` |
| Infrastructure | Adapter reads/writes against test DB | `tests/integration/` |
| API | HTTP contract, status codes, response shape | `tests/e2e/` |

## What Not to Test

- Framework internals (FastAPI routing, SQLAlchemy ORM mechanics).
- Mock behavior — do not assert that a mock was called unless the call itself is the contract.
- Implementation details — test observable outcomes, not internal state.

## Running Tests

```bash
uv run pytest                        # all tests
uv run pytest tests/unit/            # unit only
uv run pytest tests/integration/     # integration only
uv run pytest tests/e2e/             # e2e only
```
