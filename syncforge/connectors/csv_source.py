
import csv
from pathlib import Path
from typing import Any, Iterator

from syncforge.connectors.base import SourceConnector


class CSVSourceConnector(SourceConnector):
    """Read CSV files through the SyncForge connector interface."""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.connected = False

    def connect(self) -> None:
        if not self.file_path.is_file():
            raise FileNotFoundError(
                f"CSV file not found: {self.file_path}"
            )

        self.connected = True

    def read_records(self) -> Iterator[dict[str, Any]]:
        if not self.connected:
            raise RuntimeError("Call connect() first")

        with self.file_path.open(
            "r", encoding="utf-8-sig", newline=""
        ) as file:
            reader = csv.DictReader(file)

            if not reader.fieldnames:
                raise ValueError("CSV file must have a header")

            if "id" not in reader.fieldnames:
                raise ValueError(
                    "CSV file must contain an 'id' column"
                )

            for row in reader:
                if None in row:
                    raise ValueError("Malformed CSV row")

                try:
                    record_id = int(row["id"])
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f"Invalid record ID: {row['id']}"
                    ) from exc

                if record_id < 0:
                    raise ValueError("ID cannot be negative")

                row["id"] = record_id
                yield row

    def close(self) -> None:
        self.connected = False
