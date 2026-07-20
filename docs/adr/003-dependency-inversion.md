# ADR-003: Dependency Inversion

## Status

Accepted

## Context

The layered architecture established in ADR-001 requires that inner layers remain independent of outer layers. Without an explicit mechanism to enforce this, inner layers naturally accumulate direct dependencies on concrete implementations — databases, HTTP clients, AI SDKs — because those are the easiest things to reach for.

Direct dependencies on concrete implementations make inner layers impossible to test in isolation and tightly couple business logic to infrastructure choices.

## Decision

Dependencies between layers flow inward through abstractions. Inner layers define interfaces (ports) that describe what they need. Outer layers provide concrete implementations (adapters) that satisfy those interfaces. No inner layer holds a direct reference to a concrete outer-layer implementation.

## Rationale

**Benefits** — Inner layers can be tested without any real infrastructure. Concrete implementations can be replaced without modifying the layers that depend on them. The direction of source-code dependencies is the inverse of the direction of control flow.

**Tradeoffs** — Every external dependency requires a corresponding abstraction. This adds indirection and more files.

**Assumptions** — The cost of defining abstractions is lower than the cost of coupling inner layers to concrete implementations. This holds as long as the system has more than one integration point or requires unit testing.

**Risks** — Abstractions may be defined too narrowly, requiring changes when a new adapter needs capabilities the interface does not expose.

## Alternatives Considered

**Direct dependencies** — Inner layers import concrete implementations directly. Rejected because it makes inner layers untestable in isolation and couples them to infrastructure.

**Service locator** — Inner layers resolve dependencies at runtime from a global registry. Rejected because it hides dependencies, making the system harder to reason about and test.

## Consequences

### Positive

- Inner layers are testable without real infrastructure.
- Concrete implementations are interchangeable without modifying business logic.
- Dependency relationships are explicit and visible at the interface boundary.

### Negative

- Every external dependency requires a defined abstraction.
- More indirection between a call site and its implementation.

### Risks

- Interfaces designed too narrowly may need to be widened when new adapters require additional capabilities.

## Mandatory Rules

- Inner layers must only depend on abstractions they define themselves.
- Concrete implementations must live in the infrastructure layer.
- Dependencies must be injected — never instantiated inside an inner layer.

## Allowed Changes

- Adding new methods to an existing interface, provided all existing adapters are updated.
- Introducing new adapters for an existing interface without modifying the interface or inner layers.

## Forbidden Changes

- Importing a concrete infrastructure type directly into the application or domain layer.
- Instantiating infrastructure dependencies inside inner layers.

## Validation Criteria

- No inner layer imports from the infrastructure layer.
- All infrastructure types are referenced only through their interfaces within inner layers.

## Related Documents

- [ADR-001](001-clean-architecture.md)
- [ADR-002](002-architecture-first-technology-second.md)

## Future Revisions

- If the number of abstractions grows to the point where the indirection cost outweighs the benefit, revisit the granularity of interface boundaries.
