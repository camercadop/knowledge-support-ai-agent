import logging
import uuid

from cachetools import TTLCache, cached
from cachetools.keys import hashkey

from app.application.support.ports.repositories.knowledge_base_config import (
    AbstractKnowledgeBaseConfigRepository,
)
from app.config.settings import settings
from app.infrastructure.database.sqlalchemy.postgresql.engine import SessionLocal
from app.infrastructure.database.sqlalchemy.postgresql.unit_of_work.base import (
    SqlAlchemyUnitOfWork,
)

logger = logging.getLogger(__name__)

_KB_CONFIG_TTL = 300
_kb_config_cache: TTLCache[object, dict[str, str]] = TTLCache(
    maxsize=256, ttl=_KB_CONFIG_TTL
)


@cached(cache=_kb_config_cache, key=lambda repo, kb_id: hashkey(kb_id))
def _load_kb_config(
    repo: AbstractKnowledgeBaseConfigRepository, kb_id: uuid.UUID
) -> dict[str, str]:
    """Load and cache KB config for the given knowledge base ID.

    Args:
        repo: The repository used to fetch config entries.
        kb_id: The knowledge base to load config for.

    Returns:
        A dict mapping each config key to its value.
    """
    return repo.get_by_knowledge_base_id(kb_id)


def _open_kb_config(kb_id: uuid.UUID) -> dict[str, str]:
    """Open a session, load and return the KB config dict, then close the session.

    Args:
        kb_id: The knowledge base to load config for.

    Returns:
        A dict mapping each config key to its value.
    """
    db = SessionLocal()
    try:
        uow = SqlAlchemyUnitOfWork(db)
        repo = uow.get(AbstractKnowledgeBaseConfigRepository)  # type: ignore[type-abstract]
        return _load_kb_config(repo, kb_id)
    finally:
        db.close()


def resolve_setting(key: str, kb_id: uuid.UUID | None) -> object:
    """Return the effective value for a settings key, with KB config taking priority.

    Loads the knowledge base config from the database and returns the value for
    the given key if present, casting it to the type declared on ``Settings``.
    Falls back to the global ``settings`` value when the key is absent or the
    cast fails.

    Args:
        key: The ``Settings`` field name to resolve.
        kb_id: The knowledge base whose config overrides are checked first.
            When None, the global setting value is returned immediately.

    Returns:
        The KB override cast to the correct type, or the global setting value.

    Raises:
        AttributeError: If ``key`` does not exist on ``Settings``.
    """
    global_value = getattr(settings, key)
    if kb_id is None:
        return global_value

    kb_config = _open_kb_config(kb_id)
    if key not in kb_config:
        return global_value

    try:
        return type(global_value)(kb_config[key])
    except ValueError, TypeError:
        logger.warning(
            "Failed to cast KB config key %s to %s, using global setting",
            key,
            type(global_value).__name__,
        )
        return global_value


def resolve_settings_batch(
    keys: list[str], kb_id: uuid.UUID | None
) -> dict[str, object]:
    """Resolve multiple settings keys at once, with KB config taking priority.

    Loads the KB config once and resolves all requested keys in a single DB call.
    Falls back to the global ``settings`` value for each key that is absent or
    fails to cast.

    Args:
        keys: List of ``Settings`` field names to resolve.
        kb_id: The knowledge base whose config overrides are checked first.
            When None, all values are returned from the global settings.

    Returns:
        A dict mapping each key to its resolved value.

    Raises:
        AttributeError: If any key does not exist on ``Settings``.
    """
    if kb_id is None:
        return {key: getattr(settings, key) for key in keys}

    kb_config = _open_kb_config(kb_id)
    result: dict[str, object] = {}
    for key in keys:
        global_value = getattr(settings, key)
        if key not in kb_config:
            result[key] = global_value
            continue
        try:
            result[key] = type(global_value)(kb_config[key])
        except ValueError, TypeError:
            logger.warning(
                "Failed to cast KB config key %s to %s, using global setting",
                key,
                type(global_value).__name__,
            )
            result[key] = global_value
    return result
