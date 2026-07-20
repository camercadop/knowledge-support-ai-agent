# ADR-001: Clean Architecture

## Status

Accepted

## Context

The platform integrates with multiple external systems across different concerns: communication channels, AI providers, and data stores. Without explicit boundaries, business logic risks becoming coupled to these integrations, making the system hard to test, extend, or replace individual components.

The project requires extensibility across all integration points and independent testability of business logic without relying on real infrastructure.

## Decision

Adopt Clean Architecture. The codebase is divided into four concentric layers — domain, application, infrastructure, and API — with a strict inward dependency rule: outer layers depend on inner layers, never the reverse.

The application layer defines abstract ports (interfaces) for every external dependency it needs. The infrastructure layer provides concrete adapters that implement those ports. Dependencies are injected at the composition root, so inner layers never reference concrete outer-layer types.

## Rationale

**Benefits** — Business logic is fully isolated from external systems. Each layer can be tested independently without real infrastructure. New integrations require only a new adapter without touching the core. The ports make every external dependency explicit and visible.

**Tradeoffs** — More boilerplate than a flat structure. Simple operations require touching multiple layers. Every external dependency requires a corresponding port definition.

**Assumptions** — The system will need to swap or extend external integrations over its lifetime. If the system remains a single-integration prototype, this structure is over-engineered.

**Risks** — Layer boundaries erode over time if not enforced. Cross-layer shortcuts are easy to introduce and hard to detect without tooling.

## Alternatives Considered

**Flat structure** — All code in a single layer. Rejected because it couples business logic to infrastructure from the start, making testing and extension significantly harder.

**Generic layered architecture without ports** — Layers with inward dependencies but no explicit port interfaces. Rejected because it still allows inner layers to accumulate implicit dependencies on concrete types, undermining testability and replaceability.

## Consequences

### Positive

- External integrations can be replaced without modifying business logic.
- Each layer is independently testable without real infrastructure.
- Every external dependency is explicit — declared as a port in the application layer.
- Onboarding is straightforward — the structure communicates intent.

### Negative

- Simple features require changes across multiple layers.
- More files and indirection compared to a flat structure.
- Every new external dependency requires a port definition before it can be used.

### Risks

- Layer boundaries may erode under time pressure without active enforcement.
- Ports designed too narrowly may need to be widened when new adapters require additional capabilities.

## Mandatory Rules

- Inner layers must not import from outer layers.
- All external I/O must live in the infrastructure layer.
- Inner layers must only depend on ports they define themselves — never on concrete infrastructure types.
- Dependencies must be injected — never instantiated inside an inner layer.

## Allowed Changes

- Adding new modules within an existing layer.
- Introducing new adapters for an existing port without changing the port or inner layers.
- Reorganizing files within a layer without crossing boundaries.

## Forbidden Changes

- Importing outer-layer or infrastructure types directly into inner layers.
- Instantiating infrastructure dependencies inside the application or domain layer.
- Merging two layers into one without a superseding ADR.

## Validation Criteria

- No inner layer imports from an outer layer.
- No application or domain layer imports from the infrastructure layer.
- CI enforces import boundaries (or manual review on every PR).

## Related Documents

- `docs/architecture.md`

## Future Revisions

- If the system grows to multiple bounded contexts, revisit whether a modular monolith or service-per-domain better fits the scale.
- If the number of ports grows to the point where the indirection cost outweighs the benefit, revisit the granularity of interface boundaries.
