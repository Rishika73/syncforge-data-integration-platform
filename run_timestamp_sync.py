from syncforge.database import get_database_url

import os
from datetime import datetime, timezone

from syncforge.connectors.postgres import PostgreSQLDestination


DATABASE_URL = get_database_url()

destination = PostgreSQLDestination(DATABASE_URL)

source_name = "timestamp_customers_demo"
sync_name = "timestamp_customers_demo_sync"

initial_records = [
    {
        "id": 101,
        "name": "Ava",
        "city": "New York",
        "updated_at": "2026-10-10T09:00:00Z",
    },
    {
        "id": 102,
        "name": "Noah",
        "city": "Chicago",
        "updated_at": "2026-10-10T10:00:00Z",
    },
]

updated_records = [
    {
        "id": 101,
        "name": "Ava",
        "city": "Boston",
        "updated_at": "2026-10-12T11:00:00Z",
    },
    {
        "id": 103,
        "name": "Mia",
        "city": "Seattle",
        "updated_at": "2026-10-12T12:00:00Z",
    },
]

try:
    destination.connect()

    first_count = destination.write_with_timestamp_checkpoint(
        records=initial_records,
        source_name=source_name,
        sync_name=sync_name,
    )

    print("First sync:", first_count)

    second_count = destination.write_with_timestamp_checkpoint(
        records=updated_records,
        source_name=source_name,
        sync_name=sync_name,
    )

    print("Second sync:", second_count)

    with destination.connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, payload->>'name', payload->>'city'
            FROM api_records
            WHERE source_name = %s
            ORDER BY id
            """,
            (source_name,),
        )

        rows = cursor.fetchall()

    for row in rows:
        print(row)

finally:
    destination.close()
