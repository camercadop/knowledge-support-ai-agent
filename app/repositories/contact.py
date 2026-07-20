from sqlalchemy.orm import Session

from app.models.contact import Contact


class ContactRepository:
    """Handles persistence operations for Contact entities."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._db = db

    def get_or_create_by_phone(self, phone: str) -> Contact:
        """Return the contact with the given phone, creating one if it does not exist.

        Flushes the session so the new contact gets an id before commit.
        """
        contact = self._db.query(Contact).filter(Contact.phone == phone).first()
        if contact is None:
            contact = Contact(phone=phone)
            self._db.add(contact)
            self._db.flush()
        return contact
