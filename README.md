
# SyncForge — Config-Driven Data Integration Platform

### 🚀 Live Demo

[Explore the SyncForge Monitoring Dashboard](PASTE_YOUR_STREAMLIT_APP_URL_HERE)

Interactive public dashboard showcasing synchronization
history, execution metrics, and failure analysis using
clearly labeled synthetic data.


### A Modular Python Framework for Reliable Data Ingestion, Incremental Synchronization, and Operational Monitoring

[![SyncForge CI](https://github.com/Rishika73/syncforge-data-integration-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/Rishika73/syncforge-data-integration-platform/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B)
![License](https://img.shields.io/badge/License-MIT-green)

**SyncForge** is a configuration-driven data integration platform built with Python, PostgreSQL, Docker, and Streamlit.

It provides reusable connectors for ingesting data from REST APIs and CSV files, supports incremental and snapshot synchronization, and includes transactional checkpoint management, batch processing, job scheduling, execution tracking, and a monitoring dashboard.

The project demonstrates the engineering concepts behind modern data integration platforms such as Airbyte and Fivetran, while remaining a lightweight, extensible portfolio implementation.

---

## Table of Contents

- [Why SyncForge?](#why-syncforge)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Running Data Integration Jobs](#running-data-integration-jobs)
- [Synchronization Strategies](#synchronization-strategies)
- [Job Scheduling](#job-scheduling)
- [Monitoring Dashboard](#monitoring-dashboard)
- [Database Design](#database-design)
- [Testing and CI/CD](#testing-and-cicd)
- [Reliability and Recovery](#reliability-and-recovery)
- [Current Limitations](#current-limitations)
- [Future Enhancements](#future-enhancements)
- [Author](#author)

---

## Why SyncForge?

Data engineering teams regularly ingest information from different sources into centralized databases and analytics platforms.

A production-oriented ingestion framework must address challenges such as:

- Supporting multiple data sources through reusable interfaces
- Avoiding unnecessary full reloads
- Handling transient API failures
- Processing large datasets without excessive memory usage
- Preventing duplicate records
- Maintaining synchronization state
- Recovering safely from database failures
- Tracking job execution and diagnosing errors
- Running ingestion workflows automatically

SyncForge explores these challenges through a modular, Python-based integration framework.

Instead of writing a separate ingestion script for every data source, users configure a synchronization job in YAML and execute it using a command-line interface.

---

## Key Features

### 1. Pluggable Source Connectors

A reusable connector interface supports different data sources.

**REST API Connector**
- HTTP-based data extraction
- Paginated data retrieval
- Configurable page size
- Retry handling for transient HTTP failures
- Support for optional incremental cursor parameters

**CSV Connector**
- CSV file ingestion
- Header and record validation
- Iterator-based record processing
- Integration with PostgreSQL snapshot synchronization

Additional connectors can be implemented using the existing source interface.

### 2. PostgreSQL Destination

- PostgreSQL 16 integration
- JSONB-based record storage
- Upserts using `INSERT ... ON CONFLICT`
- Transactional record operations
- Support for multiple logical sources
- Persistent synchronization state

### 3. Incremental Synchronization

SyncForge supports increasing-ID checkpoints for ordered, append-only data feeds.

It tracks the last successfully processed record ID and uses that state to avoid repeating previously committed records.

### 4. Timestamp-Based Synchronization

Timestamp-based synchronization supports detecting updates to existing records.

Records are compared using the composite cursor:

`(updated_at, id)`

This supports processing multiple records with the same update timestamp when the source provides a stable ordering.

### 5. Transactional Checkpoints

Record writes and their corresponding checkpoint updates can occur in a single PostgreSQL transaction.

If a database operation fails, the transaction rolls back, preventing checkpoint advancement for uncommitted records.

### 6. Memory-Efficient Batch Processing

SyncForge processes source records in configurable batches rather than loading all records into memory.

This supports more memory-efficient ingestion for larger datasets.

### 7. Configuration-Driven Jobs

Synchronization jobs are configured using YAML and validated using Pydantic.

Users specify:

- Source type
- Source location or API URL
- Synchronization mode
- Batch size
- Logical source and job names
- Destination connection configuration

### 8. Automated Scheduling

A Python interval scheduler supports:

- Sequential job execution
- Configurable delays between attempts
- Limited or continuous execution
- Logging of failed attempts
- Continued operation after recoverable job failures

### 9. Job Execution History

PostgreSQL stores operational information, including:

- Job name
- Source name
- Run ID
- Start and completion times
- Execution status
- Number of processed records
- Error information

### 10. Streamlit Monitoring Dashboard

A web-based dashboard displays ingestion activity, success and failure statistics, execution history, and processing counts.

---

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python 3.11 |
| Database | PostgreSQL 16 |
| Database Driver | Psycopg 3 |
| API Ingestion | Requests |
| CSV Processing | Python CSV Module |
| Configuration | YAML, Pydantic |
| Batch Processing | Python Iterators |
| Scheduling | Python Interval Scheduler |
| Monitoring | Streamlit, Pandas |
| Containerization | Docker Compose |
| Testing | Pytest |
| CI/CD | GitHub Actions |
| Version Control | Git and GitHub |

---

## System Architecture

SyncForge uses a modular architecture to separate configuration, source extraction, synchronization logic, persistence, and operational monitoring.

```mermaid
flowchart TD
    A["YAML Job Configuration"] --> B["CLI / Scheduler"]
    B --> C["Pydantic Configuration Validation"]
    C --> D["Connector Factory"]

    D --> E1["REST API Connector"]
    D --> E2["CSV Connector"]

    E1 --> F["Synchronization Engine"]
    E2 --> F

    F --> G["Validation and Batch Processing"]
    G --> H["PostgreSQL Destination"]

    H --> I["JSONB Record Storage"]
    H --> J["Synchronization Checkpoints"]

    B --> K["Execution History"]
    K --> L["Streamlit Monitoring Dashboard"]
```

### Data Flow

1. A user defines a synchronization job using YAML.
2. The CLI or scheduler loads the job.
3. Pydantic validates the configuration.
4. The connector factory creates the requested source connector.
5. The source connector retrieves records.
6. The synchronization engine validates and batches the records.
7. PostgreSQL upserts the records and stores synchronization state.
8. Job execution history is recorded in PostgreSQL.
9. Streamlit visualizes job metrics and execution history.

---

## Project Structure

```text
syncforge-data-integration-platform/
|
|-- .github/
|   `-- workflows/
|       `-- ci.yml
|
|-- configs/
|   `-- customers_csv.yaml
|
|-- dashboard/
|   `-- app.py
|
|-- docs/
|   `-- images/
|       `-- dashboard.png
|
|-- sample_data/
|   `-- customers.csv
|
|-- sql/
|   `-- init.sql
|
|-- syncforge/
|   |-- __init__.py
|   |-- cli.py
|   |-- database.py
|   |-- factory.py
|   |-- scheduler.py
|   |
|   |-- config/
|   |   `-- loader.py
|   |
|   |-- connectors/
|   |   |-- base.py
|   |   |-- csv_source.py
|   |   |-- rest_api.py
|   |   `-- postgres.py
|   |
|   |-- engine/
|   |   |-- batch.py
|   |   |-- generic_sync.py
|   |   |-- incremental.py
|   |   |-- ordering.py
|   |   |-- postgres_sync.py
|   |   `-- timestamp_filter.py
|   |
|   |-- monitoring/
|   |   `-- job_history.py
|   |
|   `-- state/
|       |-- checkpoint.py
|       `-- timestamp_checkpoint.py
|
|-- tests/
|   `-- test_*.py
|
|-- docker-compose.yml
|-- recover_jobs.py
|-- requirements.txt
|-- .env.example
`-- README.md
```

---

## Getting Started

### Prerequisites

Before running SyncForge, install:

- Python 3.11
- Docker Desktop
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/Rishika73/syncforge-data-integration-platform.git
cd syncforge-data-integration-platform
```

### Step 2: Create a Virtual Environment

**macOS / Linux**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Open `.env` and configure your local PostgreSQL credentials.

Example:

```dotenv
POSTGRES_USER=syncforge
POSTGRES_PASSWORD=change_me
POSTGRES_DB=syncforge
POSTGRES_PORT=5433

SYNCFORGE_DATABASE_URL=postgresql://syncforge:change_me@127.0.0.1:5433/syncforge
```

Use a development-only password and ensure both password values match.

The `.env` file is excluded from Git version control.

### Step 5: Start PostgreSQL

Make sure Docker Desktop is running.

```bash
docker compose up -d
```

Docker Compose starts PostgreSQL 16.

When a new PostgreSQL data volume is initialized, the SQL script at `sql/init.sql` creates the database tables.

**Note:** Docker initialization scripts do not automatically rerun when using an existing database volume.

To apply the schema to an existing database:

```bash
docker compose exec -T postgres \
  psql -U syncforge -d syncforge < sql/init.sql
```

### Step 6: Export the Database Connection

On macOS or Linux:

```bash
export SYNCFORGE_DATABASE_URL="$(grep '^SYNCFORGE_DATABASE_URL=' .env | cut -d= -f2-)"
```

Docker Compose loads `.env` automatically, while the current Python implementation reads the database URL from the process environment.

---

## Running Data Integration Jobs

SyncForge uses a YAML-driven command-line interface.

Run the sample CSV synchronization job:

```bash
python -m syncforge.cli --config configs/customers_csv.yaml
```

Example successful output:

```text
Starting SyncForge job: csv_customers_sync
Run ID: 45
Records processed: 5
Synchronization completed successfully!
```

Run IDs vary across installations.

### Example YAML Configuration

File: `configs/customers_csv.yaml`

```yaml
sync_name: csv_customers_sync
source_name: csv_customers
sync_mode: snapshot
batch_size: 2

source:
  type: csv
  file_path: sample_data/customers.csv

destination:
  type: postgres
  connection_env: SYNCFORGE_DATABASE_URL
```

With this configuration, SyncForge reads the sample CSV, creates batches of two records, and upserts each batch into PostgreSQL.

### Creating a New Job

Create another YAML configuration file in the `configs/` directory.

For example:

`configs/my_customers.yaml`

Then execute it:

```bash
python -m syncforge.cli --config configs/my_customers.yaml
```

No application-code modification is required for supported connector types.

---

## Synchronization Strategies

### Incremental Synchronization

Incremental mode is intended for insert-only sources whose IDs increase strictly.

The synchronization engine:

1. Reads the last committed ID checkpoint.
2. Retrieves new source records.
3. Validates increasing IDs.
4. Writes records in batches.
5. Updates the checkpoint transactionally.

This reduces unnecessary processing for supported append-only feeds.

### Snapshot Synchronization

Snapshot mode processes all records from the configured source.

It performs PostgreSQL upserts, allowing existing records to be updated without creating duplicate database rows.

For example, if customer 101 changes their city from New York to Boston, the existing PostgreSQL record is updated.

**Important:** The current snapshot implementation uses per-batch commits, does not delete missing source records, and does not provide atomic publication of an entire refreshed dataset.

### Timestamp-Based Synchronization

A separate timestamp-based synchronization path supports detecting records with newer update timestamps.

The checkpoint contains:

```text
(last_updated_at, last_record_id)
```

This enables processing changes to existing IDs, provided the source supplies reliable update timestamps and consistent ordering.

Late-arriving changes with timestamps older than the committed checkpoint require additional reconciliation logic.

---

## Job Scheduling

SyncForge includes a sequential fixed-delay scheduler.

Example: run a CSV synchronization twice, waiting five seconds after each completed attempt.

```bash
python -m syncforge.scheduler \
  --config configs/customers_csv.yaml \
  --interval-seconds 5 \
  --max-runs 2
```

For continuous scheduling:

```bash
python -m syncforge.scheduler \
  --config configs/customers_csv.yaml \
  --interval-seconds 300
```

This starts another attempt approximately five minutes after the previous attempt finishes.

**Operational note:** The scheduler currently runs as a local Python process. It does not provide distributed job locking, durable orchestration, or automatic restart after host failure.

---

## Monitoring Dashboard

SyncForge includes a Streamlit dashboard for monitoring ingestion activity and job execution history.

### Dashboard Preview

![SyncForge Monitoring Dashboard](docs/images/dashboard.png)

### Dashboard Capabilities

- Total recorded synchronization runs
- Successful job executions
- Failed job executions
- Records processed
- Job execution counts
- Recent synchronization history
- Failed-job error information
- Manual refresh
- Filtering by execution status

### Launch the Dashboard

```bash
python -m streamlit run dashboard/app.py
```

Open your browser:

**http://localhost:8501**

The dashboard queries PostgreSQL for recent execution records.

Dashboard processing totals represent records handled across job runs, not necessarily unique records in the destination.

---

## Database Design

SyncForge uses four main PostgreSQL tables.

### `api_records`

Stores source records in JSONB format.

Important fields:

- `source_name`
- `id`
- `payload`
- `synced_at`

The composite primary key `(source_name, id)` prevents duplicate destination rows for the same source and record ID.

### `sync_checkpoints`

Stores the most recently processed ID for incremental synchronization jobs.

### `timestamp_checkpoints`

Stores composite timestamp/ID synchronization cursors.

### `sync_job_runs`

Tracks synchronization executions and their operational status.

Important fields include:

- `run_id`
- `sync_name`
- `source_name`
- `status`
- `records_processed`
- `started_at`
- `finished_at`
- `error_message`

All table definitions are maintained in:

`sql/init.sql`

---

## Testing and CI/CD

SyncForge uses Pytest for automated testing.

The test suite covers:

- Connector interfaces
- REST API pagination and retries
- CSV ingestion
- Checkpoint persistence
- Incremental synchronization
- PostgreSQL transactions
- Timestamp filtering
- Timestamp synchronization
- Batch processing
- Increasing-ID validation
- YAML configuration validation
- Snapshot and incremental modes
- Job scheduling
- Job execution history

### Run Tests Locally

```bash
python -m pytest -q
```

During local development, the project reached **69 passing automated tests**.

The exact test count may change as features and additional tests are introduced.

### GitHub Actions

The CI workflow is defined in:

`.github/workflows/ci.yml`

On pushes and pull requests targeting `main`, the workflow is configured to:

1. Check out the repository.
2. Install Python 3.11.
3. Install project dependencies.
4. Start PostgreSQL 16.
5. Initialize the database using `sql/init.sql`.
6. Check Python syntax.
7. Execute Pytest.

CI status can be viewed in the GitHub Actions tab.

---

## Reliability and Recovery

SyncForge includes several reliability-oriented mechanisms.

### HTTP Retries

The REST API connector retries selected transient HTTP failures, including HTTP 429 and selected 5xx responses.

### Transactional Checkpoints

Incremental record writes and checkpoint updates occur within PostgreSQL transactions to reduce the risk of committing synchronization progress without committed data.

### Duplicate Prevention

The destination uses PostgreSQL upserts to maintain one record per source and ID.

### Failure Tracking

Job execution history tracks successful and failed synchronization runs, including error information.

### Stale-Job Recovery

The recovery utility can mark execution-history entries as failed when they remain in the running state beyond a configured threshold.

Run:

```bash
python recover_jobs.py
```

This uses elapsed-time thresholds. It does not verify whether the worker process is still alive, so recovery thresholds must be chosen carefully.

---

## Current Limitations

SyncForge is a portfolio-oriented MVP designed to demonstrate data integration architecture, not a fully managed production service.

Current limitations include:

- The ID-based incremental engine assumes strictly increasing record IDs.
- Late-arriving source records may require lookback windows and reconciliation.
- Snapshot ingestion commits batches separately rather than publishing complete snapshots atomically.
- The scheduler is process-based and does not provide distributed locking.
- Stale-job recovery is timeout-based rather than heartbeat-based.
- Source-specific pagination consistency is not universally guaranteed.
- Additional testing and hardening are needed for production deployment.

These limitations represent potential areas for future development.

---

## Future Enhancements

Potential improvements include:

- Additional database and SaaS source connectors
- Schema evolution handling
- Data quality checks and quarantine tables
- Source-specific cursor pagination
- Lookback windows for late-arriving records
- Atomic snapshot staging and publication
- Distributed execution and scheduling
- Heartbeat-based job recovery
- Structured metrics and alerting
- Cloud deployment
- Integration with Airflow or another durable orchestrator

---

## What This Project Demonstrates

SyncForge demonstrates practical engineering skills relevant to Data Engineer, Platform Engineer, and Backend Engineer positions, including:

- Python software design
- Reusable connector architecture
- REST API integration
- PostgreSQL and JSONB
- Incremental ETL/ELT processing
- Checkpoint management
- Transaction handling
- Batch processing
- Docker-based development
- Automation and scheduling
- Observability and operational monitoring
- Unit and integration testing
- Configuration-driven application design
- GitHub Actions CI/CD

---

## Author

**Rishika Reddy Thumma**

GitHub: https://github.com/Rishika73

Built as a hands-on Data Engineering and backend platform engineering portfolio project.
