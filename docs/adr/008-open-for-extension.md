# ADR-008: Open for Extension

## Status

Accepted

## Context

As the system grows, new behavioral variants are expected to be added across multiple dimensions. Without a deliberate extensibility strategy, each new variant requires modifying existing code, increasing the risk of regressions and making the codebase harder to maintain.

## Decision

New behavior must be added by adding code, not by modifying existing code. Existing modules, classes, and functions must remain closed to modification when the change is purely additive.

## Rationale

Keeping existing code closed to modification reduces the risk of regressions, narrows the scope of code review, and makes the system easier to reason about over time. Each addition is self-contained and does not require understanding or touching unrelated code.

## Alternatives Considered

**Modifying existing dispatch logic for each new variant** — Simple for a small number of variants but does not scale. Every addition touches existing code, increasing coupling and regression risk.

## Consequences

### Positive

- Additions are isolated and do not affect existing behavior.
- The scope of each change is minimal and reviewable in isolation.

### Negative

- Requires upfront design discipline to define stable extension points.

### Risks

- Poorly defined extension points force modifications anyway, undermining the principle.

## Mandatory Rules

- New behavioral variants must be added without modifying existing modules.
- Extension points must be defined before new variants are introduced.

## Allowed Changes

- Adding new implementations alongside existing ones.
- Introducing new extension points for new behavioral dimensions.

## Forbidden Changes

- Modifying an existing module solely to accommodate a new variant when an extension point already exists.

## Validation Criteria

- No existing module is modified when a new behavioral variant is added.

## Related Documents

- [ADR-001](001-clean-architecture.md)
- [ADR-003](003-dependency-inversion.md)

## Future Revisions

- If the cost of maintaining extension points outweighs the benefit for a given dimension, revisit whether the principle applies there.
