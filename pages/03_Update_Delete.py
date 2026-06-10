from __future__ import annotations

from datetime import datetime

import streamlit as st

from duckdb_service import (
    list_tables,
    maintenance_vacuum,
    preview_delete_count,
    run_delete,
    run_update,
)


st.title("Update / Delete")
st.warning("Mutations are disabled unless write mode is enabled in the sidebar.", icon="⚠️")

if not st.session_state.write_mode:
    st.info("Enable write mode in the sidebar to use this page.")
    st.stop()

tables = list_tables(st.session_state.db_path)
table_options = [f"{r.table_schema}.{r.table_name}" for r in tables.itertuples(index=False)]
selected_table = st.selectbox("Target table", table_options)

tab_del, tab_upd, tab_maint = st.tabs(["Delete Rows", "Update Rows", "Maintenance"])

with tab_del:
    st.subheader("Delete Rows")
    where_clause = st.text_area("WHERE clause", height=120, placeholder="close_date >= '2023-11-01'")
    allow_full = st.checkbox("Allow full-table delete (dangerous)", value=False)

    if st.button("Preview delete count"):
        try:
            if not where_clause.strip() and not allow_full:
                st.error("WHERE clause required unless full-table override is checked.")
            else:
                count = (
                    preview_delete_count(st.session_state.db_path, selected_table, where_clause)
                    if where_clause.strip()
                    else -1
                )
                if count >= 0:
                    st.info(f"Rows matching filter: {count:,}")
                else:
                    st.info("Full-table delete selected.")
        except Exception as exc:
            st.error(str(exc))

    confirm_text = st.text_input("Type confirmation text", placeholder=f"DELETE {selected_table}")
    if st.button("Execute delete", type="primary"):
        if confirm_text.strip() != f"DELETE {selected_table}":
            st.error("Confirmation text mismatch.")
        else:
            try:
                deleted = run_delete(
                    st.session_state.db_path,
                    table=selected_table,
                    where_clause=where_clause,
                    allow_full_table_delete=allow_full,
                )
                st.session_state.op_log.insert(
                    0,
                    {
                        "timestamp": datetime.utcnow().isoformat(),
                        "operation": f"DELETE {selected_table}",
                        "message": f"Deleted {deleted} rows.",
                    },
                )
                st.success(f"Deleted {deleted} rows.")
            except Exception as exc:
                st.error(str(exc))

with tab_upd:
    st.subheader("Update Rows")
    set_clause = st.text_area("SET clause", height=90, placeholder="status = 'Closed'")
    where_clause_u = st.text_area("WHERE clause", height=90, placeholder="internal_case_number = 'ABC123'")
    allow_full_u = st.checkbox("Allow full-table update (dangerous)", value=False)
    confirm_update = st.text_input("Type confirmation text", placeholder=f"UPDATE {selected_table}")

    if st.button("Execute update", type="primary"):
        if confirm_update.strip() != f"UPDATE {selected_table}":
            st.error("Confirmation text mismatch.")
        else:
            try:
                updated = run_update(
                    st.session_state.db_path,
                    table=selected_table,
                    set_clause=set_clause,
                    where_clause=where_clause_u,
                    allow_full_table_update=allow_full_u,
                )
                st.session_state.op_log.insert(
                    0,
                    {
                        "timestamp": datetime.utcnow().isoformat(),
                        "operation": f"UPDATE {selected_table}",
                        "message": f"Updated {updated} rows.",
                    },
                )
                st.success(f"Updated {updated} rows.")
            except Exception as exc:
                st.error(str(exc))

with tab_maint:
    st.subheader("Maintenance")
    if st.button("Run VACUUM"):
        try:
            maintenance_vacuum(st.session_state.db_path)
            st.success("VACUUM completed.")
        except Exception as exc:
            st.error(str(exc))

st.subheader("Operation Log")
for item in st.session_state.op_log[:20]:
    st.write(f"{item['timestamp']} - {item['operation']} - {item['message']}")
