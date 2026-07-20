from abc import ABC, abstractmethod

from app.application.models.contact import Contact


class AbstractContactRepository(ABC):
    """Port that defines the contract for contact persistence.

    Implementations live in infrastructure/database/repositories/.
    """

    @abstractmethod
    def get_or_create_by_phone(self, phone: str) -> Contact:
        """Return the contact with the given phone, creating one if it does not exist.
        """
