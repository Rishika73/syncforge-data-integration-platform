
import pytest
from pydantic import ValidationError

from syncforge.config.loader import load_config


def test_valid_csv_config(tmp_path):
    config_file = tmp_path / "job.yaml"

    config_file.write_text(
        """
sync_name: customers_sync
source_name: customers
sync_mode: snapshot
batch_size: 100

source:
  type: csv
  file_path: sample_data/customers.csv

destination:
  type: postgres
  connection_env: SYNCFORGE_DATABASE_URL
""",
        encoding="utf-8",
    )

    config = load_config(config_file)

    assert config.sync_name == "customers_sync"
    assert config.source.type == "csv"
    assert config.batch_size == 100


def test_missing_csv_path(tmp_path):
    config_file = tmp_path / "invalid.yaml"

    config_file.write_text(
        """
sync_name: customers_sync
source_name: customers
sync_mode: snapshot

source:
  type: csv

destination:
  type: postgres
""",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_config(config_file)


def test_invalid_batch_size(tmp_path):
    config_file = tmp_path / "invalid.yaml"

    config_file.write_text(
        """
sync_name: customers_sync
source_name: customers
sync_mode: snapshot
batch_size: -10

source:
  type: csv
  file_path: customers.csv

destination:
  type: postgres
""",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_config(config_file)


def test_csv_incremental_rejected(tmp_path):
    config_file = tmp_path / "invalid.yaml"

    config_file.write_text(
        """
sync_name: customers_sync
source_name: customers
sync_mode: incremental

source:
  type: csv
  file_path: customers.csv

destination:
  type: postgres
""",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_config(config_file)


def test_unknown_field_rejected(tmp_path):
    config_file = tmp_path / "invalid.yaml"

    config_file.write_text(
        """
sync_name: customers_sync
source_name: customers
sync_mode: snapshot
unexpected_setting: true

source:
  type: csv
  file_path: customers.csv

destination:
  type: postgres
""",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_config(config_file)
