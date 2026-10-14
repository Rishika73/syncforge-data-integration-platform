
from typing import Any, Iterable, Iterator


def validate_increasing_ids(
    records: Iterable[dict[str, Any]],
    starting_id: int = 0,
) -> Iterator[dict[str, Any]]:
    """
    Validate strictly increasing integer IDs.

    Raises ValueError if records are unsorted,
    duplicated, or have invalid IDs.
    """
    previous_id = starting_id

    for record in records:
        record_id = record.get("id")

        if type(record_id) is not int:
            raise ValueError(
                "Record ID must be an integer"
            )

        if record_id <= previous_id:
            raise ValueError(
                f"Record ID {record_id} is not greater "
                f"than previous ID {previous_id}"
            )

        previous_id = record_id
        yield record
