from __future__ import annotations

from datetime import datetime

import streamlit as st

from duckdb_service import execute_sql


st.title("Query Runner")
st.caption("Run SQL against the selected DuckDB file. Read-only mode is enforced unless write mode is enabled.")

sql = st.text_area(
    "SQL",
    value="SELECT * FROM accident_repair LIMIT 100;",
    height=180,
)

col1, col2 = st.columns([1, 1])
run = col1.button("Run SQL", type="primary")
clear_history = col2.button("Clear SQL history")

if clear_history:
    st.session_state.sql_history = []
    st.success("History cleared.")

if run:
    try:
        result = execute_sql(
            st.session_state.db_path,
            sql,
            write_mode=st.session_state.write_mode,
        )
        st.session_state.sql_history.insert(
            0,
            {
                "timestamp": datetime.utcnow().isoformat(),
                "sql": sql,
                "message": result.message,
            },
        )
        st.success(result.message)
        if result.rows is not None:
            st.dataframe(result.rows, use_container_width=True)
            csv = result.rows.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download CSV",
                data=csv,
                file_name="query_result.csv",
                mime="text/csv",
            )
    except Exception as exc:
        st.error(str(exc))

st.subheader("Recent SQL")
for item in st.session_state.sql_history[:20]:
    st.code(item["sql"], language="sql")
    st.caption(f'{item["timestamp"]} - {item["message"]}')
