from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd


MUTATING_PREFIXES = ("insert", "update", "delete", "create", "drop", "alter", "truncate", "copy")


@dataclass
class QueryResult:
    rows: pd.DataFrame | None
    rowcount: int | None
    message: str


def strip_sql_comments(sql: str) -> str:
    without_inline = re.sub(r"--.*?$", "", sql, flags=re.MULTILINE)
    without_block = re.sub(r"/\*.*?\*/", "", without_inline, flags=re.DOTALL)
    return without_block.strip()


def first_keyword(sql: str) -> str:
    cleaned = strip_sql_comments(sql).lstrip(" \n\t(")
    match = re.match(r"([a-zA-Z]+)", cleaned)
    return match.group(1).lower() if match else ""


def is_mutating_sql(sql: str) -> bool:
    keyword = first_keyword(sql)
    return keyword in MUTATING_PREFIXES


def has_where_clause(sql: str) -> bool:
    return bool(re.search(r"\bwhere\b", sql, flags=re.IGNORECASE))


def connect(db_path: str | Path) -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(db_path))


def execute_sql(
    db_path: str | Path,
    sql: str,
    write_mode: bool = False,
    fetch_limit: int = 10000,
) -> QueryResult:
    if not sql.strip():
        return QueryResult(rows=None, rowcount=None, message="No SQL provided.")

    mutating = is_mutating_sql(sql)
    if mutating and not write_mode:
        raise ValueError("Mutating SQL blocked. Enable write mode first.")

    with connect(db_path) as con:
        rel = con.execute(sql)
        keyword = first_keyword(sql)
        if keyword in ("select", "with", "show", "describe", "pragma"):
            rows = rel.fetch_df()
            if len(rows) > fetch_limit:
                rows = rows.head(fetch_limit)
                return QueryResult(
                    rows=rows,
                    rowcount=len(rows),
                    message=f"Result truncated to {fetch_limit} rows.",
                )
            return QueryResult(rows=rows, rowcount=len(rows), message=f"Returned {len(rows)} rows.")
        return QueryResult(rows=None, rowcount=rel.rowcount, message="Statement executed.")


def preview_delete_count(db_path: str | Path, table: str, where_clause: str) -> int:
    sql = f"SELECT COUNT(*) AS c FROM {table} WHERE {where_clause}"
    with connect(db_path) as con:
        return int(con.execute(sql).fetchone()[0])


def run_delete(
    db_path: str | Path,
    table: str,
    where_clause: str,
    allow_full_table_delete: bool = False,
) -> int:
    if not where_clause.strip() and not allow_full_table_delete:
        raise ValueError("Refusing full-table delete without explicit override.")
    sql = f"DELETE FROM {table} WHERE {where_clause}" if where_clause.strip() else f"DELETE FROM {table}"
    with connect(db_path) as con:
        con.execute("BEGIN")
        try:
            rel = con.execute(sql)
            con.execute("COMMIT")
            return rel.rowcount if rel.rowcount is not None else 0
        except Exception:
            con.execute("ROLLBACK")
            raise


def run_update(
    db_path: str | Path,
    table: str,
    set_clause: str,
    where_clause: str,
    allow_full_table_update: bool = False,
) -> int:
    if not set_clause.strip():
        raise ValueError("SET clause is required.")
    if not where_clause.strip() and not allow_full_table_update:
        raise ValueError("Refusing full-table update without explicit override.")

    sql = f"UPDATE {table} SET {set_clause}"
    if where_clause.strip():
        sql += f" WHERE {where_clause}"

    with connect(db_path) as con:
        con.execute("BEGIN")
        try:
            rel = con.execute(sql)
            con.execute("COMMIT")
            return rel.rowcount if rel.rowcount is not None else 0
        except Exception:
            con.execute("ROLLBACK")
            raise


def list_tables(db_path: str | Path) -> pd.DataFrame:
    sql = """
    SELECT table_schema, table_name
    FROM information_schema.tables
    WHERE table_type='BASE TABLE'
    ORDER BY table_schema, table_name
    """
    with connect(db_path) as con:
        return con.execute(sql).fetch_df()


def list_columns(db_path: str | Path, schema: str, table: str) -> pd.DataFrame:
    sql = """
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_schema = ? AND table_name = ?
    ORDER BY ordinal_position
    """
    with connect(db_path) as con:
        return con.execute(sql, [schema, table]).fetch_df()


def read_table_page(
    db_path: str | Path,
    schema: str,
    table: str,
    limit: int,
    offset: int,
    where_clause: str = "",
) -> pd.DataFrame:
    base = f"SELECT * FROM {schema}.{table}"
    if where_clause.strip():
        base += f" WHERE {where_clause}"
    base += f" LIMIT {int(limit)} OFFSET {int(offset)}"
    with connect(db_path) as con:
        return con.execute(base).fetch_df()


def maintenance_vacuum(db_path: str | Path) -> None:
    with connect(db_path) as con:
        con.execute("VACUUM")
