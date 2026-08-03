import uuid
from abc import abstractmethod

from sqlalchemy.orm import Session

from app.application.shared.ports.repository import CrudRepository


class SqlAlchemyRepository[OrmT, DomainT](CrudRepository[DomainT]):
    """Base class for SQLAlchemy repository adapters.

    Holds the session, the ORM class, and enforces a consistent ORM-to-domain
    mapping contract. Subclasses declare `_orm_class` once and implement
    `_to_domain` to translate ORM rows into domain objects. Default
    implementations of `get_by_id` and `delete` are provided using `_orm_class`
    and `_to_domain` — override only when the behaviour needs to differ.
    """

    _orm_class: type[OrmT]

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._db = db

    @abstractmethod
    def _to_domain(self, orm: OrmT) -> DomainT:
        """Translate an ORM instance into its domain model counterpart.

        Args:
            orm: The ORM row to translate.

        Returns:
            The corresponding domain model instance.
        """

    def _persist(self, **kwargs: object) -> DomainT:
        """Instantiate an ORM object, add it to the session,
        flush, and return its domain model.

        A UUID is always generated and assigned to `id`. Extra keyword arguments
        are forwarded to the ORM constructor.

        Args:
            **kwargs: Field values forwarded to `_orm_class`.

        Returns:
            The corresponding domain model instance.
        """
        orm = self._orm_class(id=uuid.uuid4(), **kwargs)  # type: ignore[call-arg]
        self._db.add(orm)
        self._db.flush()
        return self._to_domain(orm)

    def list(self) -> list[DomainT]:
        """Return all entities of this type.

        Returns:
            List of all domain instances.
        """
        return [self._to_domain(orm) for orm in self._db.query(self._orm_class).all()]

    def get_by_id(self, entity_id: uuid.UUID) -> DomainT | None:
        """Return the entity with the given id, or None if not found.

        Args:
            entity_id: UUID of the entity to retrieve.

        Returns:
            The matching domain instance, or None if it does not exist.
        """
        orm = self._db.get(self._orm_class, entity_id)
        return self._to_domain(orm) if orm is not None else None

    def update(self, entity: DomainT, **changes: object) -> DomainT:
        """Apply changes to a persisted entity and return the updated domain model.

        Args:
            entity: The domain entity to update.
            **changes: Fields to update on the ORM instance.

        Returns:
            The updated domain instance.

        Raises:
            ValueError: If the entity does not exist in the database.
        """
        orm = self._db.get(self._orm_class, getattr(entity, "id"))
        if orm is None:
            raise ValueError(f"{self._orm_class.__name__} not found")
        for key, value in changes.items():
            setattr(orm, key, value)
        self._db.flush()
        return self._to_domain(orm)

    def delete(self, entity_id: uuid.UUID) -> None:
        """Delete the entity with the given id, if it exists.

        Args:
            entity_id: UUID of the entity to delete.
        """
        orm = self._db.get(self._orm_class, entity_id)
        if orm is not None:
            self._db.delete(orm)
            self._db.flush()
