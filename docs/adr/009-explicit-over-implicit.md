# ADR-009: Explicit over Implicit

## Status

Accepted

## Context

A system that relies on conventions, defaults, or runtime resolution to determine behavior is harder to read, test, and debug. When dependencies are resolved silently, optional features are toggled by internal flag checks, or contracts are inferred rather than declared, the actual behavior of the system is not visible from the code alone.

This project integrates with multiple external providers, supports configurable optional behaviors, and is expected to be maintained and extended over time. Implicit behavior increases the cost of every change.

## Decision

Anything that affects behavior must be visible at the point where it is declared or wired. Dependencies, optionality, and contracts are stated explicitly — never inferred, defaulted silently, or resolved at runtime from a source outside the caller's control.

Configuration translates into wiring decisions at the composition root. A component does not decide for itself whether an optional behavior is active; that decision is made by whoever constructs it.

## Rationale

**Benefits** — Behavior is auditable from the code alone, without tracing runtime state or reading configuration. Optional features can be controlled in isolation during testing. The composition root is the single authoritative place where configuration becomes behavior.

**Tradeoffs** — Explicit wiring is more verbose than implicit alternatives.

**Assumptions** — The cost of verbose wiring is lower than the cost of behavior that is invisible to the reader. This holds as long as the system has more than a handful of dependencies or configurable behaviors.

**Risks** — The composition root may grow complex as the number of conditional wirings increases.

## Alternatives Considered

**Runtime resolution** — Dependencies or behaviors resolved from a global source at the point of use. Rejected because the dependency is invisible at the call site and cannot be controlled without modifying global state.

**Internal flag checks** — A component reads configuration internally to decide whether optional behavior is active. Rejected because it distributes wiring decisions across the codebase rather than centralizing them at the composition root.

**Implicit contracts** — Structural compatibility inferred at runtime rather than declared. Rejected because contracts are invisible and errors surface at runtime rather than at definition time.

## Consequences

### Positive

- Behavior is fully visible from the wiring point without tracing runtime state.
- Optional features are independently controllable without side effects on other components.
- The composition root is the single place where configuration translates into behavior.

### Negative

- Wiring is more verbose than implicit alternatives.

### Risks

- The composition root may become difficult to navigate as the number of conditional wirings grows.

## Mandatory Rules

- Behavioral dependencies and contracts must be declared at the boundary where they are used, not resolved or inferred internally.
- Configuration decisions must be made at the composition root, not inside the components being configured.

## Allowed Changes

- Introducing new optional behaviors, provided they are declared explicitly at the wiring point.
- Reorganizing the composition root, provided wiring decisions remain centralized there.

## Forbidden Changes

- Moving wiring or configuration decisions inside components in a way that makes behavior invisible to the caller.

## Validation Criteria

- No component determines its own optional behavior based on configuration it resolves internally.
- All behavioral contracts between layers are declared, not inferred.

## Related Documents

- [ADR-001](001-clean-architecture.md)
- [ADR-003](003-dependency-inversion.md)
- [ADR-004](004-use-case-oriented-application-layer.md)

## Future Revisions

- If the composition root grows to the point where conditional wiring becomes unmanageable, revisit whether a more structured wiring mechanism is warranted.
