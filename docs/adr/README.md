# Architecture Decision Records

This directory contains the Architecture Decision Records (ADRs) for the Knowledge Support AI Agent.

## What is an ADR?

An ADR documents a significant architectural decision: the context that led to it, the decision itself, and its consequences. ADRs are immutable once accepted — they are never edited, only superseded.

## Rules

- ADRs represent the highest-priority architectural constraints in this project.
- No implementation or instruction may contradict an accepted ADR.
- If a request conflicts with an accepted ADR, flag the conflict before proceeding.

## Naming Convention

```
NNNN-short-title.md
```

Example: `0001-use-postgresql-as-primary-database.md`

## Status Values

- `Draft` - under discussion, not yet binding
- `Accepted` - binding, must be followed
- `Superseded by NNNN` - replaced by a newer ADR

## Template

```markdown
# NNNN - Title

## Status

Accepted

## Context

What situation or problem led to this decision?

## Decision

What was decided?

## Consequences

What are the trade-offs, implications, or follow-up actions?
```

## Index

| ID | Title | Status |
|----|-------|--------|
| — | No ADRs yet | — |
