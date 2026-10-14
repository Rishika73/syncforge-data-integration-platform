
import os

from syncforge.monitoring.job_history import JobHistory


DATABASE_URL = os.environ.get(
    "SYNCFORGE_DATABASE_URL"
)

if not DATABASE_URL:
    raise RuntimeError(
        "SYNCFORGE_DATABASE_URL is not configured"
    )

history = JobHistory(DATABASE_URL)

count = history.recover_stale_jobs(
    older_than_minutes=60
)

print(f"Recovered stale jobs: {count}")
