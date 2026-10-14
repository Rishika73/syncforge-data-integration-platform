from syncforge.database import get_database_url

import os

from syncforge.connectors.postgres import PostgreSQLDestination
from syncforge.connectors.rest_api import RESTAPIConnector
from syncforge.engine.postgres_sync import PostgreSQLSyncEngine


source = RESTAPIConnector(
    url="https://jsonplaceholder.typicode.com/posts",
    page_size=20,
)

destination = PostgreSQLDestination(
    get_database_url()
)

engine = PostgreSQLSyncEngine(
    source=source,
    destination=destination,
    source_name="jsonplaceholder_posts",
    sync_name="posts_auto_sync",
)

count = engine.run()

print(f"New records synchronized: {count}")
print("Automatic synchronization completed!")
