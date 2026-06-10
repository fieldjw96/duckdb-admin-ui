from __future__ import annotations

from pathlib import Path

import streamlit as st

from config import default_db_path


st.set_page_config(page_title="DuckDB Admin UI", page_icon=":material/storage:", layout="wide")

st.title("DuckDB Admin UI")
st.write("Local, safety-first UI for querying and modifying DuckDB data.")

if "db_path" not in st.session_state:
    st.session_state.db_path = str(default_db_path())
if "write_mode" not in st.session_state:
    st.session_state.write_mode = False
if "sql_history" not in st.session_state:
    st.session_state.sql_history = []
if "op_log" not in st.session_state:
    st.session_state.op_log = []

st.sidebar.header("Connection")
db_path = st.sidebar.text_input("DuckDB file path", value=st.session_state.db_path)
st.session_state.db_path = db_path.strip()

exists = Path(st.session_state.db_path).exists()
if exists:
    st.sidebar.success("Database file found")
else:
    st.sidebar.warning("Database file not found yet")

st.session_state.write_mode = st.sidebar.toggle(
    "Enable write mode",
    value=st.session_state.write_mode,
    help="When off, mutating SQL is blocked.",
)

st.info(
    "Use pages in the left sidebar: Query, Table Browser, and Update/Delete. "
    "Write mode is disabled by default."
)
