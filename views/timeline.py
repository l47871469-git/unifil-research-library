import sys
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).parent.parent))
from timeline_loader import build_html

_BASE = Path(__file__).parent.parent

def show():
    st.markdown("""
    <style>
    [data-testid="stMain"] { padding: 0 !important; }
    .main .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    iframe {
        width: 100% !important;
        min-width: 100% !important;
        display: block !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    html = build_html(
        json_path=str(_BASE / "data" / "unifil_timeline.json"),
        html_path=str(_BASE / "Event Timeline.html"),
    )
    components.html(html, height=12000, scrolling=True)
