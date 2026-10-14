
from syncforge.state.checkpoint import CheckpointStore


def test_checkpoint_save_and_load(tmp_path):
    checkpoint_file = tmp_path / "checkpoints.json"

    store = CheckpointStore(str(checkpoint_file))

    assert store.get("posts_sync") == 0

    store.save("posts_sync", 100)

    assert store.get("posts_sync") == 100


def test_multiple_sync_checkpoints(tmp_path):
    checkpoint_file = tmp_path / "checkpoints.json"

    store = CheckpointStore(str(checkpoint_file))

    store.save("posts_sync", 100)
    store.save("users_sync", 10)

    assert store.get("posts_sync") == 100
    assert store.get("users_sync") == 10


def test_checkpoint_persists_after_restart(tmp_path):
    checkpoint_file = tmp_path / "checkpoints.json"

    first_store = CheckpointStore(str(checkpoint_file))
    first_store.save("posts_sync", 105)

    second_store = CheckpointStore(str(checkpoint_file))

    assert second_store.get("posts_sync") == 105
