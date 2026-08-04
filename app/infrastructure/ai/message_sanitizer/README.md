# message_sanitizer

Adapters for the `MessageSanitizer` port (`app/application/support/ports/message_sanitizer.py`).

Sanitizers are applied in `AnswerQuestion` before the user message enters the prompt pipeline, neutralizing content that could manipulate LLM behavior.

## Modules

- `regex.py` — `RegexMessageSanitizer`: applies a configurable list of regex patterns, replacing matches with a configurable replacement string
- `base.py` — `CompositeSanitizer`: applies a list of `MessageSanitizer` instances in order, passing the output of each as input to the next

## Rejection

When a message is deemed entirely invalid, an implementation should raise `MessageRejected(reason)` instead of returning a sanitized string. `AnswerQuestion` catches this, logs the reason at `WARNING` level, and returns a safe reply configured via `prompts_message_rejected_reply` in `prompts.ini`. The reason is never exposed to the client.


```python
from app.infrastructure.ai.message_sanitizer import CompositeSanitizer, RegexMessageSanitizer

sanitizer = CompositeSanitizer([
    RegexMessageSanitizer(patterns=[r"ignore previous instructions"], replacement="[removed]"),
    RegexMessageSanitizer(patterns=[r"you are now"]),
])

sanitized = sanitizer.sanitize(user_message)
```

To add a new sanitization strategy, implement the `MessageSanitizer` port and compose it via `CompositeSanitizer`.
