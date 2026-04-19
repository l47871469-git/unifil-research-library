import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_utils import load_sources

MISSION_START = 1978
MISSION_END   = 2026


def _build_density_chart(sources):
    """Bar chart: number of sources published in each 4-year bucket."""
    bucket = 4
    years, counts, colors = [], [], []
    y = MISSION_START
    while y < MISSION_END:
        y_end = min(y + bucket, MISSION_END)
        count = sum(1 for s in sources if y <= s.get("year", 0) < y_end)
        years.append(y)
        counts.append(max(count, 0.05))
        colors.append("#1a3a5c" if count >= 2 else ("#9ab8d0" if count == 1 else "#e0dbd2"))
        y += bucket

    fig = go.Figure(go.Bar(
        x=years, y=counts, marker_color=colors,
        width=bucket * 0.85,
        hovertemplate="%{x}: %{customdata} source(s)<extra></extra>",
        customdata=[max(0, int(c)) for c in counts],
    ))
    fig.update_layout(
        height=90,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#f5f3ee",
        xaxis=dict(
            range=[MISSION_START - 1, MISSION_END + 1], showgrid=False,
            tickmode="linear", tick0=1978, dtick=8,
            tickfont=dict(size=10, color="#8a9ab0"), zeroline=False,
        ),
        yaxis=dict(visible=False),
        showlegend=False,
    )
    return fig


def show():
    sources = load_sources()

    st.markdown("""
    <div class="library-header">
        <div>
            <h1 class="library-title">Sources Timeline</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.9rem; color:#5a6a7a; margin-bottom:1.2rem; max-width:680px;">
        Browse sources by publication year. Use the slider to narrow to a specific period.
        The density bar shows how many sources were published in each 4-year window.
    </div>
    """, unsafe_allow_html=True)

    # Density chart — publication years only
    st.markdown("**Sources published per period**")
    st.plotly_chart(_build_density_chart(sources), use_container_width=True,
                    config={"displayModeBar": False})

    st.markdown("""
    <div style="display:flex; gap:1.5rem; font-size:0.75rem; color:#8a9ab0;
         margin-bottom:1rem; margin-top:-1rem;">
        <span><span style="display:inline-block;width:10px;height:10px;background:#1a3a5c;
            border-radius:1px;margin-right:4px;vertical-align:middle;"></span>2+ sources</span>
        <span><span style="display:inline-block;width:10px;height:10px;background:#9ab8d0;
            border-radius:1px;margin-right:4px;vertical-align:middle;"></span>1 source</span>
        <span><span style="display:inline-block;width:10px;height:10px;background:#e0dbd2;
            border-radius:1px;margin-right:4px;vertical-align:middle;"></span>None published</span>
    </div>
    """, unsafe_allow_html=True)

    year_range = st.slider(
        "Publication year range",
        min_value=MISSION_START, max_value=MISSION_END,
        value=(MISSION_START, MISSION_END), step=1, format="%d",
        key="sources_timeline_years",
    )
    y_start, y_end = year_range

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    in_range = sorted(
        [s for s in sources if y_start <= s.get("year", 0) <= y_end],
        key=lambda s: s.get("year", 0),
    )

    st.markdown(
        f'<div style="font-size:0.82rem; color:#6b7c8d; margin-bottom:0.8rem; '
        f'letter-spacing:0.04em; text-transform:uppercase;">'
        f'{len(in_range)} source{"s" if len(in_range) != 1 else ""} '
        f'published {y_start}–{y_end}</div>',
        unsafe_allow_html=True,
    )

    if not in_range:
        st.markdown("""
        <div style="background:#fff8ec; border:1px solid #e6c87a;
             border-left:3px solid #c8952a; border-radius:3px; padding:1rem;
             font-size:0.88rem; color:#5a3a0a;">
            No sources published in this period.
        </div>
        """, unsafe_allow_html=True)
        return

    for s in in_range:
        clusters   = s.get("thematic_clusters", [])[:2]
        clust_html = "".join([
            f'<span class="tag tag-cluster" style="font-size:0.68rem;">{c}</span>'
            for c in clusters
        ])
        abstract = s.get("abstract", "")
        preview  = abstract[:180] + "…" if len(abstract) > 180 else abstract
        st.markdown(f"""
        <div style="background:white; border:1px solid #ddd8cc;
             border-left:3px solid #1a3a5c; border-radius:3px;
             padding:0.9rem 1.1rem; margin-bottom:0.6rem;">
            <div style="display:flex; align-items:baseline; gap:0.8rem; margin-bottom:0.2rem;">
                <span style="font-family:'Playfair Display',serif; font-size:0.95rem;
                     font-weight:700; color:#1a3a5c; white-space:nowrap;">{s.get('year','')}</span>
                <span style="font-family:'Playfair Display',serif; font-size:0.9rem;
                     font-weight:600; color:#1a3a5c; line-height:1.25;">{s['title']}</span>
            </div>
            <div style="font-size:0.78rem; color:#8a9ab0; margin-bottom:0.4rem;">
                {s.get('author', '')} · {s.get('source_type', '')}
            </div>
            <div style="font-size:0.83rem; color:#3a3a3a; line-height:1.5;
                 margin-bottom:0.45rem;">{preview}</div>
            <div>{clust_html}</div>
        </div>
        """, unsafe_allow_html=True)
