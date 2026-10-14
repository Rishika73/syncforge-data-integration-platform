
from datetime import datetime
from typing import Optional

import psycopg


class TimestampCheckpointStore:
    """
    Manages timestamp-based checkpoints in PostgreSQL.
    """

    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def get(
        self,
        sync_name: str,
    ) -> Optional[tuple[datetime, int]]:
        """
        Return the last timestamp and record ID.
        Returns None if no checkpoint exists.
        """
        with psycopg.connect(
            self.connection_string
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT last_updated_at, last_record_id
                    FROM timestamp_checkpoints
                    WHERE sync_name = %s
                    """,
                    (sync_name,),
                )

                row = cursor.fetchone()

        if row is None or row[0] is None:
            return None

        return row[0], row[1]

    def save(
        self,
        sync_name: str,
        updated_at: datetime,
        record_id: int,
    ) -> None:
        """
        Insert or update the timestamp checkpoint.
        """
        if updated_at.tzinfo is None:
            raise ValueError(
                "updated_at must include a timezone"
            )

        if type(record_id) is not int:
            raise ValueError(
                "record_id must be an integer"
            )

        with psycopg.connect(
            self.connection_string
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO timestamp_checkpoints
                        (
                            sync_name,
                            last_updated_at,
                            last_record_id
                        )
                    VALUES (%s, %s, %s)
                    ON CONFLICT (sync_name)
                    DO UPDATE SET
                        last_updated_at = EXCLUDED.last_updated_at,
                        last_record_id = EXCLUDED.last_record_id,
                        checkpoint_saved_at = CURRENT_TIMESTAMP
                    """,
                    (
                        sync_name,
                        updated_at,
                        record_id,
                    ),
                )
