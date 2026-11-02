"""
node_007 — Streamlit app entry.

  streamlit run main.py
"""

from __future__ import annotations

import streamlit as st

from node_003_visuals import SUBTITLE, TITLE
from node_004_layout import render_app

st.set_page_config(
    page_title=f"{TITLE} — {SUBTITLE}",
    layout="wide",
    initial_sidebar_state="collapsed",
)
render_app()
