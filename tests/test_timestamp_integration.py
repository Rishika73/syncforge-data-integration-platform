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

    source_name = f"timestamp_test_{uuid4().hex}"
    sync_name = f"timestamp_sync_{uuid4().hex}"

    try:
        yield db, source_name, sync_name
    finally:
        with db.connection.transaction():
            with db.connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM api_records
                    WHERE source_name = %s
                    """,
                    (source_name,),
                )
                cursor.execute(
                    """
                    DELETE FROM timestamp_checkpoints
                    WHERE sync_name = %s
                    """,
                    (sync_name,),
                )

        db.close()


def read_records(db, source_name):
    with db.connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, payload
            FROM api_records
            WHERE source_name = %s
            ORDER BY id
            """,
            (source_name,),
        )
        return cursor.fetchall()


# TEST 1: First timestamp synchronization
def test_initial_timestamp_sync(destination):
    db, source_name, sync_name = destination

    records = [
        {
            "id": 1,
            "city": "New York",
            "updated_at": "2026-10-10T10:00:00Z",
        },
        {
            "id": 2,
            "city": "Chicago",
            "updated_at": "2026-10-11T10:00:00Z",
        },
    ]

    count = db.write_with_timestamp_checkpoint(
        records, source_name, sync_name
    )

    assert count == 2
    assert len(read_records(db, source_name)) == 2


# TEST 2: Update an existing record
def test_updated_record_is_upserted(destination):
    db, source_name, sync_name = destination

    db.write_with_timestamp_checkpoint(
        [
            {
                "id": 1,
                "city": "New York",
                "updated_at": "2026-10-10T10:00:00Z",
            }
        ],
        source_name,
        sync_name,
    )

    count = db.write_with_timestamp_checkpoint(
        [
            {
                "id": 1,
                "city": "Boston",
                "updated_at": "2026-10-12T11:00:00Z",
            }
        ],
        source_name,
        sync_name,
    )

    assert count == 1

    rows = read_records(db, source_name)

    assert len(rows) == 1
    assert rows[0][1]["city"] == "Boston"


# TEST 3: Same timestamp with higher ID
def test_same_timestamp_uses_id(destination):
    db, source_name, sync_name = destination

    db.write_with_timestamp_checkpoint(
        [
            {
                "id": 1,
                "updated_at": "2026-10-12T10:00:00Z",
            }
        ],
        source_name,
        sync_name,
    )

    count = db.write_with_timestamp_checkpoint(
        [
            {
                "id": 2,
                "updated_at": "2026-10-12T10:00:00Z",
            }
        ],
        source_name,
        sync_name,
    )

    assert count == 1
    assert len(read_records(db, source_name)) == 2


# TEST 4: Avoid duplicate synchronization
def test_repeated_timestamp_sync_is_idempotent(destination):
    db, source_name, sync_name = destination

    records = [
        {
            "id": 1,
            "updated_at": "2026-10-12T10:00:00Z",
        }
    ]

    first = db.write_with_timestamp_checkpoint(
        records, source_name, sync_name
    )

    second = db.write_with_timestamp_checkpoint(
        records, source_name, sync_name
    )

    assert first == 1
    assert second == 0
    assert len(read_records(db, source_name)) == 1


# TEST 5: Database failure rolls back records
def test_timestamp_transaction_rollback(destination):
    db, source_name, sync_name = destination

    records = [
        {
            "id": 1,
            "updated_at": "2026-10-12T10:00:00Z",
        },
        {
            "id": 2**63,
            "updated_at": "2026-10-12T11:00:00Z",
        },
    ]

    with pytest.raises(psycopg.Error):
        db.write_with_timestamp_checkpoint(
            records, source_name, sync_name
        )

    assert read_records(db, source_name) == []

    with db.connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM timestamp_checkpoints
            WHERE sync_name = %s
            """,
            (sync_name,),
        )
        assert cursor.fetchone()[0] == 0
