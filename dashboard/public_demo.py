
from datetime import datetime, timedelta, timezone

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="SyncForge | Live Demo",
    page_icon="⚙️",
    layout="wide",
)

st.title("⚙️ SyncForge")
st.subheader("Data Integration Monitoring Platform")

st.info(
    "Public portfolio demonstration using synthetic "
    "sample job data. No production database is connected."
)

st.markdown(
    """
    SyncForge is a configuration-driven data integration
    framework built using Python, PostgreSQL, and Docker.

    It supports REST API and CSV ingestion, incremental
    checkpoints, batch processing, job scheduling, and
    operational monitoring.
    """
)


def generate_demo_data():
    now = datetime.now(timezone.utc)

    examples = [
        ("csv_customers_sync", "CSV Customers", "success", 5),
        ("api_posts_sync", "REST API Posts", "success", 100),
        ("api_users_sync", "REST API Users", "success", 10),
        ("csv_customers_sync", "CSV Customers", "success", 5),
        ("api_posts_sync", "REST API Posts", "failed", 0),
        ("api_users_sync", "REST API Users", "success", 10),
        ("csv_customers_sync", "CSV Customers", "success", 5),
        ("api_posts_sync", "REST API Posts", "success", 100),
        ("api_users_sync", "REST API Users", "failed", 0),
        ("csv_customers_sync", "CSV Customers", "success", 5),
    ]

    rows = []

    for index, (name, source, status, count) in enumerate(
        examples, start=1
    ):
        started = now - timedelta(hours=index * 3)
        finished = started + timedelta(seconds=12 + index)

        rows.append(
            {
                "Run ID": index,
                "Job": name,
                "Source": source,
                "Status": status,
                "Records Processed": count,
                "Started At": started,
                "Finished At": finished,
                "Error": (
                    "Simulated transient API failure"
                    if status == "failed"
                    else ""
                ),
            }
        )

    return pd.DataFrame(rows)


df = generate_demo_data()

total = len(df)
successes = int((df["Status"] == "success").sum())
failures = int((df["Status"] == "failed").sum())
records = int(df["Records Processed"].sum())

st.divider()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Runs", total)
col2.metric("Successful Runs", successes)
col3.metric("Failed Runs", failures)
col4.metric("Records Processed", records)

st.subheader("📊 Job Execution Overview")

status_counts = pd.crosstab(
    df["Job"],
    df["Status"],
)

st.bar_chart(status_counts)

st.subheader("📋 Synchronization History")

selected_status = st.selectbox(
    "Filter executions",
    ["All", "success", "failed"],
)

filtered = df.copy()

if selected_status != "All":
    filtered = filtered[
        filtered["Status"] == selected_status
    ]

st.dataframe(
    filtered[
        [
            "Run ID",
            "Job",
            "Source",
            "Status",
            "Records Processed",
            "Started At",
            "Finished At",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

st.subheader("⚠️ Failure Analysis")

failed = df[df["Status"] == "failed"]

st.dataframe(
    failed[["Run ID", "Job", "Error"]],
    use_container_width=True,
    hide_index=True,
)

st.divider()

st.subheader("🔧 Platform Capabilities")

st.markdown(
    """
    - REST API and CSV source connectors
    - PostgreSQL JSONB destination
    - Incremental synchronization and checkpointing
    - Transactional upserts
    - Configurable batch processing
    - YAML-driven ingestion jobs
    - Automatic interval scheduling
    - Execution history and recovery utilities
    - Streamlit monitoring
    - Automated Pytest and GitHub Actions CI
    """
)

st.markdown(
    "**[View SyncForge source code on GitHub]"
    "(https://github.com/Rishika73/"
    "syncforge-data-integration-platform)**"
)

st.caption(
    "Demo statistics are illustrative, not actual "
    "production workload metrics."
)
