import logging

logger = logging.getLogger(__name__)

_REGISTRY: dict[type, type] = {}


def repository(port: type) -> type:
    """Register a concrete repository class against its port type.

    Attach this decorator to a SqlAlchemyRepository subclass to make it
    discoverable by ``get_repository``. Each port must be unique across
    all registered implementations.

    Args:
        port: The abstract repository port this class implements.

    Raises:
        ValueError: If a repository for the given port is already registered.

    Example:
        @repository(AbstractDocumentRepository)
        class DocumentRepository(SqlAlchemyRepository): ...
    """

    def decorator(cls: type) -> type:
        if port in _REGISTRY:
            raise ValueError(
                f"A repository for port '{port.__name__}' is already registered."
            )
        _REGISTRY[port] = cls
        return cls

    return decorator  # type: ignore[return-value]


def get_repository(port: type) -> type:
    """Return the concrete repository class registered for the given port.

    Args:
        port: The abstract repository port to look up.

    Returns:
        The concrete repository class registered for ``port``.

    Raises:
        KeyError: If no repository is registered for the given port.
    """
    if port not in _REGISTRY:
        raise KeyError(
            f"No repository registered for port '{port.__name__}'. "
            f"Available ports: {sorted(p.__name__ for p in _REGISTRY)}"
        )
    return _REGISTRY[port]
