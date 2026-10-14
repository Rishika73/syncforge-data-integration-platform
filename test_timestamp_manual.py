from syncforge.database import get_database_url

import os
from datetime import datetime, timezone

from syncforge.state.timestamp_checkpoint import (
    TimestampCheckpointStore,
)


DATABASE_URL = get_database_url()

store = TimestampCheckpointStore(DATABASE_URL)

sync_name = "timestamp_demo_sync"

checkpoint = store.get(sync_name)

print("Before:", checkpoint)

updated_at = datetime(
    2026, 10, 12, 10, 30,
    tzinfo=timezone.utc,
)

store.save(
    sync_name=sync_name,
    updated_at=updated_at,
    record_id=101,
)

checkpoint = store.get(sync_name)

print("After:", checkpoint)

assert checkpoint == (updated_at, 101)

print("Timestamp checkpoint test successful!")
