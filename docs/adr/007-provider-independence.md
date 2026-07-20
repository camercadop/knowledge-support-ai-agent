# ADR-007: Provider Independence

## Status

Accepted

## Context

The platform depends on external providers for AI inference, communication channels, and data storage. These providers are third-party services with their own APIs, pricing models, and availability constraints. If the system is built directly against any one provider's API, replacing or supplementing it becomes a structural change rather than a configuration change.

## Decision

The system treats all external providers as interchangeable behind stable interfaces. No provider-specific type, concept, or behavior is allowed to cross the boundary into the application or domain layers. Each provider is represented by an adapter in the infrastructure layer that satisfies an interface defined by the application layer.

## Rationale

**Benefits** — Any provider can be replaced or supplemented without modifying business logic. The system can run against different providers in different environments. Provider-specific failure modes are contained at the adapter boundary.

**Tradeoffs** — Provider capabilities that have no equivalent in the interface contract cannot be used without first extending the contract. The lowest common denominator of provider capabilities shapes the interface.

**Assumptions** — The providers the system depends on are substitutable at the capability level relevant to the system's needs. If a provider offers a capability with no viable alternative, this assumption breaks down.

**Risks** — Interfaces designed around one provider's capabilities may inadvertently encode that provider's model, making true substitution harder than it appears.

## Alternatives Considered

**Direct provider SDK usage in use cases** — Use cases call provider SDKs directly. Rejected because it couples business logic to a specific vendor and violates ADR-003.

**Provider-specific base classes** — Share behavior through inheritance from provider-specific base classes. Rejected because it propagates provider concepts into layers that should be provider-agnostic.

## Consequences

### Positive

- Providers are replaceable without modifying the application or domain layers.
- The system can be tested with stub providers without real external calls.
- Provider-specific failure modes are isolated to the infrastructure layer.

### Negative

- Provider capabilities that exceed the interface contract are unavailable to the application layer without an interface change.
- Defining a provider-agnostic interface requires understanding the capabilities of multiple providers upfront.

### Risks

- An interface that appears provider-agnostic may encode one provider's model implicitly, making substitution harder in practice than in theory.

## Mandatory Rules

- No provider SDK type or concept may appear in the application or domain layers.
- Provider interfaces must be defined in the application layer.
- All provider adapters must live in the infrastructure layer.

## Allowed Changes

- Adding new provider adapters for an existing interface.
- Extending a provider interface with new capabilities, provided all adapters are updated.

## Forbidden Changes

- Importing provider SDK types into the application or domain layers.
- Designing an interface around a single provider's API surface without considering substitutability.

## Validation Criteria

- No application or domain layer code imports from any provider SDK.
- All provider interfaces are defined within the application layer.

## Related Documents

- [ADR-001](001-layered-architecture.md)
- [ADR-002](002-architecture-first-technology-second.md)
- [ADR-003](003-dependency-inversion.md)

## Future Revisions

- If the system commits permanently to a single provider with no substitution requirement, revisit whether the abstraction cost remains justified.
