
-- SyncForge PostgreSQL Initialization
-- Creates database tables for ingestion,
-- checkpoints, and monitoring.

CREATE TABLE IF NOT EXISTS api_records (
    id BIGINT NOT NULL,
    source_name TEXT NOT NULL,
    payload JSONB NOT NULL,
    synced_at TIMESTAMPTZ
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (source_name, id)
);


CREATE TABLE IF NOT EXISTS sync_checkpoints (
    sync_name TEXT PRIMARY KEY,
    last_id BIGINT NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_last_id
        CHECK (last_id >= 0)
);


CREATE TABLE IF NOT EXISTS timestamp_checkpoints (
    sync_name TEXT PRIMARY KEY,
    last_updated_at TIMESTAMPTZ,
    last_record_id BIGINT,
    checkpoint_saved_at TIMESTAMPTZ
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_timestamp_checkpoint
        CHECK (
            (
                last_updated_at IS NULL
                AND last_record_id IS NULL
            )
            OR
            (
                last_updated_at IS NOT NULL
                AND last_record_id IS NOT NULL
            )
        )
);


CREATE TABLE IF NOT EXISTS sync_job_runs (
    run_id BIGSERIAL PRIMARY KEY,
    sync_name TEXT NOT NULL,
    source_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'running',
    records_processed BIGINT NOT NULL DEFAULT 0,
    started_at TIMESTAMPTZ
        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMPTZ,
    error_message TEXT,

    CONSTRAINT valid_job_status
        CHECK (
            status IN (
                'running',
                'success',
                'failed'
            )
        ),

    CONSTRAINT valid_records_processed
        CHECK (records_processed >= 0)
);


CREATE INDEX IF NOT EXISTS idx_sync_job_runs_name
ON sync_job_runs (
    sync_name,
    started_at DESC
);
