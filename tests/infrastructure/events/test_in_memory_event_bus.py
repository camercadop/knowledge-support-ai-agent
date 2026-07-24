import uuid
from dataclasses import dataclass

from app.application.shared.events.domain_event import DomainEvent
from app.infrastructure.events.in_memory_event_bus import InMemoryEventBus


@dataclass(frozen=True)
class OrderPlaced(DomainEvent):
    order_id: uuid.UUID


@dataclass(frozen=True)
class OrderCancelled(DomainEvent):
    order_id: uuid.UUID


class _RecordingHandler:
    def __init__(self) -> None:
        self.received: list[DomainEvent] = []

    def handle(self, event: DomainEvent) -> None:
        self.received.append(event)


# --- publish ---


def test_registered_handler_receives_event() -> None:
    bus = InMemoryEventBus()
    handler = _RecordingHandler()
    event = OrderPlaced(order_id=uuid.uuid4())

    bus.register(OrderPlaced, handler)
    bus.publish(event)

    assert handler.received == [event]


def test_unregistered_event_type_is_silently_ignored() -> None:
    bus = InMemoryEventBus()
    handler = _RecordingHandler()
    bus.register(OrderPlaced, handler)

    bus.publish(OrderCancelled(order_id=uuid.uuid4()))

    assert handler.received == []


def test_multiple_handlers_for_same_event_all_called() -> None:
    bus = InMemoryEventBus()
    handler_a = _RecordingHandler()
    handler_b = _RecordingHandler()
    event = OrderPlaced(order_id=uuid.uuid4())

    bus.register(OrderPlaced, handler_a)
    bus.register(OrderPlaced, handler_b)
    bus.publish(event)

    assert handler_a.received == [event]
    assert handler_b.received == [event]


def test_handlers_called_in_registration_order() -> None:
    bus = InMemoryEventBus()
    call_order: list[str] = []

    class _OrderedHandler:
        def __init__(self, name: str) -> None:
            self._name = name

        def handle(self, event: DomainEvent) -> None:
            call_order.append(self._name)

    bus.register(OrderPlaced, _OrderedHandler("first"))
    bus.register(OrderPlaced, _OrderedHandler("second"))
    bus.publish(OrderPlaced(order_id=uuid.uuid4()))

    assert call_order == ["first", "second"]


def test_handler_for_one_type_does_not_receive_other_type() -> None:
    bus = InMemoryEventBus()
    placed_handler = _RecordingHandler()
    cancelled_handler = _RecordingHandler()

    bus.register(OrderPlaced, placed_handler)
    bus.register(OrderCancelled, cancelled_handler)

    bus.publish(OrderPlaced(order_id=uuid.uuid4()))

    assert len(placed_handler.received) == 1
    assert len(cancelled_handler.received) == 0


def test_publish_multiple_events_accumulates_in_handler() -> None:
    bus = InMemoryEventBus()
    handler = _RecordingHandler()
    bus.register(OrderPlaced, handler)

    bus.publish(OrderPlaced(order_id=uuid.uuid4()))
    bus.publish(OrderPlaced(order_id=uuid.uuid4()))

    assert len(handler.received) == 2
