
import json
import os
from pathlib import Path
from typing import Any

from syncforge.connectors.base import SourceConnector
from syncforge.state.checkpoint import CheckpointStore


class IncrementalSyncEngine:

    def __init__(
        self,
        source: SourceConnector,
        checkpoint_store: CheckpointStore,
        sync_name: str,
        destination_path: str,
    ):
        self.source = source
        self.checkpoint_store = checkpoint_store
        self.sync_name = sync_name
        self.destination_path = Path(destination_path)

    def run(self) -> int:
        last_id = self.checkpoint_store.get(self.sync_name)

        # Read existing destination records by ID.
        records_by_id: dict[int, dict[str, Any]] = {}

        if self.destination_path.exists():
            with self.destination_path.open(
                "r", encoding="utf-8"
            ) as file:
                for line in file:
                    if line.strip():
                        record = json.loads(line)
                        records_by_id[record["id"]] = record

        new_records: list[dict[str, Any]] = []

        self.source.connect()

        try:
            for record in self.source.read_records():
                record_id = record["id"]

                if type(record_id) is not int:
                    raise ValueError(
                        "Record IDs must be integers"
                    )

                if record_id > last_id:
                    new_records.append(record)

        finally:
            self.source.close()

        if not new_records:
            return 0

        # Upsert records instead of appending duplicates.
        for record in new_records:
            records_by_id[record["id"]] = record

        self.destination_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp_path = self.destination_path.with_suffix(
            self.destination_path.suffix + ".tmp"
        )

        try:
            with temp_path.open(
                "w", encoding="utf-8"
            ) as output:
                for record_id in sorted(records_by_id):
                    output.write(
                        json.dumps(records_by_id[record_id])
                        + "\n"
                    )

                output.flush()
                os.fsync(output.fileno())

            os.replace(temp_path, self.destination_path)

        finally:
            temp_path.unlink(missing_ok=True)

        new_last_id = max(
            record["id"] for record in new_records
        )

        self.checkpoint_store.save(
            self.sync_name,
            new_last_id,
        )

        return len(new_records)
