from app.container.support import SupportContainer


class ApplicationContainer:
    """Top-level application-scoped container.

    Created once at startup and stored on app.state. Composes all
    domain-scoped containers. Route handlers access the specific domain
    container they need via the corresponding attribute.
    """

    def __init__(self) -> None:
        self.support = SupportContainer()
