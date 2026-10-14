
import pytest

from syncforge.engine.batch import iter_batches


def test_batches_of_three():
    records = [{"id": i} for i in range(1, 8)]

    batches = list(iter_batches(iter(records), 3))

    assert len(batches) == 3
    assert [len(batch) for batch in batches] == [3, 3, 1]


def test_empty_input():
    assert list(iter_batches(iter([]), 3)) == []


def test_invalid_batch_size():
    with pytest.raises(ValueError):
        list(iter_batches([], 0))


def test_records_preserve_order():
    records = [{"id": i} for i in range(1, 6)]

    batches = list(iter_batches(iter(records), 2))

    ids = [
        record["id"]
        for batch in batches
        for record in batch
    ]

    assert ids == [1, 2, 3, 4, 5]


def test_generator_is_consumed_lazily():
    consumed = []

    def generate_records():
        for i in range(100):
            consumed.append(i)
            yield {"id": i}

    iterator = iter_batches(generate_records(), 10)

    assert consumed == []

    first_batch = next(iterator)

    assert len(first_batch) == 10
    assert len(consumed) == 10
