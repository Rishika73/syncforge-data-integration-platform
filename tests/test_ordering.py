
import pytest

from syncforge.engine.ordering import validate_increasing_ids


def test_sorted_ids():
    records = [
        {"id": 1},
        {"id": 2},
        {"id": 3},
    ]

    result = list(validate_increasing_ids(records))

    assert [record["id"] for record in result] == [1, 2, 3]


def test_out_of_order_ids():
    records = [
        {"id": 1},
        {"id": 5},
        {"id": 3},
    ]

    with pytest.raises(ValueError):
        list(validate_increasing_ids(records))


def test_duplicate_ids():
    records = [
        {"id": 1},
        {"id": 2},
        {"id": 2},
    ]

    with pytest.raises(ValueError):
        list(validate_increasing_ids(records))


def test_invalid_id():
    records = [
        {"id": "100"},
    ]

    with pytest.raises(ValueError):
        list(validate_increasing_ids(records))


def test_respects_starting_checkpoint():
    records = [
        {"id": 101},
        {"id": 102},
    ]

    result = list(
        validate_increasing_ids(
            records,
            starting_id=100,
        )
    )

    assert len(result) == 2


def test_rejects_id_below_checkpoint():
    records = [
        {"id": 99},
    ]

    with pytest.raises(ValueError):
        list(
            validate_increasing_ids(
                records,
                starting_id=100,
            )
        )
