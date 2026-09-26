from __future__ import annotations

import os
from pathlib import Path


def default_db_path() -> Path:
    """The database the sidebar starts on: `DUCKDB_PATH` if set, else `data.duckdb` here."""
    return Path(os.environ.get("DUCKDB_PATH", "data.duckdb"))
