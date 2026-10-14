
import psycopg


class JobHistory:
    """
    Track synchronization job execution in PostgreSQL.
    """

    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def start_job(
        self,
        sync_name: str,
        source_name: str,
    ) -> int:
        """Create a running job and return its run ID."""

        with psycopg.connect(
            self.connection_string
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO sync_job_runs (
                        sync_name,
                        source_name,
                        status
                    )
                    VALUES (%s, %s, 'running')
                    RETURNING run_id
                    """,
                    (sync_name, source_name),
                )

                run_id = cursor.fetchone()[0]

        return run_id

    def finish_job(
        self,
        run_id: int,
        records_processed: int,
    ) -> None:
        """Mark a running job as successful."""

        with psycopg.connect(
            self.connection_string
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE sync_job_runs
                    SET status = 'success',
                        records_processed = %s,
                        finished_at = CURRENT_TIMESTAMP,
                        error_message = NULL
                    WHERE run_id = %s
                      AND status = 'running'
                    RETURNING run_id
                    """,
                    (records_processed, run_id),
                )

                if cursor.fetchone() is None:
                    raise ValueError(
                        f"Running job {run_id} not found"
                    )

    def fail_job(
        self,
        run_id: int,
        error_message: str,
    ) -> None:
        """Mark a running job as failed."""

        with psycopg.connect(
            self.connection_string
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE sync_job_runs
                    SET status = 'failed',
                        finished_at = CURRENT_TIMESTAMP,
                        error_message = %s
                    WHERE run_id = %s
                      AND status = 'running'
                    RETURNING run_id
                    """,
                    (error_message[:2000], run_id),
                )

                if cursor.fetchone() is None:
                    raise ValueError(
                        f"Running job {run_id} not found"
                    )

    def get_recent_runs(self, limit: int = 10):
        """Fetch recent synchronization executions."""

        if not 1 <= limit <= 100:
            raise ValueError(
                "limit must be between 1 and 100"
            )

        with psycopg.connect(
            self.connection_string
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        run_id,
                        sync_name,
                        status,
                        records_processed,
                        started_at,
                        finished_at
                    FROM sync_job_runs
                    ORDER BY run_id DESC
                    LIMIT %s
                    """,
                    (limit,),
                )

                return cursor.fetchall()

    def recover_stale_jobs(
        self,
        older_than_minutes: int = 60,
    ) -> int:
        """
        Mark jobs stuck in 'running' as failed.

        Only use this when jobs are not expected
        to run longer than the configured threshold.
        """

        if older_than_minutes <= 0:
            raise ValueError(
                "older_than_minutes must be positive"
            )

        with psycopg.connect(
            self.connection_string
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE sync_job_runs
                    SET status = 'failed',
                        finished_at = CURRENT_TIMESTAMP,
                        error_message =
                            'Job exceeded the allowed runtime'
                    WHERE status = 'running'
                      AND started_at <
                          CURRENT_TIMESTAMP
                          - (%s * INTERVAL '1 minute')
                    RETURNING run_id
                    """,
                    (older_than_minutes,),
                )

                recovered = cursor.fetchall()

        return len(recovered)
