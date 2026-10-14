
from typing import Any, Iterator

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from syncforge.connectors.base import SourceConnector


class RESTAPIConnector(SourceConnector):
    """
    REST API source connector with:
    - Pagination
    - Incremental ID filtering
    - Timeouts
    - Automatic retries
    - Rate-limit handling
    """

    def __init__(
        self,
        url: str,
        page_size: int = 10,
        since_id: int | None = None,
        cursor_parameter: str | None = None,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
    ):
        if page_size <= 0:
            raise ValueError("page_size must be positive")

        if since_id is not None and since_id < 0:
            raise ValueError("since_id cannot be negative")

        if cursor_parameter is not None and not cursor_parameter:
            raise ValueError("Invalid cursor parameter")

        if max_retries < 0:
            raise ValueError("max_retries cannot be negative")

        if backoff_factor < 0:
            raise ValueError("backoff_factor cannot be negative")

        self.url = url
        self.page_size = page_size
        self.since_id = since_id
        self.cursor_parameter = cursor_parameter
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.session = None

    def connect(self) -> None:
        retry_strategy = Retry(
            total=self.max_retries,
            connect=self.max_retries,
            read=self.max_retries,
            status=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[
                429,
                500,
                502,
                503,
                504,
            ],
            allowed_methods=["GET"],
            respect_retry_after_header=True,
        )

        adapter = HTTPAdapter(
            max_retries=retry_strategy
        )

        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def read_records(self) -> Iterator[dict[str, Any]]:
        if self.session is None:
            raise RuntimeError("Call connect() first")

        page = 1

        while True:
            params = {
                "_page": page,
                "_limit": self.page_size,
            }

            if (
                self.since_id is not None
                and self.cursor_parameter is not None
            ):
                params[self.cursor_parameter] = self.since_id

            response = self.session.get(
                self.url,
                params=params,
                timeout=30,
            )

            response.raise_for_status()
            data = response.json()

            if not isinstance(data, list):
                raise ValueError("Expected a JSON list")

            if not data:
                break

            for record in data:
                if not isinstance(record, dict):
                    raise ValueError(
                        "Expected JSON objects"
                    )

                if self.since_id is not None:
                    record_id = record.get("id")

                    if type(record_id) is not int:
                        raise ValueError(
                            "Record IDs must be integers"
                        )

                    if record_id <= self.since_id:
                        continue

                yield record

            if len(data) < self.page_size:
                break

            page += 1

    def close(self) -> None:
        if self.session is not None:
            self.session.close()
            self.session = None
