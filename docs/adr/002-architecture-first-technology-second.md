# ADR-002: Architecture First, Technology Second

## Status

Accepted

## Context

Technology choices — frameworks, libraries, databases, AI providers — change over time. If the system's structure is shaped around a specific technology, replacing or upgrading that technology requires restructuring the entire codebase.

The platform integrates with several external systems that are likely to evolve: AI providers, communication channels, and data stores. Locking the architecture to any one of them creates long-term maintenance risk.

## Decision

Architectural decisions are made independently of technology choices. The structure of the system — its layers, boundaries, and contracts — is defined first. Technology is then selected to fulfill those contracts, not to define them.

## Rationale

**Benefits** — The system remains adaptable. A technology can be swapped without restructuring the architecture. Architectural decisions are evaluated on their own merits, not constrained by what a framework makes easy.

**Tradeoffs** — More upfront design effort. Some technology-native conveniences are deliberately avoided to preserve architectural independence.

**Assumptions** — The system will outlive its initial technology choices. If the system is a short-lived prototype, this discipline adds unnecessary overhead.

**Risks** — Abstractions may be designed without enough knowledge of the underlying technology, leading to leaky or ill-fitting contracts.

## Alternatives Considered

**Technology-driven design** — Let the framework or provider dictate the structure. Rejected because it couples the system's shape to a vendor's API surface, making future changes expensive.

**Decide architecture and technology together** — Co-design both simultaneously. Rejected because it introduces implicit technology assumptions into architectural decisions that should remain independent.

## Consequences

### Positive

- Technology can be replaced without restructuring the system.
- Architectural decisions are evaluated on their own merits.
- The system is easier to reason about independently of any specific tool.

### Negative

- Requires more deliberate design effort upfront.
- Some framework conveniences must be foregone to preserve independence.

### Risks

- Abstractions designed without sufficient technology knowledge may not fit well in practice.

## Mandatory Rules

- Architectural boundaries and contracts must be defined before selecting the technology that implements them.
- No layer's structure may be shaped by the API surface of an external library or provider.

## Allowed Changes

- Replacing a technology implementation as long as it fulfills the existing architectural contract.
- Introducing new technologies within an existing layer without altering the layer's contract.

## Forbidden Changes

- Reshaping an architectural boundary to accommodate a technology's constraints without a superseding ADR.
- Exposing technology-specific types or abstractions across layer boundaries.

## Validation Criteria

- Inner layers contain no imports from external libraries or providers.
- Contracts between layers are expressed in domain terms, not technology terms.

## Related Documents

- [ADR-001](001-clean-architecture.md)

## Future Revisions

- If the system stabilizes around a single long-lived technology stack with no foreseeable changes, revisit whether this level of abstraction remains justified.
