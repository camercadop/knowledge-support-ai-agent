from typing import Protocol

from app.application.shared.events.domain_event import DomainEvent


class EventHandler[TEvent: DomainEvent](Protocol):
    """Contract for handling a specific domain event type.

    Implement this in infrastructure to react to a published event.
    Each handler is responsible for a single event type.
    """

    def handle(self, event: TEvent) -> None:
        """React to the given domain event.

        Args:
            event: The domain event to handle.
        """
