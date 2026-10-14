
from syncforge.connectors.postgres import PostgreSQLDestination
from syncforge.connectors.rest_api import RESTAPIConnector


class PostgreSQLSyncEngine:
    """
    Coordinates incremental REST API ingestion
    and transactional PostgreSQL writes.
    """

    def __init__(
        self,
        source: RESTAPIConnector,
        destination: PostgreSQLDestination,
        source_name: str,
        sync_name: str,
    ):
        self.source = source
        self.destination = destination
        self.source_name = source_name
        self.sync_name = sync_name

    def run(self) -> int:
        source_connected = False
        destination_connected = False

        try:
            self.destination.connect()
            destination_connected = True

            # Load checkpoint from PostgreSQL.
            last_id = self.destination.get_checkpoint(
                self.sync_name
            )

            # Configure the API connector.
            self.source.since_id = last_id

            self.source.connect()
            source_connected = True

            # Fetch records newer than the checkpoint.
            records = list(self.source.read_records())

            # Atomically write records and checkpoint.
            count = self.destination.write_with_checkpoint(
                records=records,
                source_name=self.source_name,
                sync_name=self.sync_name,
            )

            return count

        finally:
            if source_connected:
                self.source.close()

            if destination_connected:
                self.destination.close()
