
import argparse
import os
import sys

from syncforge.config.loader import load_config
from syncforge.connectors.postgres import PostgreSQLDestination
from syncforge.engine.generic_sync import GenericSyncEngine
from syncforge.factory import create_source
from syncforge.monitoring.job_history import JobHistory


def run_job(config_path: str) -> int:
    """Execute a configured SyncForge job with tracking."""

    config = load_config(config_path)

    connection_env = config.destination.connection_env
    connection_string = os.environ.get(connection_env)

    if not connection_string:
        raise ValueError(
            f"Missing database environment variable: "
            f"{connection_env}"
        )

    history = JobHistory(connection_string)

    source = create_source(config)
    destination = PostgreSQLDestination(connection_string)

    engine = GenericSyncEngine(
        source=source,
        destination=destination,
        source_name=config.source_name,
        sync_name=config.sync_name,
        batch_size=config.batch_size,
        sync_mode=config.sync_mode,
    )

    run_id = history.start_job(
        sync_name=config.sync_name,
        source_name=config.source_name,
    )

    print(f"Starting SyncForge job: {config.sync_name}")
    print(f"Run ID: {run_id}")

    try:
        count = engine.run()

    except Exception as exc:
        try:
            history.fail_job(
                run_id=run_id,
                error_message=str(exc),
            )
        except Exception as history_error:
            print(
                f"Could not record job failure: "
                f"{history_error}",
                file=sys.stderr,
            )

        raise

    history.finish_job(
        run_id=run_id,
        records_processed=count,
    )

    print(f"Records processed: {count}")
    print("Synchronization completed successfully!")

    return count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SyncForge Data Integration CLI"
    )

    parser.add_argument(
        "--config",
        required=True,
        help="Path to YAML job configuration",
    )

    args = parser.parse_args()

    try:
        run_job(args.config)

    except Exception as exc:
        print(
            f"SyncForge job failed: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
