# prompt_builder

This sub-package implements the `PromptBuilder` port. Each module provides a distinct prompt assembly strategy.

## Modules

- `default.py` — `DefaultPromptBuilder`; assembles the provider-agnostic message list by prepending a system message that combines the base instructions with either the retrieved knowledge excerpts or a no-context fallback instruction.
