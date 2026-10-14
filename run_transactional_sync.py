from syncforge.database import get_database_url

import os

from syncforge.connectors.rest_api import RESTAPIConnector
from syncforge.connectors.postgres import PostgreSQLDestination


source = RESTAPIConnector(
    "https://jsonplaceholder.typicode.com/posts",
    page_size=20,
)

destination = PostgreSQLDestination(
    get_database_url()
)

try:
    source.connect()
    destination.connect()

    records = list(source.read_records())

    count = destination.write_with_checkpoint(
        records=records,
        source_name="jsonplaceholder_posts",
        sync_name="posts_transactional_sync",
    )

    checkpoint = destination.get_checkpoint(
        "posts_transactional_sync"
    )

    print(f"New records synchronized: {count}")
    print(f"Last checkpoint: {checkpoint}")

finally:
    source.close()
    destination.close()
