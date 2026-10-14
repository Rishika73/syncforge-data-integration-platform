
import os


def get_database_url() -> str:
    """Return the database connection URL from environment."""

    database_url = os.environ.get(
        "SYNCFORGE_DATABASE_URL"
    )

    if not database_url:
        raise RuntimeError(
            "SYNCFORGE_DATABASE_URL is not configured. "
            "Set it before running SyncForge."
        )

    return database_url
