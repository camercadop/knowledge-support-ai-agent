from collections import defaultdict
from typing import Any

from app.application.shared.events.domain_event import DomainEvent
from app.application.shared.events.event_handler import EventHandler


class InMemoryEventBus:
    """EventPublisher implementation that dispatches events to in-process handlers.

    Handlers are registered per event type. On publish, all handlers registered
    for the event's exact type are called in registration order. Unhandled event
    types are silently ignored.
    """

    def __init__(self) -> None:
        """Initialize with an empty handler registry."""
        self._handlers: dict[type, list[EventHandler[Any]]] = defaultdict(list)

    def subscribe[TEvent: DomainEvent](
        self, event_type: type[TEvent], handler: EventHandler[TEvent]
    ) -> None:
        """Subscribe a handler to a specific event type.

        Args:
            event_type: The domain event class to subscribe to.
            handler: The handler to invoke when an event of that type is published.
        """
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        """Dispatch the event to all handlers registered for its type.

        Args:
            event: The domain event to publish.
        """
        for handler in self._handlers[type(event)]:
            handler.handle(event)
