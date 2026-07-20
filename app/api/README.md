# api

This package is the HTTP entry point of the application. It contains FastAPI route handlers organized by feature area. Each module defines an `APIRouter` that is mounted in `app.main`. Handlers are intentionally thin: they validate the incoming request via schemas, delegate all business logic to the application layer, and return the serialized response. No domain logic lives here.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/chat` | Receive a user message and return the assistant reply |

## Request / Response flow

```mermaid
sequenceDiagram
    participant Client
    participant POST /chat
    participant ChatService

    Client->>POST /chat: {phone, message}
    POST /chat->>ChatService: handle(phone, message)
    ChatService-->>POST /chat: reply: str
    POST /chat-->>Client: {reply}
```

## Modules

- `chat.py` — `/chat` endpoint; delegates all logic to `ChatService`
