
from typing import Literal

from syncforge.connectors.base import SourceConnector
from syncforge.connectors.postgres import PostgreSQLDestination
from syncforge.connectors.rest_api import RESTAPIConnector
from syncforge.engine.batch import iter_batches
from syncforge.engine.ordering import validate_increasing_ids


class GenericSyncEngine:
    """
    Generic ingestion engine supporting two modes:

    incremental:
        Append-only records with increasing IDs.
        Uses transactional PostgreSQL checkpoints.

    snapshot:
        Re-imports records and performs upserts.
        Does not advance ID checkpoints.
    """

    def __init__(
        self,
        source: SourceConnector,
        destination: PostgreSQLDestination,
        source_name: str,
        sync_name: str,
        batch_size: int = 1000,
        sync_mode: Literal[
            "incremental", "snapshot"
        ] = "incremental",
    ):
        if batch_size <= 0:
            raise ValueError(
                "batch_size must be positive"
            )

        if sync_mode not in ("incremental", "snapshot"):
            raise ValueError(
                "Unsupported synchronization mode"
            )

        self.source = source
        self.destination = destination
        self.source_name = source_name
        self.sync_name = sync_name
        self.batch_size = batch_size
        self.sync_mode = sync_mode

    def run(self) -> int:
        total_processed = 0

        try:
            self.destination.connect()

            if self.sync_mode == "incremental":
                last_id = self.destination.get_checkpoint(
                    self.sync_name
                )

                if isinstance(
                    self.source, RESTAPIConnector
                ):
                    self.source.since_id = last_id

            else:
                last_id = 0

                if isinstance(
                    self.source, RESTAPIConnector
                ):
                    self.source.since_id = None

            self.source.connect()

            records = self.source.read_records()

            if self.sync_mode == "incremental":
                records = validate_increasing_ids(
                    records,
                    starting_id=last_id,
                )

            for batch in iter_batches(
                records,
                self.batch_size,
            ):
                if self.sync_mode == "incremental":
                    count = (
                        self.destination
                        .write_with_checkpoint(
                            records=batch,
                            source_name=self.source_name,
                            sync_name=self.sync_name,
                        )
                    )
                else:
                    count = self.destination.write_records(
                        records=batch,
                        source_name=self.source_name,
                    )

                total_processed += count

            return total_processed

        finally:
            self.source.close()
            self.destination.close()
