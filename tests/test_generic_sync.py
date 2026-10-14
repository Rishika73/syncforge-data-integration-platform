
from unittest.mock import MagicMock

import pytest

from syncforge.connectors.csv_source import CSVSourceConnector
from syncforge.connectors.rest_api import RESTAPIConnector
from syncforge.engine.generic_sync import GenericSyncEngine


# Helper: Create a mock PostgreSQL destination
def make_destination(checkpoint=0):
    destination = MagicMock()

    destination.get_checkpoint.return_value = checkpoint
    destination.write_with_checkpoint.return_value = 2

    return destination


# TEST 1: CSV source synchronization
def test_csv_source_sync():
    source = MagicMock(spec=CSVSourceConnector)

    source.read_records.return_value = iter([
        {"id": 1, "name": "Ava"},
        {"id": 2, "name": "Noah"},
    ])

    destination = make_destination()

    engine = GenericSyncEngine(
        source=source,
        destination=destination,
        source_name="csv_customers",
        sync_name="csv_sync",
    )

    count = engine.run()

    assert count == 2

    destination.connect.assert_called_once()

    destination.write_with_checkpoint.assert_called_once_with(
        records=[
            {"id": 1, "name": "Ava"},
            {"id": 2, "name": "Noah"},
        ],
        source_name="csv_customers",
        sync_name="csv_sync",
    )

    source.close.assert_called_once()
    destination.close.assert_called_once()


# TEST 2: REST API checkpoint synchronization
def test_rest_checkpoint_passed_to_source():

    # Use the actual RESTAPIConnector class.
    # Mock its methods so no real API request is made.
    source = RESTAPIConnector(
        "https://example.com/records"
    )

    source.connect = MagicMock()

    source.read_records = MagicMock(
        return_value=iter([
            {"id": 11}
        ])
    )

    source.close = MagicMock()

    destination = make_destination(checkpoint=10)

    destination.write_with_checkpoint.return_value = 1

    engine = GenericSyncEngine(
        source=source,
        destination=destination,
        source_name="api_records",
        sync_name="api_sync",
    )

    count = engine.run()

    assert count == 1

    # Verify PostgreSQL checkpoint is passed
    # to the REST connector.
    assert source.since_id == 10

    destination.get_checkpoint.assert_called_once_with(
        "api_sync"
    )

    destination.write_with_checkpoint.assert_called_once_with(
        records=[{"id": 11}],
        source_name="api_records",
        sync_name="api_sync",
    )

    source.connect.assert_called_once()
    source.close.assert_called_once()
    destination.close.assert_called_once()


# TEST 3: Close connections when sync fails
def test_sync_closes_connections_on_failure():
    source = MagicMock(spec=CSVSourceConnector)

    source.read_records.side_effect = RuntimeError(
        "Simulated source failure"
    )

    destination = make_destination()

    engine = GenericSyncEngine(
        source=source,
        destination=destination,
        source_name="csv_customers",
        sync_name="csv_sync",
    )

    with pytest.raises(
        RuntimeError,
        match="Simulated source failure",
    ):
        engine.run()

    source.close.assert_called_once()
    destination.close.assert_called_once()
