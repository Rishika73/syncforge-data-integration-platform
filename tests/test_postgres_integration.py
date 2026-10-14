from syncforge.database import get_database_url

import os
from uuid import uuid4

import psycopg
import pytest

from syncforge.connectors.postgres import PostgreSQLDestination


DATABASE_URL = get_database_url()


@pytest.fixture
def destination():
    db = PostgreSQLDestination(DATABASE_URL)
    db.connect()

    source_name = f"test_source_{uuid4().hex}"
    sync_name = f"test_sync_{uuid4().hex}"

    try:
        yield db, source_name, sync_name
    finally:
        # Remove only records created by this test.
        with db.connection.transaction():
            with db.connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM api_records WHERE source_name = %s",
                    (source_name,),
                )
                cursor.execute(
                    "DELETE FROM sync_checkpoints WHERE sync_name = %s",
                    (sync_name,),
                )

        db.close()


def test_first_sync(destination):
    db, source_name, sync_name = destination

    records = [
        {"id": 1, "title": "First"},
        {"id": 2, "title": "Second"},
    ]

    count = db.write_with_checkpoint(
        records,
        source_name,
        sync_name,
    )

    assert count == 2
    assert db.get_checkpoint(sync_name) == 2


def test_second_sync_is_idempotent(destination):
    db, source_name, sync_name = destination

    records = [
        {"id": 1},
        {"id": 2},
    ]

    first_count = db.write_with_checkpoint(
        records, source_name, sync_name
    )

    second_count = db.write_with_checkpoint(
        records, source_name, sync_name
    )

    assert first_count == 2
    assert second_count == 0
    assert db.get_checkpoint(sync_name) == 2


def test_transaction_rolls_back_on_failure(destination):
    db, source_name, sync_name = destination

    records = [
        {"id": 1, "title": "Valid"},
        {"id": 2**63, "title": "Invalid BIGINT"},
    ]

    # The second ID exceeds PostgreSQL BIGINT range.
    # The first insert must roll back as well.
    with pytest.raises(psycopg.Error):
        db.write_with_checkpoint(
            records, source_name, sync_name
        )

    assert db.get_checkpoint(sync_name) == 0

    with db.connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM api_records
            WHERE source_name = %s
            """,
            (source_name,),
        )
        count = cursor.fetchone()[0]

    assert count == 0
