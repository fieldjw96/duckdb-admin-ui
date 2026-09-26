from __future__ import annotations

from pathlib import Path

import pytest

from config import default_db_path


def test_default_db_path_uses_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DUCKDB_PATH", "/some/where/my.duckdb")
    assert default_db_path() == Path("/some/where/my.duckdb")


def test_default_db_path_falls_back_to_working_directory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DUCKDB_PATH", raising=False)
    assert default_db_path() == Path("data.duckdb")
