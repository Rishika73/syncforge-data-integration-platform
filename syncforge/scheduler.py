
import argparse
import logging
import time
from collections.abc import Callable

from syncforge.cli import run_job


logger = logging.getLogger(__name__)


def run_scheduler(
    config_path: str,
    interval_seconds: float,
    max_runs: int | None = None,
    job_runner: Callable[[str], int] | None = None,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> tuple[int, int]:
    """
    Run a configured synchronization job repeatedly.

    Wait interval_seconds after each completed attempt.

    Returns:
        (number_of_attempts, number_of_failures)
    """

    if interval_seconds <= 0:
        raise ValueError(
            "interval_seconds must be positive"
        )

    if max_runs is not None and max_runs <= 0:
        raise ValueError(
            "max_runs must be positive"
        )

    runner = job_runner or run_job

    attempts = 0
    failures = 0

    while max_runs is None or attempts < max_runs:
        attempts += 1

        logger.info(
            "Starting scheduled attempt %s",
            attempts,
        )

        try:
            count = runner(config_path)

            logger.info(
                "Scheduled attempt %s succeeded: "
                "%s records processed",
                attempts,
                count,
            )

        except Exception:
            failures += 1

            logger.exception(
                "Scheduled attempt %s failed",
                attempts,
            )

        if max_runs is not None and attempts >= max_runs:
            break

        logger.info(
            "Next attempt in %s seconds",
            interval_seconds,
        )

        sleep_fn(interval_seconds)

    return attempts, failures


def main():
    parser = argparse.ArgumentParser(
        description="SyncForge Interval Scheduler"
    )

    parser.add_argument(
        "--config",
        required=True,
        help="Path to YAML job configuration",
    )

    parser.add_argument(
        "--interval-seconds",
        type=float,
        required=True,
        help="Delay between completed job attempts",
    )

    parser.add_argument(
        "--max-runs",
        type=int,
        default=None,
        help="Maximum attempts; omit to keep running",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    try:
        attempts, failures = run_scheduler(
            config_path=args.config,
            interval_seconds=args.interval_seconds,
            max_runs=args.max_runs,
        )

    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
        return

    except ValueError as exc:
        parser.error(str(exc))

    logger.info(
        "Scheduler finished: %s attempts, %s failures",
        attempts,
        failures,
    )

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
