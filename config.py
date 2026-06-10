from __future__ import annotations

import os
import tempfile
from pathlib import Path


def default_db_path() -> Path:
    work_dir = Path(os.environ.get("WORK_DIR", "C:/tmp/gecko"))
    return work_dir / "solera.duckdb"
