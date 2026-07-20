# ADR-004: Use Case Oriented Application Layer

## Status

Accepted

## Context

The application layer sits between the domain and the infrastructure. Without a clear organizing principle, it tends to accumulate logic in arbitrary groupings — by entity, by HTTP verb, or by whatever is convenient at the time. This makes it hard to understand what the system actually does and where a given behavior lives.

The system needs a structure that makes business operations discoverable, independently testable, and free of infrastructure concerns.

## Decision

The application layer is organized around use cases. Each use case represents a single, named business operation. It orchestrates domain logic and delegates all I/O to injected abstractions. A use case has one entry point and one responsibility.

## Rationale

**Benefits** — The set of use cases is the executable specification of what the system does. Each operation is independently testable. Adding a new feature means adding a new use case without modifying existing ones.

**Tradeoffs** — Fine-grained use cases produce more files. Operations that share steps require explicit coordination rather than shared methods.

**Assumptions** — Business operations are stable enough to be named and bounded. If the domain is too fluid to name operations, this structure adds overhead without clarity.

**Risks** — Use cases may grow beyond a single responsibility over time if not actively kept focused.

## Alternatives Considered

**Service classes grouped by entity** — One service per domain entity containing all operations on that entity. Rejected because it concentrates unrelated behaviors in a single class and grows unbounded as the entity gains more operations.

**Fat controllers** — Business logic lives directly in the API layer. Rejected because it couples business behavior to the delivery mechanism and makes it untestable in isolation.

## Consequences

### Positive

- The application layer reads as a catalog of what the system does.
- Each use case is independently testable without infrastructure.
- New features are additive — existing use cases are not modified.

### Negative

- More files than a service-per-entity approach.
- Shared steps between use cases must be extracted explicitly rather than inherited.

### Risks

- Use cases may accumulate secondary responsibilities over time, eroding the single-responsibility boundary.

## Mandatory Rules

- Each use case must represent exactly one business operation.
- Use cases must not depend on infrastructure directly — only on injected abstractions.
- Use cases must not depend on delivery-layer concerns (HTTP, request/response shapes).

## Allowed Changes

- Adding new use cases without modifying existing ones.
- Extracting shared logic into domain services or helpers, provided they remain infrastructure-free.

## Forbidden Changes

- Adding multiple unrelated operations to a single use case.
- Importing infrastructure or delivery-layer types directly into a use case.

## Validation Criteria

- Each use case class has a single public entry point.
- No use case imports from the infrastructure or API layers.

## Related Documents

- [ADR-001](001-layered-architecture.md)
- [ADR-003](003-dependency-inversion.md)

## Future Revisions

- If the number of use cases grows to the point where discoverability suffers, revisit whether grouping by bounded context or domain module is warranted.
