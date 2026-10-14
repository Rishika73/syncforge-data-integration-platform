from syncforge.database import get_database_url

import os
from uuid import uuid4

import pytest

from syncforge.monitoring.job_history import JobHistory


DATABASE_URL = get_database_url()


@pytest.fixture
def history():
    manager = JobHistory(DATABASE_URL)
    created_runs = []

    yield manager, created_runs

    # Clean up test data
    import psycopg

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            for run_id in created_runs:
                cursor.execute(
                    "DELETE FROM sync_job_runs WHERE run_id = %s",
                    (run_id,),
                )


def test_job_starts_as_running(history):
    manager, created_runs = history

    sync_name = f"test_sync_{uuid4().hex}"

    run_id = manager.start_job(
        sync_name=sync_name,
        source_name="test_source",
    )
    created_runs.append(run_id)

    rows = manager.get_recent_runs(limit=100)

    matching = [row for row in rows if row[0] == run_id]

    assert len(matching) == 1
    assert matching[0][2] == "running"


def test_successful_job_records_count(history):
    manager, created_runs = history

    run_id = manager.start_job(
        sync_name=f"success_{uuid4().hex}",
        source_name="test_source",
    )
    created_runs.append(run_id)

    manager.finish_job(
        run_id=run_id,
        records_processed=25,
    )

    rows = manager.get_recent_runs(limit=100)
    matching = [row for row in rows if row[0] == run_id]

    assert matching[0][2] == "success"
    assert matching[0][3] == 25
    assert matching[0][5] is not None


def test_failed_job_records_failure(history):
    manager, created_runs = history

    run_id = manager.start_job(
        sync_name=f"failed_{uuid4().hex}",
        source_name="test_source",
    )
    created_runs.append(run_id)

    manager.fail_job(
        run_id=run_id,
        error_message="API connection failed",
    )

    rows = manager.get_recent_runs(limit=100)
    matching = [row for row in rows if row[0] == run_id]

    assert matching[0][2] == "failed"
    assert matching[0][5] is not None


def test_cannot_finish_job_twice(history):
    manager, created_runs = history

    run_id = manager.start_job(
        sync_name=f"duplicate_{uuid4().hex}",
        source_name="test_source",
    )
    created_runs.append(run_id)

    manager.finish_job(run_id, 10)

    with pytest.raises(ValueError):
        manager.finish_job(run_id, 20)


def test_recent_runs_limit_validation(history):
    manager, _ = history

    with pytest.raises(ValueError):
        manager.get_recent_runs(limit=0)

    with pytest.raises(ValueError):
        manager.get_recent_runs(limit=101)
