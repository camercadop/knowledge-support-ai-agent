from app.container.base import BaseContainer
from app.infrastructure.observability.instrumentation import InstrumentationConfig


def _make_container() -> BaseContainer:
    return BaseContainer()


# --- _singleton ---


def test_singleton_returns_same_instance_on_repeated_calls() -> None:
    container = _make_container()
    assert container._singleton(list) is container._singleton(list)


def test_singleton_calls_factory_only_once() -> None:
    container = _make_container()
    call_count = 0

    def factory() -> object:
        nonlocal call_count
        call_count += 1
        return object()

    container._singleton(factory)
    container._singleton(factory)
    assert call_count == 1


def test_singleton_different_factories_produce_separate_instances() -> None:
    container = _make_container()
    assert container._singleton(list) is not container._singleton(dict)


# --- _instrumentation ---


def test_instrumentation_returns_same_instance_on_repeated_calls() -> None:
    container = _make_container()
    config = InstrumentationConfig()
    assert container._instrumentation(config) is container._instrumentation(config)


def test_instrumentation_different_configs_produce_separate_instances() -> None:
    container = _make_container()
    config_a = InstrumentationConfig(timed_spans={"span_a": ("metric_a", None, "")})
    config_b = InstrumentationConfig(timed_spans={"span_b": ("metric_b", None, "")})
    assert container._instrumentation(config_a) is not container._instrumentation(config_b)
