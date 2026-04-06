import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title="UNIFIL Research Library",
    page_icon="🇺🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Sans+3:wght@300;400;500;600&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #1a3a5c !important;
    border-right: none;
}
[data-testid="stSidebar"] * {
    color: #e8e0d0 !important;
}
[data-testid="stSidebar"] .stRadio label {
    font-size: 0.95rem;
    letter-spacing: 0.02em;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(232,224,208,0.2) !important;
}

/* Main header */
.library-header {
    display: flex;
    align-items: flex-end;
    gap: 1rem;
    padding: 2rem 0 1.5rem 0;
    border-bottom: 2px solid #1a3a5c;
    margin-bottom: 2rem;
}
.library-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem;
    font-weight: 700;
    color: #1a3a5c;
    line-height: 1.1;
    margin: 0;
}
.library-subtitle {
    font-size: 0.9rem;
    color: #5a6a7a;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 0;
    padding-bottom: 0.3rem;
}

/* Source cards */
.source-card {
    background: white;
    border: 1px solid #ddd8cc;
    border-left: 4px solid #1a3a5c;
    border-radius: 4px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.8rem;
    cursor: pointer;
    transition: all 0.15s ease;
}
.source-card:hover {
    border-left-color: #c8952a;
    box-shadow: 0 2px 12px rgba(26,58,92,0.08);
    transform: translateX(2px);
}
.source-card-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: #1a3a5c;
    margin: 0 0 0.3rem 0;
}
.source-card-meta {
    font-size: 0.82rem;
    color: #6b7c8d;
    margin: 0 0 0.6rem 0;
}
.source-card-abstract {
    font-size: 0.88rem;
    color: #3a3a3a;
    line-height: 1.5;
    margin: 0;
}

/* Tags */
.tag {
    display: inline-block;
    background: #eef2f7;
    color: #1a3a5c;
    border: 1px solid #c8d4e0;
    border-radius: 2px;
    font-size: 0.75rem;
    padding: 0.15rem 0.5rem;
    margin: 0.15rem;
    font-family: 'Source Sans 3', sans-serif;
    letter-spacing: 0.02em;
}
.tag-cluster {
    background: #1a3a5c;
    color: #e8e0d0;
    border-color: #1a3a5c;
}
.tag-actor {
    background: #f5ede0;
    color: #7a4510;
    border-color: #d4a96a;
}
.tag-lesson-sd {
    background: #edf7ed;
    color: #1a5c1a;
    border-color: #9ac99a;
}
.tag-lesson-ai {
    background: #f7f0ed;
    color: #5c2a1a;
    border-color: #c99a8a;
}

/* Detail panel */
.detail-section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1rem;
    font-weight: 600;
    color: #1a3a5c;
    border-bottom: 1px solid #ddd8cc;
    padding-bottom: 0.3rem;
    margin: 1.2rem 0 0.6rem 0;
}
.detail-body {
    font-size: 0.9rem;
    color: #2a2a2a;
    line-height: 1.6;
}

/* Metric cards */
.metric-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
}
.metric-card {
    background: white;
    border: 1px solid #ddd8cc;
    border-top: 3px solid #1a3a5c;
    border-radius: 4px;
    padding: 1rem 1.4rem;
    flex: 1;
    text-align: center;
}
.metric-number {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #1a3a5c;
    line-height: 1;
}
.metric-label {
    font-size: 0.78rem;
    color: #6b7c8d;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 0.3rem;
}

/* Filter panel */
.filter-panel {
    background: #ede9e0;
    border: 1px solid #ddd8cc;
    border-radius: 4px;
    padding: 1.2rem;
    margin-bottom: 1.5rem;
}

/* Bias flag */
.bias-flag {
    background: #fff8ec;
    border: 1px solid #e6c87a;
    border-left: 3px solid #c8952a;
    border-radius: 3px;
    padding: 0.7rem 1rem;
    font-size: 0.86rem;
    color: #4a3a1a;
    line-height: 1.5;
}

/* Gap card */
.gap-card {
    background: white;
    border: 1px solid #ddd8cc;
    border-left: 4px solid #c8952a;
    border-radius: 4px;
    padding: 1rem 1.3rem;
    margin-bottom: 0.7rem;
}
.gap-auto {
    border-left-color: #9ab8d0;
}
.gap-title {
    font-family: 'Playfair Display', serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: #1a3a5c;
    margin: 0 0 0.3rem 0;
}
.gap-desc {
    font-size: 0.85rem;
    color: #444;
    line-height: 1.5;
}

/* Divider */
.section-divider {
    border: none;
    border-top: 1px solid #ddd8cc;
    margin: 1.5rem 0;
}

/* UN emblem watermark in sidebar */
.sidebar-emblem {
    text-align: center;
    padding: 1.5rem 0 0.5rem 0;
    opacity: 0.85;
    font-size: 3rem;
}
.sidebar-version {
    text-align: center;
    font-size: 0.7rem;
    opacity: 0.4;
    letter-spacing: 0.05em;
}

/* Scrollable source list */
.source-list-container {
    max-height: 65vh;
    overflow-y: auto;
    padding-right: 0.3rem;
}

/* Streamlit overrides */
.stButton > button {
    background: #1a3a5c;
    color: white;
    border: none;
    border-radius: 3px;
    font-family: 'Source Sans 3', sans-serif;
    font-size: 0.85rem;
    letter-spacing: 0.04em;
    padding: 0.4rem 1rem;
}
.stButton > button:hover {
    background: #c8952a;
    color: white;
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: 3px;
    border-color: #c8d4e0;
    font-family: 'Source Sans 3', sans-serif;
    font-size: 0.9rem;
}
div[data-testid="stExpander"] {
    border: 1px solid #ddd8cc;
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-emblem">🇺🇳</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; padding-bottom:1rem;">
        <div style="font-family:'Playfair Display',serif; font-size:1.1rem; font-weight:700; letter-spacing:0.02em;">UNIFIL Lessons Learned</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<hr style="border-color:rgba(232,224,208,0.2); margin:0 0 1rem 0;">', unsafe_allow_html=True)
    
    page = st.radio(
        "Navigate",
        ["Source Library", "Thematic Navigator", "Timeline", "Actors Index", "Lessons Log", "Mind Map", "Gaps Register"],
        label_visibility="collapsed"
    )
    
    st.markdown('<hr style="border-color:rgba(232,224,208,0.2); margin:1rem 0;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.72rem; opacity:0.5; text-align:center; letter-spacing:0.05em;">UN DPO · PBPS · KMG<br>UNIFIL Lessons Learned 2026</div>', unsafe_allow_html=True)

# ── Page routing ──────────────────────────────────────────────────────────────
if page == "Source Library":
    from views.library import show
    show()
elif page == "Thematic Navigator":
    from views.thematic import show
    show()
elif page == "Timeline":
    from views.timeline import show
    show()
elif page == "Actors Index":
    from views.actors import show
    show()
elif page == "Lessons Log":
    from views.lessons import show
    show()
elif page == "Mind Map":
    from views.mindmap import show
    show()
elif page == "Gaps Register":
    from views.gaps import show
    show()
