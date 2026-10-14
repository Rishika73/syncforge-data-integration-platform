
from syncforge.config.loader import JobConfig
from syncforge.connectors.csv_source import CSVSourceConnector
from syncforge.connectors.rest_api import RESTAPIConnector


def create_source(config: JobConfig):
    """Create a source connector from validated configuration."""

    if config.source.type == "csv":
        return CSVSourceConnector(
            config.source.file_path
        )

    if config.source.type == "rest_api":
        return RESTAPIConnector(
            url=config.source.url,
            page_size=config.source.page_size,
            cursor_parameter=config.source.cursor_parameter,
        )

    raise ValueError(
        f"Unsupported source: {config.source.type}"
    )
