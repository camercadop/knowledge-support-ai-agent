from sqlalchemy.orm import Session

from app.application.models.contact import Contact
from app.application.ports.repositories.contact import AbstractContactRepository
from app.infrastructure.database.sqlalchemy.postgresql.models.contact import Contact as ContactORM


class ContactRepository(AbstractContactRepository):
    """Handles persistence operations for Contact entities."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._db = db

    def get_or_create_by_phone(self, phone: str) -> Contact:
        """Return the contact with the given phone, creating one if it does not exist.

        Flushes the session so the new contact gets an id before commit.
        """
        orm = self._db.query(ContactORM).filter(ContactORM.phone == phone).first()
        if orm is None:
            orm = ContactORM(phone=phone)
            self._db.add(orm)
            self._db.flush()
        return Contact(id=orm.id, phone=orm.phone)
