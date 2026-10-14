
from abc import ABC, abstractmethod
from typing import Any, Iterator


class SourceConnector(ABC):
    """Common interface for all SyncForge source connectors."""

    @abstractmethod
    def connect(self) -> None:
        """Establish or verify a connection to the source."""
        pass

    @abstractmethod
    def read_records(self) -> Iterator[dict[str, Any]]:
        """Yield records from the source."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Release source resources."""
        pass
