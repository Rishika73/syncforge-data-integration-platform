
import json
import os
from pathlib import Path


class CheckpointStore:
    def __init__(self, file_path: str = "checkpoints.json"):
        self.file_path = Path(file_path)

    def get(self, sync_name: str) -> int:
        if not self.file_path.exists():
            return 0

        with self.file_path.open("r") as file:
            checkpoints = json.load(file)

        return checkpoints.get(sync_name, 0)

    def save(self, sync_name: str, last_id: int) -> None:
        checkpoints = {}

        if self.file_path.exists():
            with self.file_path.open("r") as file:
                checkpoints = json.load(file)

        checkpoints[sync_name] = last_id

        temp_path = self.file_path.with_suffix(
            self.file_path.suffix + ".tmp"
        )

        with temp_path.open("w") as file:
            json.dump(checkpoints, file, indent=2)

        os.replace(temp_path, self.file_path)
