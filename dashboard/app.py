
import os

import pandas as pd
import psycopg
import streamlit as st


st.set_page_config(
    page_title="SyncForge Monitoring",
    page_icon="⚙️",
    layout="wide",
)


def load_job_runs(connection_string: str) -> pd.DataFrame:
    """Read recent job executions from PostgreSQL."""

    query = """
        SELECT
            run_id,
            sync_name,
            source_name,
            status,
            records_processed,
            started_at,
            finished_at,
            error_message
        FROM sync_job_runs
        ORDER BY run_id DESC
        LIMIT 1000
    """

    with psycopg.connect(connection_string) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [column.name for column in cursor.description]

    return pd.DataFrame(rows, columns=columns)


st.title("⚙️ SyncForge Monitoring Dashboard")
st.caption("Data integration job execution and reliability")

connection_string = os.environ.get(
    "SYNCFORGE_DATABASE_URL"
)

if not connection_string:
    st.error(
        "SYNCFORGE_DATABASE_URL is not configured. "
        "Set it before launching the dashboard."
    )
    st.stop()

if st.button("Refresh data"):
    st.rerun()

try:
    df = load_job_runs(connection_string)
except psycopg.Error:
    st.error(
        "Could not connect to PostgreSQL or read job history. "
        "Check that Docker is running and the "
        "sync_job_runs table exists."
    )
    st.stop()

if df.empty:
    st.info(
        "No synchronization jobs have been recorded yet. "
        "Run a SyncForge job to populate this dashboard."
    )
    st.stop()

# Summary metrics
total_runs = len(df)
successful_runs = (df["status"] == "success").sum()
failed_runs = (df["status"] == "failed").sum()
running_runs = (df["status"] == "running").sum()

total_records = df.loc[
    df["status"] == "success",
    "records_processed",
].sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Runs", total_runs)
col2.metric("Successful", int(successful_runs))
col3.metric("Failed", int(failed_runs))
col4.metric("Records Processed", int(total_records))

st.subheader("Execution Overview")

status_counts = (
    df.groupby(["sync_name", "status"])
    .size()
    .unstack(fill_value=0)
)

st.bar_chart(status_counts)

st.subheader("Recent Synchronization Jobs")

status_options = ["All"] + sorted(
    df["status"].dropna().unique().tolist()
)

selected_status = st.selectbox(
    "Filter by status",
    status_options,
)

filtered = df.copy()

if selected_status != "All":
    filtered = filtered[
        filtered["status"] == selected_status
    ]

st.dataframe(
    filtered[
        [
            "run_id",
            "sync_name",
            "source_name",
            "status",
            "records_processed",
            "started_at",
            "finished_at",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

st.subheader("Failed Jobs")

failed = df[df["status"] == "failed"]

if failed.empty:
    st.success("No failures in the displayed job history.")
else:
    st.dataframe(
        failed[
            [
                "run_id",
                "sync_name",
                "started_at",
                "error_message",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

st.caption(
    "Metrics reflect the 1,000 most recent executions, "
    "not necessarily all historical jobs."
)
