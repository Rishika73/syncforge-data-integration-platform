
from itertools import islice
from typing import Any, Iterable, Iterator


def iter_batches(
    records: Iterable[dict[str, Any]],
    batch_size: int = 1000,
) -> Iterator[list[dict[str, Any]]]:
    """Yield fixed-size batches without loading all records."""

    if batch_size <= 0:
        raise ValueError("batch_size must be positive")

    iterator = iter(records)

    while True:
        batch = list(islice(iterator, batch_size))

        if not batch:
            break

        yield batch
