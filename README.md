# DuckDB Admin UI

Local Streamlit app for safely querying and modifying DuckDB databases.

## What it does

- Query runner with result table and CSV download
- Table/schema browser using `information_schema`
- Guarded update/delete workflows with confirmation text
- Optional `VACUUM` maintenance action

## Install

```bash
cd "duckdb-admin-ui"
python -m pip install -e ".[dev]"
```

## Run

```bash
streamlit run app.py
python -m streamlit run app.py
```

Then open the local URL shown by Streamlit.

## Default DB path

The app defaults to:

- `WORK_DIR/solera.duckdb` when `WORK_DIR` is set
- otherwise: `%TEMP%/gecko/solera.duckdb`

You can override this in the sidebar.

## Safety model

- Write mode is **off by default**
- Mutating SQL is blocked in Query page unless write mode is enabled
- Delete/update page requires explicit confirmation text:
  - `DELETE <schema.table>`
  - `UPDATE <schema.table>`
- Full-table delete/update requires explicit override checkboxes
- Mutations are executed in explicit transactions (`BEGIN`/`COMMIT`/`ROLLBACK`)

## Recommended workflow for destructive changes

1. Back up the DB file
2. Use Query page to preview rows to be affected
3. Use Update/Delete page and run preview count first
4. Execute mutation and verify with a SELECT query
5. Run `VACUUM` for large deletes if needed

## Tests

```bash
pytest -q
```

