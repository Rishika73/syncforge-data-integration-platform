
from typing import Any

import psycopg
from psycopg.types.json import Jsonb


class PostgreSQLDestination:
    """
    PostgreSQL destination connector for SyncForge.

    Supports:
    - Database connections
    - Record upserts
    - Multiple data sources
    - Checkpoint retrieval
    - Transactional incremental synchronization
    """

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None

    def connect(self) -> None:
        """Connect to PostgreSQL using explicit transactions."""
        self.connection = psycopg.connect(
            self.connection_string,
            autocommit=True,
        )

    def write_records(
        self,
        records: list[dict[str, Any]],
        source_name: str,
    ) -> int:
        """
        Insert or update records in PostgreSQL.
        Uses a composite key (source_name, id).
        """
        if self.connection is None:
            raise RuntimeError("Call connect() first")

        with self.connection.transaction():
            with self.connection.cursor() as cursor:
                for record in records:
                    cursor.execute(
                        """
                        INSERT INTO api_records
                            (id, source_name, payload)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (source_name, id)
                        DO UPDATE SET
                            payload = EXCLUDED.payload,
                            synced_at = CURRENT_TIMESTAMP
                        """,
                        (
                            record["id"],
                            source_name,
                            Jsonb(record),
                        ),
                    )

        return len(records)

    def get_checkpoint(self, sync_name: str) -> int:
        """
        Retrieve the last successfully processed
        record ID for a synchronization job.
        """
        if self.connection is None:
            raise RuntimeError("Call connect() first")

        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT last_id
                FROM sync_checkpoints
                WHERE sync_name = %s
                """,
                (sync_name,),
            )

            row = cursor.fetchone()

        return row[0] if row else 0

    def write_with_checkpoint(
        self,
        records: list[dict[str, Any]],
        source_name: str,
        sync_name: str,
    ) -> int:
        """
        Atomically upsert new records and save
        the synchronization checkpoint.

        The checkpoint advances only when the
        database transaction succeeds.
        """
        if self.connection is None:
            raise RuntimeError("Call connect() first")

        if not records:
            return 0

        # Validate IDs before starting the transaction.
        for record in records:
            if type(record.get("id")) is not int:
                raise ValueError(
                    "Record IDs must be integers"
                )

            if record["id"] < 0:
                raise ValueError(
                    "Record IDs cannot be negative"
                )

        with self.connection.transaction():
            with self.connection.cursor() as cursor:

                # Create checkpoint row if missing.
                cursor.execute(
                    """
                    INSERT INTO sync_checkpoints
                        (sync_name, last_id)
                    VALUES (%s, 0)
                    ON CONFLICT (sync_name) DO NOTHING
                    """,
                    (sync_name,),
                )

                # Lock the checkpoint for this sync.
                cursor.execute(
                    """
                    SELECT last_id
                    FROM sync_checkpoints
                    WHERE sync_name = %s
                    FOR UPDATE
                    """,
                    (sync_name,),
                )

                last_id = cursor.fetchone()[0]

                # Only process records newer than
                # the saved checkpoint.
                new_records = [
                    record
                    for record in records
                    if record["id"] > last_id
                ]

                if not new_records:
                    return 0

                # Insert or update records.
                for record in new_records:
                    cursor.execute(
                        """
                        INSERT INTO api_records
                            (id, source_name, payload)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (source_name, id)
                        DO UPDATE SET
                            payload = EXCLUDED.payload,
                            synced_at = CURRENT_TIMESTAMP
                        """,
                        (
                            record["id"],
                            source_name,
                            Jsonb(record),
                        ),
                    )

                # Calculate the highest processed ID.
                new_last_id = max(
                    record["id"]
                    for record in new_records
                )

                # Save checkpoint inside the same transaction.
                cursor.execute(
                    """
                    UPDATE sync_checkpoints
                    SET last_id = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE sync_name = %s
                    """,
                    (
                        new_last_id,
                        sync_name,
                    ),
                )

        return len(new_records)

    def write_with_timestamp_checkpoint(
        self,
        records: list[dict[str, Any]],
        source_name: str,
        sync_name: str,
    ) -> int:
        """Atomically upsert changed records and checkpoint."""
        from syncforge.engine.timestamp_filter import (
            filter_updated_records,
            parse_timestamp,
        )

        if self.connection is None:
            raise RuntimeError("Call connect() first")

        with self.connection.transaction():
            with self.connection.cursor() as cursor:
                # Ensure there is a checkpoint row to lock.
                cursor.execute(
                    """
                    INSERT INTO timestamp_checkpoints (sync_name)
                    VALUES (%s)
                    ON CONFLICT (sync_name) DO NOTHING
                    """,
                    (sync_name,),
                )

                cursor.execute(
                    """
                    SELECT last_updated_at, last_record_id
                    FROM timestamp_checkpoints
                    WHERE sync_name = %s
                    FOR UPDATE
                    """,
                    (sync_name,),
                )

                row = cursor.fetchone()
                checkpoint = (
                    (row[0], row[1])
                    if row[0] is not None
                    else None
                )

                # Select records newer than the checkpoint.
                changed = list(
                    filter_updated_records(
                        iter(records),
                        checkpoint,
                    )
                )

                if not changed:
                    return 0

                for record in changed:
                    cursor.execute(
                        """
                        INSERT INTO api_records
                            (id, source_name, payload)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (source_name, id)
                        DO UPDATE SET
                            payload = EXCLUDED.payload,
                            synced_at = CURRENT_TIMESTAMP
                        """,
                        (
                            record["id"],
                            source_name,
                            Jsonb(record),
                        ),
                    )

                # Find the newest timestamp/ID pair.
                newest = max(
                    changed,
                    key=lambda record: (
                        parse_timestamp(record["updated_at"]),
                        record["id"],
                    ),
                )

                cursor.execute(
                    """
                    UPDATE timestamp_checkpoints
                    SET last_updated_at = %s,
                        last_record_id = %s,
                        checkpoint_saved_at = CURRENT_TIMESTAMP
                    WHERE sync_name = %s
                    """,
                    (
                        parse_timestamp(newest["updated_at"]),
                        newest["id"],
                        sync_name,
                    ),
                )

        return len(changed)

    def close(self) -> None:
        """Close the PostgreSQL connection."""
        if self.connection is not None:
            self.connection.close()
            self.connection = None
