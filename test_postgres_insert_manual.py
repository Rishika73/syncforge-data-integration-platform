from syncforge.database import get_database_url

import os

from syncforge.connectors.postgres import PostgreSQLDestination


destination = PostgreSQLDestination(
    get_database_url()
)

records = [
    {"id": 1, "title": "First SyncForge Record"},
    {"id": 2, "title": "Second SyncForge Record"},
    {"id": 3, "title": "Third SyncForge Record"},
]

try:
    destination.connect()

    count = destination.write_records(
        records,
        source_name="manual_test",
    )

    print(f"Records written: {count}")

finally:
    destination.close()
