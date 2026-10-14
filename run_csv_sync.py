from syncforge.database import get_database_url

import os

from syncforge.connectors.csv_source import (
    CSVSourceConnector,
)
from syncforge.connectors.postgres import (
    PostgreSQLDestination,
)
from syncforge.engine.generic_sync import (
    GenericSyncEngine,
)


source = CSVSourceConnector(
    "sample_data/customers.csv"
)

destination = PostgreSQLDestination(
    get_database_url()
)

engine = GenericSyncEngine(
    source=source,
    destination=destination,
    source_name="csv_customers",
    sync_name="csv_customers_sync",
    batch_size=2,
    sync_mode="snapshot",
)

count = engine.run()

print(f"CSV records upserted: {count}")
print("Snapshot synchronization completed!")
