from typing import Protocol

from app.application.shared.events.domain_event import DomainEvent


class EventPublisher(Protocol):
    """Contract for publishing domain events.

    Use this in application-layer use cases to remain decoupled from any
    specific event bus implementation. Implementations live in
    infrastructure/events/.
    """

    def publish(self, event: DomainEvent) -> None:
        """Publish a domain event to all registered subscribers.

        Args:
            event: The domain event to publish.
        """
