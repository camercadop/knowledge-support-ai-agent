# Writing Tests

## Structure

The `tests/` directory mirrors the production package structure under `app/`.

```
tests/
    api/              # mirrors app/api/
    application/      # mirrors app/application/
    infrastructure/   # mirrors app/infrastructure/
    conftest.py       # shared fixtures
```

Rules:
- Production code never imports from `tests/`.
- Tests may import any production module.
- Shared fixtures live in `tests/conftest.py`.

## Application Tests (`tests/application/`)

Target: `app/application/` — use cases.

- Inject all dependencies as mocks or fakes — never use real adapters.
- Do not patch internals (`unittest.mock.patch`). Inject through the constructor instead.
- Use the in-memory SQLite session from `conftest.py` via the `db` fixture.

```python
def test_answer_question_returns_reply(
    uow: SqlAlchemyMessagingUnitOfWork, vector_store: FakeVectorStore
) -> None:
    use_case = AnswerQuestion(
        uow=uow,
        chat_model=MockChatModel(reply="hello"),
        embedding_model=MockEmbeddingModel(),
        vector_store=vector_store,
    )
    reply = use_case.handle("+1234567890", "Hi")
    assert reply == "hello"
```

## Infrastructure Tests (`tests/infrastructure/`)

Target: `app/infrastructure/` — adapters, vector stores, pure utility logic.

- Use the in-memory SQLite session from `conftest.py` for DB-backed tests.
- For pure logic (e.g. `FakeVectorStore`, `_cosine_distance`), no fixtures are needed.
- Do not test business logic here — only that the adapter correctly reads and writes data.

## API Tests (`tests/api/`)

Target: `app/api/` — route handlers.

- Use FastAPI's `TestClient`.
- Override infrastructure dependencies via `app.dependency_overrides` or by replacing module-level singletons with mocks.
- Test HTTP contract: status codes, response shape, and error responses.
- Do not assert on business logic outcomes — that belongs in application tests.

```python
@pytest.fixture()
def client() -> Generator[TestClient]:
    app.dependency_overrides[get_db] = lambda: None
    chat_module._chat_model = MockChatModel(reply="mock reply")
    chat_module._embedding_model = MockEmbeddingModel()
    with patch("app.api.chat.AnswerQuestion.handle", return_value="mock reply"):
        yield TestClient(app)
    app.dependency_overrides.clear()


def test_chat_returns_reply(client: TestClient) -> None:
    response = client.post("/chat", json={"phone": "+1234567890", "message": "Hi"})
    assert response.status_code == 200
    assert response.json() == {"reply": "mock reply"}
```

## Naming

- Test files: `test_<module>.py`
- Test functions: `test_<what>_<expected_outcome>` — e.g. `test_chat_returns_reply`, `test_chat_missing_fields_returns_422`

## What to Test

| Layer | What | Where |
|---|---|---|
| Application | Use case orchestration with mock ports | `tests/application/` |
| Infrastructure | Adapter reads/writes, pure utility logic | `tests/infrastructure/` |
| API | HTTP contract, status codes, response shape | `tests/api/` |

## What Not to Test

- Framework internals (FastAPI routing, SQLAlchemy ORM mechanics).
- Mock behavior — do not assert that a mock was called unless the call itself is the contract.
- Implementation details — test observable outcomes, not internal state.

## Running Tests

```bash
uv run pytest
```
