"""
Entry Streamlit do repo.

  streamlit run main.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

_APP_DIR = Path(__file__).resolve().parent / "stage_0070_streamlit"
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from node_003_visuals import SUBTITLE, TITLE
from node_004_layout import render_app

st.set_page_config(
    page_title=f"{TITLE} — {SUBTITLE}",
    layout="wide",
    initial_sidebar_state="collapsed",
)
render_app()
