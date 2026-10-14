
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class SourceConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["csv", "rest_api"]
    file_path: str | None = None
    url: str | None = None
    page_size: int = Field(default=100, gt=0)
    cursor_parameter: str | None = None

    @model_validator(mode="after")
    def validate_source(self):
        if self.type == "csv":
            if not self.file_path:
                raise ValueError(
                    "CSV source requires file_path"
                )

        if self.type == "rest_api":
            if not self.url:
                raise ValueError(
                    "REST API source requires url"
                )

            if not self.url.startswith(
                ("http://", "https://")
            ):
                raise ValueError(
                    "REST API URL must use HTTP or HTTPS"
                )

        return self


class DestinationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["postgres"]
    connection_env: str = "SYNCFORGE_DATABASE_URL"


class JobConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sync_name: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    sync_mode: Literal["incremental", "snapshot"]
    batch_size: int = Field(default=1000, gt=0)

    source: SourceConfig
    destination: DestinationConfig

    @model_validator(mode="after")
    def validate_mode(self):
        if (
            self.source.type == "csv"
            and self.sync_mode == "incremental"
        ):
            raise ValueError(
                "CSV jobs should use snapshot mode "
                "until CSV-specific incremental handling "
                "is implemented"
            )
        return self


def load_config(path: str | Path) -> JobConfig:
    """Read and validate a YAML job configuration."""

    config_path = Path(path)

    with config_path.open(
        "r", encoding="utf-8"
    ) as file:
        raw_config = yaml.safe_load(file)

    if not isinstance(raw_config, dict):
        raise ValueError(
            "Configuration must be a YAML mapping"
        )

    return JobConfig.model_validate(raw_config)
