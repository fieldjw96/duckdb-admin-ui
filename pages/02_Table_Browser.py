from __future__ import annotations

import streamlit as st

from duckdb_service import list_columns, list_tables, read_table_page


st.title("Table Browser")

try:
    tables = list_tables(st.session_state.db_path)
except Exception as exc:
    st.error(f"Could not read tables: {exc}")
    st.stop()

if tables.empty:
    st.warning("No tables found.")
    st.stop()

table_options = [f"{r.table_schema}.{r.table_name}" for r in tables.itertuples(index=False)]
selected = st.selectbox("Table", options=table_options)
schema, table = selected.split(".", 1)

cols = list_columns(st.session_state.db_path, schema, table)
st.subheader("Columns")
st.dataframe(cols, use_container_width=True)

st.subheader("Data Preview")
filter_clause = st.text_input("Optional WHERE clause", value="")
page_size = st.number_input("Page size", min_value=1, max_value=5000, value=100, step=50)
offset = st.number_input("Offset", min_value=0, value=0, step=100)

if st.button("Load page", type="primary"):
    try:
        page = read_table_page(
            st.session_state.db_path,
            schema=schema,
            table=table,
            limit=int(page_size),
            offset=int(offset),
            where_clause=filter_clause,
        )
        st.dataframe(page, use_container_width=True)
    except Exception as exc:
        st.error(str(exc))
