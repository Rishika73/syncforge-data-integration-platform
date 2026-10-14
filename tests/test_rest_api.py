
from unittest.mock import MagicMock, patch

import pytest

from syncforge.connectors.rest_api import RESTAPIConnector


# Helper function to simulate API responses
def make_response(records):
    response = MagicMock()
    response.json.return_value = records
    return response


# TEST 1: Multiple API pages
@patch("syncforge.connectors.rest_api.requests.Session")
def test_multiple_pages(mock_session_class):
    mock_session = mock_session_class.return_value

    mock_session.get.side_effect = [
        make_response([{"id": 1}, {"id": 2}]),
        make_response([{"id": 3}]),
    ]

    connector = RESTAPIConnector(
        "https://example.com/posts",
        page_size=2,
    )

    connector.connect()

    try:
        records = list(connector.read_records())
    finally:
        connector.close()

    assert len(records) == 3
    assert [r["id"] for r in records] == [1, 2, 3]
    assert mock_session.get.call_count == 2


# TEST 2: Empty API response
@patch("syncforge.connectors.rest_api.requests.Session")
def test_empty_page(mock_session_class):
    mock_session = mock_session_class.return_value
    mock_session.get.return_value = make_response([])

    connector = RESTAPIConnector(
        "https://example.com/posts",
        page_size=10,
    )

    connector.connect()

    try:
        records = list(connector.read_records())
    finally:
        connector.close()

    assert records == []
    assert mock_session.get.call_count == 1


# TEST 3: Invalid page size
def test_invalid_page_size():
    with pytest.raises(ValueError):
        RESTAPIConnector(
            "https://example.com/posts",
            page_size=0,
        )


# TEST 4: Reading without connecting
def test_read_without_connection():
    connector = RESTAPIConnector(
        "https://example.com/posts"
    )

    with pytest.raises(RuntimeError):
        list(connector.read_records())


# TEST 5: Invalid JSON structure
@patch("syncforge.connectors.rest_api.requests.Session")
def test_invalid_json_structure(mock_session_class):
    mock_session = mock_session_class.return_value
    mock_session.get.return_value = make_response(
        {"id": 1}
    )

    connector = RESTAPIConnector(
        "https://example.com/posts"
    )

    connector.connect()

    try:
        with pytest.raises(ValueError):
            list(connector.read_records())
    finally:
        connector.close()


# TEST 6: Incremental API parameter
@patch("syncforge.connectors.rest_api.requests.Session")
def test_incremental_api_parameter(mock_session_class):
    mock_session = mock_session_class.return_value

    mock_session.get.return_value = make_response(
        [{"id": 101}, {"id": 102}]
    )

    connector = RESTAPIConnector(
        "https://example.com/records",
        page_size=10,
        since_id=100,
        cursor_parameter="id_gt",
    )

    connector.connect()

    try:
        records = list(connector.read_records())
    finally:
        connector.close()

    assert len(records) == 2
    assert [r["id"] for r in records] == [101, 102]

    mock_session.get.assert_called_once_with(
        "https://example.com/records",
        params={
            "_page": 1,
            "_limit": 10,
            "id_gt": 100,
        },
        timeout=30,
    )


# TEST 7: Filter previously synchronized records
@patch("syncforge.connectors.rest_api.requests.Session")
def test_incremental_filters_old_records(mock_session_class):
    mock_session = mock_session_class.return_value

    mock_session.get.return_value = make_response(
        [
            {"id": 99},
            {"id": 100},
            {"id": 101},
        ]
    )

    connector = RESTAPIConnector(
        "https://example.com/records",
        page_size=10,
        since_id=100,
    )

    connector.connect()

    try:
        records = list(connector.read_records())
    finally:
        connector.close()

    assert [record["id"] for record in records] == [101]


def test_invalid_retry_configuration():
    with pytest.raises(ValueError):
        RESTAPIConnector(
            "https://example.com/posts",
            max_retries=-1,
        )

    with pytest.raises(ValueError):
        RESTAPIConnector(
            "https://example.com/posts",
            backoff_factor=-1,
        )


@patch("syncforge.connectors.rest_api.requests.Session")
def test_retry_adapter_configuration(mock_session_class):
    connector = RESTAPIConnector(
        "https://example.com/posts",
        max_retries=4,
        backoff_factor=2,
    )

    connector.connect()

    try:
        session = mock_session_class.return_value

        assert session.mount.call_count == 2

        adapter = session.mount.call_args_list[0].args[1]
        retry = adapter.max_retries

        assert retry.total == 4
        assert retry.backoff_factor == 2
        assert 429 in retry.status_forcelist
        assert 503 in retry.status_forcelist
        assert retry.respect_retry_after_header is True

    finally:
        connector.close()
