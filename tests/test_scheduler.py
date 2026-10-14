
from unittest.mock import Mock

import pytest

from syncforge.scheduler import run_scheduler


def test_scheduler_runs_twice():
    runner = Mock(return_value=5)
    sleeper = Mock()

    attempts, failures = run_scheduler(
        config_path="customers.yaml",
        interval_seconds=5,
        max_runs=2,
        job_runner=runner,
        sleep_fn=sleeper,
    )

    assert attempts == 2
    assert failures == 0
    assert runner.call_count == 2
    sleeper.assert_called_once_with(5)


def test_scheduler_runs_once_without_sleep():
    runner = Mock(return_value=10)
    sleeper = Mock()

    attempts, failures = run_scheduler(
        config_path="customers.yaml",
        interval_seconds=60,
        max_runs=1,
        job_runner=runner,
        sleep_fn=sleeper,
    )

    assert attempts == 1
    assert failures == 0
    sleeper.assert_not_called()


def test_scheduler_continues_after_failure():
    runner = Mock(
        side_effect=[
            RuntimeError("Temporary API failure"),
            5,
        ]
    )

    sleeper = Mock()

    attempts, failures = run_scheduler(
        config_path="customers.yaml",
        interval_seconds=5,
        max_runs=2,
        job_runner=runner,
        sleep_fn=sleeper,
    )

    assert attempts == 2
    assert failures == 1
    assert runner.call_count == 2


def test_invalid_interval():
    with pytest.raises(ValueError):
        run_scheduler(
            config_path="customers.yaml",
            interval_seconds=0,
            max_runs=1,
        )


def test_invalid_max_runs():
    with pytest.raises(ValueError):
        run_scheduler(
            config_path="customers.yaml",
            interval_seconds=5,
            max_runs=0,
        )
