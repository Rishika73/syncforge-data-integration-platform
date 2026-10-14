
from syncforge.connectors.rest_api import RESTAPIConnector
from syncforge.engine.incremental import IncrementalSyncEngine
from syncforge.state.checkpoint import CheckpointStore


source = RESTAPIConnector(
    "https://jsonplaceholder.typicode.com/posts",
    page_size=20,
)

store = CheckpointStore("checkpoints.json")

engine = IncrementalSyncEngine(
    source=source,
    checkpoint_store=store,
    sync_name="posts_sync",
    destination_path="data/posts.jsonl",
)

count = engine.run()

print(f"New records synchronized: {count}")
print("Destination: data/posts.jsonl")
print("Checkpoint: checkpoints.json")
