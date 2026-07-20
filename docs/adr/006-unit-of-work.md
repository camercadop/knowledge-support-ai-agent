# ADR-006: Unit of Work

## Status

Accepted

## Context

A use case often involves multiple repository operations that must succeed or fail together. Without a coordination mechanism, each repository manages its own connection or session, making it impossible to guarantee atomicity across operations from the application layer without leaking transaction management into business logic.

## Decision

A Unit of Work abstraction is responsible for grouping repository operations into a single atomic boundary. The application layer interacts with the Unit of Work through an interface it defines. Concrete implementations that manage the underlying transaction live in the infrastructure layer.

## Rationale

**Benefits** — Atomicity across multiple repository operations is guaranteed without exposing transaction mechanics to the application layer. Use cases remain focused on business logic. The transaction strategy is replaceable without modifying use cases.

**Tradeoffs** — Adds another abstraction that must be defined, implemented, and injected. Use cases must be aware of when to commit or roll back, even if they do not manage the mechanism.

**Assumptions** — The system requires atomic multi-repository operations. If every use case touches exactly one repository, the Unit of Work adds overhead without benefit.

**Risks** — The Unit of Work boundary may be drawn incorrectly, grouping operations that should not be atomic or splitting operations that should be.

## Alternatives Considered

**Transaction management in repositories** — Each repository manages its own transaction. Rejected because it makes cross-repository atomicity impossible without coupling repositories to each other.

**Transaction management in the infrastructure layer only** — Wrap every use case invocation in a transaction at the infrastructure boundary. Rejected because it removes the application layer's ability to control commit timing and makes partial commits impossible.

## Consequences

### Positive

- Atomicity across multiple repository operations is achievable from the application layer.
- Transaction mechanics are hidden behind an abstraction.
- The transaction strategy is replaceable without modifying use cases.

### Negative

- Use cases must explicitly signal commit or rollback intent.
- Every use case that requires atomicity must receive a Unit of Work instance.

### Risks

- Incorrect Unit of Work boundaries may cause unintended partial commits or overly broad transactions.

## Mandatory Rules

- Transaction management must not be performed directly in the application layer — only through the Unit of Work interface.
- The Unit of Work interface must be defined in the application layer.
- Concrete implementations must live in the infrastructure layer.

## Allowed Changes

- Providing additional concrete Unit of Work implementations for different persistence backends.
- Extending the interface with new coordination methods, provided all implementations are updated.

## Forbidden Changes

- Managing transactions directly in use cases or repositories without going through the Unit of Work.
- Defining the Unit of Work interface in the infrastructure layer.

## Validation Criteria

- No application-layer code references transaction primitives from the persistence mechanism directly.
- The Unit of Work interface is defined within the application layer.

## Related Documents

- [ADR-001](001-layered-architecture.md)
- [ADR-003](003-dependency-inversion.md)
- [ADR-005](005-repository-pattern.md)

## Future Revisions

- If the system adopts an event-driven or eventual consistency model, revisit whether strong transactional boundaries remain appropriate.
