
from datetime import datetime
from typing import Any, Iterator


def parse_timestamp(value: str) -> datetime:
    """Convert ISO 8601 text into a timezone-aware datetime."""
    timestamp = datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )

    if timestamp.tzinfo is None:
        raise ValueError(
            "Timestamp must include a timezone"
        )

    return timestamp


def filter_updated_records(
    records: Iterator[dict[str, Any]],
    checkpoint: tuple[datetime, int] | None,
) -> Iterator[dict[str, Any]]:
    """
    Yield records newer than a (timestamp, ID) checkpoint.

    A source must provide:
      - integer id
      - ISO 8601 updated_at timestamp

    Records are compared using (updated_at, id).
    """

    for record in records:
        record_id = record.get("id")
        updated_at = record.get("updated_at")

        if type(record_id) is not int:
            raise ValueError(
                "Record ID must be an integer"
            )

        if not isinstance(updated_at, str):
            raise ValueError(
                "updated_at must be an ISO 8601 string"
            )

        timestamp = parse_timestamp(updated_at)

        if checkpoint is None:
            yield record
            continue

        last_timestamp, last_id = checkpoint

        if (timestamp, record_id) > (
            last_timestamp,
            last_id,
        ):
            yield record
