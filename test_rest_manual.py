
from syncforge.connectors.rest_api import RESTAPIConnector


connector = RESTAPIConnector(
    "https://jsonplaceholder.typicode.com/posts",
    page_size=20,
)

count = 0

try:
    connector.connect()

    for record in connector.read_records():
        count += 1
        print(record["id"], record["title"])

finally:
    connector.close()

print(f"\nTotal records fetched: {count}")
