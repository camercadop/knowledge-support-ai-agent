# ADR-001: Layered Architecture

## Status

Accepted

## Context

The platform integrates with multiple external systems across different concerns: communication channels, AI providers, and data stores. Without explicit boundaries, business logic risks becoming coupled to these integrations, making the system hard to test, extend, or replace individual components.

The project requires extensibility across all integration points and independent testability of business logic.

## Decision

Adopt a layered architecture inspired by Clean Architecture. The codebase is divided into well-defined layers with a strict inward dependency rule — outer layers depend on inner layers, never the reverse.

## Rationale

**Benefits** — Business logic is isolated from external systems. Each layer can be tested independently. New integrations require only a new outer-layer adapter without touching the core.

**Tradeoffs** — More boilerplate than a flat structure. Simple operations require touching multiple layers.

**Assumptions** — The system will need to swap or extend external integrations over its lifetime. If the system remains a single-integration prototype, this structure is over-engineered.

**Risks** — Layer boundaries erode over time if not enforced. Cross-layer shortcuts are easy to introduce and hard to detect without tooling.

## Alternatives Considered

**Flat structure** — All code in a single layer. Rejected because it couples business logic to infrastructure from the start, making testing and extension significantly harder.

**Hexagonal (Ports and Adapters)** — Explicit port interfaces for every external dependency. Rejected as over-engineered for the current scale; the layered approach achieves the same isolation with less ceremony.

## Consequences

### Positive

- External integrations can be replaced without modifying business logic.
- Each layer is independently testable.
- Onboarding is straightforward — the structure communicates intent.

### Negative

- Simple features require changes across multiple layers.
- More files and indirection compared to a flat structure.

### Risks

- Layer boundaries may erode under time pressure without active enforcement.

## Mandatory Rules

- Inner layers must not import from outer layers.
- All external I/O must live in the outermost infrastructure layer.

## Allowed Changes

- Adding new modules within an existing layer.
- Introducing new outer-layer adapters without changing inner layers.
- Reorganizing files within a layer without crossing boundaries.

## Forbidden Changes

- Importing outer-layer dependencies directly into inner layers.
- Merging two layers into one without a superseding ADR.

## Validation Criteria

- No inner layer imports from an outer layer.
- CI enforces import boundaries (or manual review on every PR).

## Related Documents

- `docs/architecture.md`

## Future Revisions

- If the system grows to multiple bounded contexts, revisit whether a modular monolith or service-per-domain better fits the scale.
- If hexagonal ports become necessary for testing without mocks, revisit in favor of explicit port interfaces.
