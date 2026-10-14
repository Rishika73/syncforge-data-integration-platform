
import json

from syncforge.connectors.base import SourceConnector
from syncforge.engine.incremental import IncrementalSyncEngine
from syncforge.state.checkpoint import CheckpointStore


class FakeSource(SourceConnector):
    def __init__(self, records):
        self.records = records

    def connect(self):
        pass

    def read_records(self):
        yield from self.records

    def close(self):
        pass


def make_engine(tmp_path, records):
    return IncrementalSyncEngine(
        source=FakeSource(records),
        checkpoint_store=CheckpointStore(
            str(tmp_path / "checkpoints.json")
        ),
        sync_name="test_sync",
        destination_path=str(tmp_path / "records.jsonl"),
    )


def test_first_sync(tmp_path):
    engine = make_engine(
        tmp_path,
        [{"id": 1}, {"id": 2}, {"id": 3}],
    )

    assert engine.run() == 3


def test_second_sync_skips_existing_records(tmp_path):
    records = [{"id": 1}, {"id": 2}]

    engine = make_engine(tmp_path, records)

    assert engine.run() == 2
    assert engine.run() == 0


def test_incremental_sync_only_adds_new_records(tmp_path):
    first = make_engine(
        tmp_path,
        [{"id": 1}, {"id": 2}],
    )

    assert first.run() == 2

    second = make_engine(
        tmp_path,
        [{"id": 1}, {"id": 2}, {"id": 3}],
    )

    assert second.run() == 1

    destination = tmp_path / "records.jsonl"

    with destination.open() as file:
        saved_records = [
            json.loads(line) for line in file
        ]

    assert len(saved_records) == 3


def test_retry_does_not_duplicate_records(tmp_path):
    engine = make_engine(
        tmp_path,
        [{"id": 1}, {"id": 2}, {"id": 3}],
    )

    assert engine.run() == 3

    # Simulate a crash after writing but before
    # the checkpoint was successfully saved.
    checkpoint = tmp_path / "checkpoints.json"
    checkpoint.unlink()

    retry_engine = make_engine(
        tmp_path,
        [{"id": 1}, {"id": 2}, {"id": 3}],
    )

    assert retry_engine.run() == 3

    destination = tmp_path / "records.jsonl"

    with destination.open() as file:
        saved_records = [
            json.loads(line) for line in file
        ]

    assert len(saved_records) == 3
    assert [r["id"] for r in saved_records] == [
        1, 2, 3
    ]
