from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ETLConfig:
    """Configuration for the NetCDF → SQL ETL.

    Values can be provided via environment variables or directly in code.
    """

    # Database SQLAlchemy URL, e.g. postgresql+psycopg2://user:pass@localhost:5432/argo
    database_url: str = os.getenv("FLOATCHAT_DB_URL", "sqlite:///argo_etl.db")

    # Input directory containing NetCDF files (recursively searched)
    input_dir: str = os.getenv("FLOATCHAT_INPUT_DIR", "./data")

    # Batch sizes
    profile_batch_size: int = int(os.getenv("FLOATCHAT_PROFILE_BATCH", "5000"))
    measurement_batch_size: int = int(os.getenv("FLOATCHAT_MEAS_BATCH", "50000"))

    # Whether to create spatial geometry from lon/lat (requires PostGIS). If False, only lon/lat stored
    enable_postgis: bool = os.getenv("FLOATCHAT_ENABLE_POSTGIS", "false").lower() in {"1", "true", "yes"}

    # Acceptable QC flags for "good" data
    good_qc_flags: str = os.getenv("FLOATCHAT_GOOD_QC", "1,2")

    # Variables whitelist (comma-separated). Empty = ingest all variables present
    variables_whitelist: Optional[str] = os.getenv("FLOATCHAT_VARS", None)

    # File glob patterns to include (comma-separated). Defaults to *.nc
    include_patterns: str = os.getenv("FLOATCHAT_INCLUDE", "*.nc")

    # Max parallel workers for file parsing
    max_workers: int = int(os.getenv("FLOATCHAT_MAX_WORKERS", "4"))


def get_config() -> ETLConfig:
    return ETLConfig()



