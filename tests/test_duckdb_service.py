from __future__ import annotations

from pathlib import Path

import duckdb
import pytest

from duckdb_service import is_mutating_sql, run_delete, run_update


@pytest.fixture()
def db_file(tmp_path: Path) -> Path:
    path = tmp_path / "test.duckdb"
    with duckdb.connect(str(path)) as con:
        con.execute("CREATE TABLE t (id INTEGER, name VARCHAR)")
        con.execute("INSERT INTO t VALUES (1, 'a'), (2, 'b')")
    return path


def test_is_mutating_sql_detects_delete() -> None:
    assert is_mutating_sql("DELETE FROM t WHERE id = 1")
    assert not is_mutating_sql("SELECT * FROM t")


def test_run_delete_requires_guard(db_file: Path) -> None:
    with pytest.raises(ValueError):
        run_delete(db_file, "t", "", allow_full_table_delete=False)


def test_run_update_requires_where_unless_override(db_file: Path) -> None:
    with pytest.raises(ValueError):
        run_update(
            db_file,
            table="t",
            set_clause="name = 'x'",
            where_clause="",
            allow_full_table_update=False,
        )
