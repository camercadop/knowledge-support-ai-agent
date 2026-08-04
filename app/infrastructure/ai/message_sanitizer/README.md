# message_sanitizer

Adapters for the `MessageSanitizer` port (`app/application/support/ports/message_sanitizer.py`).

Sanitizers are applied in `AnswerQuestion` before the user message enters the prompt pipeline, neutralizing content that could manipulate LLM behavior.

## Modules

- `regex.py` — `RegexMessageSanitizer`: applies a configurable list of regex patterns, replacing matches with a configurable replacement string
- `base.py` — `CompositeSanitizer`: applies a list of `MessageSanitizer` instances in order, passing the output of each as input to the next

## Usage

```python
from app.infrastructure.ai.message_sanitizer import CompositeSanitizer, RegexMessageSanitizer

sanitizer = CompositeSanitizer([
    RegexMessageSanitizer(patterns=[r"ignore previous instructions"], replacement="[removed]"),
    RegexMessageSanitizer(patterns=[r"you are now"]),
])

sanitized = sanitizer.sanitize(user_message)
```

To add a new sanitization strategy, implement the `MessageSanitizer` port and compose it via `CompositeSanitizer`.
