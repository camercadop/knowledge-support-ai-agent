# ADR-010: Domain Event Bus

## Status

Accepted

## Context

Use cases produce side effects that belong to different domains. The canonical example in this system is a completed chat turn triggering an analytics record. Without an explicit decoupling mechanism, the use case must import and invoke the analytics logic directly, coupling two unrelated domains at the application layer and making the use case harder to test in isolation.

The system needs a way for a use case to signal that something happened without knowing what, if anything, reacts to it.

## Decision

Use cases communicate outcomes by publishing domain events through an event publisher port defined in the application layer. Handlers that react to those events are registered at the composition root and live in the infrastructure layer. The use case has no knowledge of its handlers.

Domain events are immutable value objects that carry the facts of what happened. They are published after the primary transaction commits, so handlers observe a consistent state.

## Rationale

**Benefits** — Use cases remain focused on their primary responsibility. Adding a new reaction to an existing event requires no modification to the use case that publishes it. Each handler is independently testable. Cross-domain coupling is eliminated at the application layer.

**Tradeoffs** — The flow of control is no longer visible at the call site. Understanding what happens after an event is published requires tracing handler registrations in the composition root.

**Assumptions** — Handlers are in-process and synchronous. If a handler fails, the failure is not propagated back to the use case. This is acceptable as long as handler failures are non-critical side effects.

**Risks** — Publishing events after commit means a handler failure cannot roll back the primary transaction. If a handler must be atomic with the primary operation, this model does not apply.

## Alternatives Considered

**Direct use case invocation** — The publishing use case calls the analytics use case directly. Rejected because it couples two unrelated domains at the application layer and forces the publishing use case to know about every consumer.

**Database-level triggers or outbox pattern** — Side effects are driven by persistence events rather than application events. Rejected because it moves business logic into the infrastructure layer and adds operational complexity that is not warranted at this scale.

**Shared service called by both use cases** — Extract shared logic into a service both use cases call. Rejected because it does not eliminate the coupling — the publishing use case still needs to know about the shared service and call it explicitly.

## Consequences

### Positive

- Use cases are decoupled from the side effects they trigger.
- New reactions to existing events are additive — no existing code is modified.
- Each handler is independently testable without the publishing use case.
- The composition root is the single place where events are connected to handlers.

### Negative

- Control flow is non-linear — understanding the full effect of a use case requires reading the composition root.
- Handler failures are silent from the use case's perspective.

### Risks

- If a handler is accidentally registered multiple times, it will execute multiple times with no warning.
- Handlers that perform I/O may introduce latency into the request path, since dispatch is synchronous and in-process.

## Mandatory Rules

- The event publisher port must be defined in the application layer.
- Domain events must be immutable value objects defined in the application layer.
- Event handlers must live in the infrastructure layer.
- Handler registration must happen at the composition root — never inside a use case or domain object.
- Events must be published after the primary transaction commits, not before.

## Allowed Changes

- Adding new event types in the application layer.
- Adding new handlers for existing or new event types, registered at the composition root.
- Replacing the in-process event bus with a different event publisher implementation without modifying use cases or handlers.

## Forbidden Changes

- Registering handlers inside use cases or domain objects.
- Publishing events before the primary transaction commits.
- Defining event types or the event publisher port in the infrastructure layer.
- Making a use case depend on a specific handler or its outcome.

## Validation Criteria

- No use case imports a concrete event handler or event bus implementation.
- All handler registrations are in the composition root.
- All domain event classes are defined in the application layer.
- The event publisher port is defined in the application layer.

## Related Documents

- [ADR-001](001-clean-architecture.md)
- [ADR-003](003-dependency-inversion.md)
- [ADR-004](004-use-case-oriented-application-layer.md)
- [ADR-008](008-open-for-extension.md)

## Future Revisions

- If handlers need to be atomic with the primary transaction, revisit whether a transactional outbox pattern is warranted.
- If the number of handlers per event grows large enough to affect request latency, revisit whether async or out-of-process dispatch is needed.
