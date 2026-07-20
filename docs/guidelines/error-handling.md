# Error Handling

This document describes how to handle errors across the project's layers.

## Principles

- The API layer translates errors into HTTP responses.
- Use cases raise plain Python exceptions — they have no knowledge of HTTP.
- Infrastructure clients let SDK exceptions propagate unless a meaningful translation is needed.

## API Layer

Catch use case exceptions in the route handler and raise `HTTPException`:

```python
from fastapi import HTTPException

@router.post("/my-resource", response_model=MyResponse)
def my_endpoint(request: MyRequest, db: Session = Depends(get_db)) -> MyResponse:
    try:
        result = use_case.handle(request.field)
    except MyEntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return MyResponse(field=result)
```

## Use Case Layer

Raise domain-specific exceptions for expected failure conditions. Define them in the same module as the use case:

```python
class MyEntityNotFoundError(Exception):
    """Raised when the requested entity does not exist."""
```

Do not raise `HTTPException` or any framework-specific exception from a use case.

## Infrastructure Layer

Let SDK exceptions propagate to the use case unless you need to normalize them across providers. If normalization is needed, define a port-level exception and raise it from the implementation:

```python
# in the port
class ChatModelError(Exception):
    """Raised when the chat model fails to generate a response."""

# in the implementation
try:
    response = self._client.responses.create(...)
except OpenAIError as exc:
    raise ChatModelError("LLM call failed") from exc
```

## What Not to Do

- Do not catch broad `Exception` unless logging and re-raising.
- Do not swallow exceptions silently.
- Do not return `None` to signal a failure — raise an exception.
- Do not let infrastructure exceptions leak into the API response unhandled.
