
from unittest.mock import MagicMock

import pytest

from syncforge.connectors.csv_source import (
    CSVSourceConnector,
)
from syncforge.engine.generic_sync import (
    GenericSyncEngine,
)


def make_source():
    source = MagicMock(spec=CSVSourceConnector)
    source.read_records.return_value = iter([
        {"id": 1, "name": "Ava"},
        {"id": 2, "name": "Noah"},
    ])
    return source


def test_snapshot_mode_uses_upserts():
    source = make_source()
    destination = MagicMock()
    destination.write_records.return_value = 2

    engine = GenericSyncEngine(
        source=source,
        destination=destination,
        source_name="customers",
        sync_name="customers_sync",
        sync_mode="snapshot",
    )

    assert engine.run() == 2

    destination.write_records.assert_called_once()
    destination.get_checkpoint.assert_not_called()
    destination.write_with_checkpoint.assert_not_called()


def test_incremental_mode_uses_checkpoint():
    source = make_source()
    destination = MagicMock()

    destination.get_checkpoint.return_value = 0
    destination.write_with_checkpoint.return_value = 2

    engine = GenericSyncEngine(
        source=source,
        destination=destination,
        source_name="customers",
        sync_name="customers_sync",
        sync_mode="incremental",
    )

    assert engine.run() == 2

    destination.get_checkpoint.assert_called_once_with(
        "customers_sync"
    )

    destination.write_with_checkpoint.assert_called_once()


def test_invalid_sync_mode():
    with pytest.raises(ValueError):
        GenericSyncEngine(
            source=make_source(),
            destination=MagicMock(),
            source_name="customers",
            sync_name="customers_sync",
            sync_mode="unknown",
        )


def test_snapshot_accepts_out_of_order_records():
    source = MagicMock(spec=CSVSourceConnector)

    source.read_records.return_value = iter([
        {"id": 5},
        {"id": 2},
        {"id": 4},
    ])

    destination = MagicMock()
    destination.write_records.return_value = 3

    engine = GenericSyncEngine(
        source=source,
        destination=destination,
        source_name="customers",
        sync_name="customers_sync",
        sync_mode="snapshot",
    )

    assert engine.run() == 3
