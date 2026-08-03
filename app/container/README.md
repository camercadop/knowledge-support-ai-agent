# container

Composition root for the application. Wires all infrastructure dependencies and exposes domain-scoped containers to entry points.

## Modules

- `base.py` — base class for all domain-scoped containers
- `__init__.py` — `ApplicationContainer`, composes all domain-scoped containers
- `support.py` — `SupportContainer`, wires all support use cases

## Pattern

Each domain-scoped container inherits from `BaseContainer` and overrides `_setup` to initialize shared singletons. Use case factory methods build a fresh instance per request, injecting cached singletons and per-request dependencies (e.g. the database session):

```python
class SupportContainer(BaseContainer):
    def _setup(self) -> None:
        self._chat_model = OpenAIChatModel(...)

    def answer_question(self, db: Session) -> AnswerQuestion:
        return AnswerQuestion(
            uow=SqlAlchemyMessagingUnitOfWork(db),
            chat_model=self._chat_model,
            embedding_model=self._singleton(OpenAIEmbeddingModel),
            instrumentation=self._instrumentation(ANSWER_QUESTION_INSTRUMENTATION),
        )
```

## Adding a new domain

1. Create `app/container/<domain>.py` with a class inheriting `BaseContainer`.
2. Add the domain container as an attribute on `ApplicationContainer` in `__init__.py`.

## CRUD use cases

For entities backed by a `CRUDUseCase`, expose a single method returning the use case instance. Route handlers call the appropriate method on the returned object:

```python
def knowledge_base_crud(self, db: Session) -> KnowledgeBaseCRUD:
    return KnowledgeBaseCRUD(uow=SqlAlchemyKnowledgeUnitOfWork(db))
```
