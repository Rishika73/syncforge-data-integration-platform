
from syncforge.connectors.csv_source import CSVSourceConnector


source = CSVSourceConnector(
    "sample_data/customers.csv"
)

try:
    source.connect()

    records = list(source.read_records())

    for record in records:
        print(record["id"], record["name"], record["city"])

    print(f"\nTotal records: {len(records)}")

finally:
    source.close()
