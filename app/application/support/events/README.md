# events

Domain events raised by the support domain use cases.

## Events

- `question_answered.py` — `QuestionAnswered`: raised after a chat turn completes and both the user and assistant messages are persisted. Carries the conversation ID, question, answer, model used, retrieved chunks, and token usage.
- `context_compressed.py` — `ContextCompressed`: raised after context compression is applied during retrieval, once the conversation is resolved. Carries the conversation ID, compression strategy, compression ratio, and chunk counts before and after compression.

## Usage

Events are published via the `EventPublisher` port injected into use cases. Handlers are registered on the `InMemoryEventBus` in the container. See [Writing Events](../../../../docs/guidelines/writing-events.md) for the full reference.
