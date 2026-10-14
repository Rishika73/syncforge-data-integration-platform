
from datetime import datetime, timezone

import pytest

from syncforge.engine.timestamp_filter import (
    filter_updated_records,
    parse_timestamp,
)


def test_first_sync_returns_all_records():
    records = [
        {"id": 1, "updated_at": "2026-10-10T09:00:00Z"},
        {"id": 2, "updated_at": "2026-10-11T10:00:00Z"},
    ]

    result = list(filter_updated_records(
        iter(records), None
    ))

    assert len(result) == 2


def test_detects_updated_existing_record():
    checkpoint = (
        datetime(2026, 10, 10, 10, tzinfo=timezone.utc),
        100,
    )

    records = [
        {"id": 50, "updated_at": "2026-10-11T11:00:00Z"},
        {"id": 100, "updated_at": "2026-10-10T10:00:00Z"},
    ]

    result = list(filter_updated_records(
        iter(records), checkpoint
    ))

    assert [r["id"] for r in result] == [50]


def test_same_timestamp_uses_id_tiebreaker():
    checkpoint = (
        datetime(2026, 10, 12, 10, tzinfo=timezone.utc),
        101,
    )

    records = [
        {"id": 100, "updated_at": "2026-10-12T10:00:00Z"},
        {"id": 101, "updated_at": "2026-10-12T10:00:00Z"},
        {"id": 102, "updated_at": "2026-10-12T10:00:00Z"},
    ]

    result = list(filter_updated_records(
        iter(records), checkpoint
    ))

    assert [r["id"] for r in result] == [102]


def test_rejects_timestamp_without_timezone():
    with pytest.raises(ValueError):
        parse_timestamp("2026-10-12T10:00:00")


def test_rejects_invalid_record_id():
    records = [
        {"id": "abc", "updated_at": "2026-10-12T10:00:00Z"}
    ]

    with pytest.raises(ValueError):
        list(filter_updated_records(iter(records), None))
