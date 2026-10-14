
import pytest

from syncforge.connectors.csv_source import CSVSourceConnector


def test_csv_reads_records(tmp_path):
    csv_file = tmp_path / "customers.csv"

    csv_file.write_text(
        "id,name\n1,Ava\n2,Noah\n3,Mia\n",
        encoding="utf-8",
    )

    source = CSVSourceConnector(str(csv_file))
    source.connect()

    try:
        records = list(source.read_records())
    finally:
        source.close()

    assert len(records) == 3
    assert [r["id"] for r in records] == [1, 2, 3]
    assert records[0]["name"] == "Ava"


def test_csv_missing_file(tmp_path):
    source = CSVSourceConnector(
        str(tmp_path / "missing.csv")
    )

    with pytest.raises(FileNotFoundError):
        source.connect()


def test_csv_requires_connection(tmp_path):
    csv_file = tmp_path / "customers.csv"
    csv_file.write_text("id,name\n1,Ava\n")

    source = CSVSourceConnector(str(csv_file))

    with pytest.raises(RuntimeError):
        list(source.read_records())


def test_csv_invalid_id(tmp_path):
    csv_file = tmp_path / "customers.csv"
    csv_file.write_text(
        "id,name\ninvalid,Ava\n",
        encoding="utf-8",
    )

    source = CSVSourceConnector(str(csv_file))
    source.connect()

    try:
        with pytest.raises(ValueError):
            list(source.read_records())
    finally:
        source.close()


def test_csv_missing_id_column(tmp_path):
    csv_file = tmp_path / "customers.csv"
    csv_file.write_text(
        "name,city\nAva,New York\n",
        encoding="utf-8",
    )

    source = CSVSourceConnector(str(csv_file))
    source.connect()

    try:
        with pytest.raises(ValueError):
            list(source.read_records())
    finally:
        source.close()
