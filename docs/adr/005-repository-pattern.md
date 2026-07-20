# ADR-005: Repository Pattern

## Status

Accepted

## Context

The application layer needs to read and persist domain objects. Without a defined boundary, data access logic spreads across use cases and domain objects, coupling business logic to the persistence mechanism and making it impossible to test without a real database.

## Decision

All data access is encapsulated behind repository interfaces. The application layer interacts with repositories through abstractions it defines. Concrete implementations that translate between domain objects and the persistence mechanism live in the infrastructure layer.

## Rationale

**Benefits** — Business logic is decoupled from the persistence mechanism. Use cases can be tested with in-memory or stub repositories. The persistence technology can be replaced without modifying the application layer.

**Tradeoffs** — Every aggregate or entity that needs persistence requires a corresponding repository interface and at least one concrete implementation.

**Assumptions** — The domain model is stable enough to define repository contracts against. If the data model is in constant flux, maintaining repository interfaces adds overhead.

**Risks** — Repository interfaces may be designed around persistence convenience rather than domain needs, leaking storage concerns into the application layer.

## Alternatives Considered

**Active Record** — Domain objects manage their own persistence. Rejected because it couples domain logic to the persistence mechanism and makes unit testing without a database impractical.

**Direct ORM access in use cases** — Use cases query the ORM directly. Rejected because it exposes persistence details to the application layer and violates ADR-003.

## Consequences

### Positive

- Use cases are testable without a real database.
- The persistence mechanism is replaceable without touching business logic.
- Data access intent is expressed in domain terms, not query terms.

### Negative

- Each persistable entity requires a repository interface and a concrete implementation.
- Query logic must be expressed through the repository contract, which can be limiting for complex queries.

### Risks

- Repository interfaces may accumulate query methods that reflect persistence needs rather than domain operations, gradually coupling the two.

## Mandatory Rules

- All data access from the application layer must go through a repository interface.
- Repository interfaces must be defined in the application layer, not the infrastructure layer.
- Concrete repository implementations must live in the infrastructure layer.

## Allowed Changes

- Adding new repository interfaces for new aggregates.
- Adding new methods to an existing interface, provided all implementations are updated.
- Providing additional concrete implementations for an existing interface.

## Forbidden Changes

- Accessing the persistence mechanism directly from the application or domain layer.
- Defining repository interfaces in the infrastructure layer.

## Validation Criteria

- No application-layer code imports ORM or database types directly.
- All repository interfaces are defined within the application layer.

## Related Documents

- [ADR-001](001-clean-architecture.md)
- [ADR-003](003-dependency-inversion.md)
- [ADR-004](004-use-case-oriented-application-layer.md)

## Future Revisions

- If complex query requirements make the repository abstraction too rigid, revisit whether a query-object pattern or read-model separation is warranted.
