from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class DomainEvent:
    """Base class for all domain events.

    Subclass this to define a concrete event. Always set occurred_at to the
    moment the event was raised, not when it is handled.
    """

    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
        kw_only=True,
    )
