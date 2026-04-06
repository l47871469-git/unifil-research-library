import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_utils import load_sources

MISSION_START = 1978
MISSION_END = 2026

KEY_EVENTS = [
    {"year": 1978, "label": "UNIFIL established", "type": "mandate", "detail": "UNSCR 425/426 establish UNIFIL following Israeli invasion. Original mandate: confirm Israeli withdrawal, restore peace, assist Lebanese government."},
    {"year": 1982, "label": "Israeli invasion", "type": "conflict", "detail": "Full-scale Israeli invasion of Lebanon. IDF advances to Beirut. PLO expelled. UNIFIL's operational environment transformed."},
    {"year": 1983, "label": "Beirut bombings", "type": "conflict", "detail": "US Embassy and MNF barracks bombings in Beirut. Hezbollah emerges as major actor. UNIFIL increasingly isolated in the south."},
    {"year": 1985, "label": "IDF partial withdrawal", "type": "mandate", "detail": "Israel withdraws to a self-declared Security Zone in southern Lebanon, maintained with SLA collaboration."},
    {"year": 1989, "label": "Taif Agreement", "type": "political", "detail": "Taif Agreement ends Lebanese Civil War. Reshapes political power-sharing but leaves Hezbollah armed as resistance."},
    {"year": 1993, "label": "Operation Accountability", "type": "conflict", "detail": "Israeli military operation against Hezbollah infrastructure in south Lebanon. Large-scale displacement of civilians."},
    {"year": 1996, "label": "Qana massacre", "type": "conflict", "detail": "Operation Grapes of Wrath. IDF shelling of UNIFIL compound kills over 100 civilians sheltering inside. Defining moment for UNIFIL's protection role."},
    {"year": 2000, "label": "Israeli withdrawal", "type": "mandate", "detail": "IDF withdraws from southern Lebanon. SLA collapses. UNIFIL verifies withdrawal, Blue Line established. Hezbollah emerges as dominant force in the south."},
    {"year": 2006, "label": "July War / UNSCR 1701", "type": "conflict", "detail": "34-day war between Israel and Hezbollah. UNSCR 1701 adopted: UNIFIL mandate expanded, force size tripled. Maritime Task Force established."},
    {"year": 2008, "label": "UNIFIL MTF operational", "type": "mandate", "detail": "UNIFIL Maritime Task Force reaches full operational capacity — the UN's only naval peacekeeping component."},
    {"year": 2023, "label": "October 7 / Gaza war", "type": "conflict", "detail": "Hamas attack on Israel triggers Gaza war. Hezbollah opens second front along Blue Line. UNIFIL enters heightened alert."},
    {"year": 2024, "label": "Blue Line escalation", "type": "conflict", "detail": "Sustained cross-border exchanges. UNIFIL positions targeted, peacekeepers injured. TCC withdrawal pressure mounts. Ceasefire reached late 2024."},
    {"year": 2025, "label": "UNSCR 2790 — final mandate", "type": "mandate", "detail": "Security Council sets final mandate extension to 31 December 2026. Mission closure process begins."},
    {"year": 2026, "label": "UNIFIL closes", "type": "mandate", "detail": "End of operations. Drawdown and withdrawal through 2027."},
]

EVENT_COLORS = {"mandate": "#1a3a5c", "conflict": "#8b1a1a", "political": "#5c5c1a"}

def get_sources_for_period(sources, year_start, year_end):
    matching = []
    for s in sources:
        cov = s.get("timeline_coverage", [])
        if len(cov) == 2:
            if cov[0] <= year_end and cov[1] >= year_start:
                matching.append(s)
        else:
            pub = s.get("year", 0)
            if year_start <= pub <= year_end:
                matching.append(s)
    return matching

def get_events_for_period(year_start, year_end):
    return [e for e in KEY_EVENTS if year_start <= e["year"] <= year_end]

def build_density_chart(sources):
    bucket_size = 4
    years, counts, colors = [], [], []
    y = MISSION_START
    while y < MISSION_END:
        y_end = min(y + bucket_size, MISSION_END)
        count = 0
        for s in sources:
            cov = s.get("timeline_coverage", [])
            if len(cov) == 2 and cov[0] <= y_end and cov[1] >= y:
                count += 1
            elif y <= s.get("year", 0) <= y_end:
                count += 1
        years.append(y)
        counts.append(max(count, 0.05))
        colors.append("#1a3a5c" if count >= 2 else ("#9ab8d0" if count == 1 else "#e0dbd2"))
        y += bucket_size

    fig = go.Figure(go.Bar(
        x=years,
        y=counts,
        marker_color=colors,
        width=bucket_size * 0.85,
        hovertemplate="%{x}: %{customdata} source(s)<extra></extra>",
        customdata=[max(0, int(c)) for c in counts],
    ))
    fig.update_layout(
        height=90,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#f5f3ee",
        xaxis=dict(range=[MISSION_START - 1, MISSION_END + 1], showgrid=False,
                   tickmode="linear", tick0=1978, dtick=8,
                   tickfont=dict(size=10, color="#8a9ab0"), zeroline=False),
        yaxis=dict(visible=False),
        showlegend=False,
    )
    return fig

def show():
    sources = load_sources()

    st.markdown("""
    <div class="library-header">
        <div>
            <p class="library-subtitle">1978 — 2026</p>
            <h1 class="library-title">Timeline</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.9rem; color:#5a6a7a; margin-bottom:1.2rem; max-width:680px;">
        Navigate UNIFIL's five decades using the year range slider. The density bar shows where 
        the corpus has strong coverage and where gaps exist. Key events are listed below — 
        click any to see sources that cover it.
    </div>
    """, unsafe_allow_html=True)

    # Density chart
    st.markdown("**Corpus coverage density**")
    st.plotly_chart(build_density_chart(sources), use_container_width=True, config={"displayModeBar": False})

    st.markdown("""
    <div style="display:flex; gap:1.5rem; font-size:0.75rem; color:#8a9ab0; margin-bottom:1rem; margin-top:-1rem;">
        <span><span style="display:inline-block;width:10px;height:10px;background:#1a3a5c;border-radius:1px;margin-right:4px;vertical-align:middle;"></span>2+ sources</span>
        <span><span style="display:inline-block;width:10px;height:10px;background:#9ab8d0;border-radius:1px;margin-right:4px;vertical-align:middle;"></span>1 source</span>
        <span><span style="display:inline-block;width:10px;height:10px;background:#e0dbd2;border-radius:1px;margin-right:4px;vertical-align:middle;"></span>No coverage</span>
    </div>
    """, unsafe_allow_html=True)

    # Year slider
    year_range = st.slider(
        "Select period",
        min_value=MISSION_START, max_value=MISSION_END,
        value=(MISSION_START, MISSION_END), step=1, format="%d",
        key="timeline_years"
    )
    y_start, y_end = year_range

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    col_events, col_sources = st.columns([1.2, 1])

    with col_events:
        events = get_events_for_period(y_start, y_end)
        st.markdown(f"""
        <div style="font-family:'Playfair Display',serif; font-size:1.05rem; font-weight:600;
             color:#1a3a5c; margin-bottom:0.6rem;">Key Events
             <span style="font-size:0.8rem; font-weight:400; color:#8a9ab0;">({len(events)} in period)</span>
        </div>
        <div style="display:flex; gap:1rem; font-size:0.72rem; margin-bottom:0.8rem;">
            <span style="color:#1a3a5c; font-weight:600;">Mandate</span>
            <span style="color:#8b1a1a; font-weight:600;">Conflict</span>
            <span style="color:#5c5c1a; font-weight:600;">Political</span>
        </div>
        """, unsafe_allow_html=True)

        if "selected_event" not in st.session_state:
            st.session_state.selected_event = None

        if not events:
            st.markdown('<div style="font-size:0.88rem; color:#8a9ab0; padding:1rem 0;">No key events in this period.</div>', unsafe_allow_html=True)
        else:
            for e in events:
                color = EVENT_COLORS.get(e["type"], "#555")
                is_sel = st.session_state.selected_event == e["year"]
                bg = "#fdf7ee" if is_sel else "white"
                border = "#c8952a" if is_sel else color
                st.markdown(f"""
                <div style="background:{bg}; border:1px solid #ddd8cc; border-left:3px solid {border};
                     border-radius:3px; padding:0.7rem 1rem; margin-bottom:0.4rem;">
                    <div style="display:flex; align-items:baseline; gap:0.6rem; margin-bottom:0.2rem;">
                        <span style="font-family:'Playfair Display',serif; font-size:1rem; font-weight:700; color:{color};">{e['year']}</span>
                        <span style="font-size:0.88rem; font-weight:600; color:#1a3a5c;">{e['label']}</span>
                    </div>
                    <div style="font-size:0.82rem; color:#4a4a4a; line-height:1.5;">{e['detail']}</div>
                </div>
                """, unsafe_allow_html=True)
                btn_label = "Hide sources" if is_sel else "Sources covering this"
                if st.button(btn_label, key=f"evt_{e['year']}"):
                    st.session_state.selected_event = None if is_sel else e["year"]
                    st.rerun()

    with col_sources:
        sel_event_year = st.session_state.get("selected_event")
        if sel_event_year:
            showing = get_sources_for_period(sources, sel_event_year, sel_event_year)
            sel_event = next((e for e in KEY_EVENTS if e["year"] == sel_event_year), None)
            header = f"Sources covering: {sel_event['label'] if sel_event else sel_event_year}"
        else:
            showing = get_sources_for_period(sources, y_start, y_end)
            header = f"Sources covering {y_start}–{y_end}"

        st.markdown(f"""
        <div style="font-family:'Playfair Display',serif; font-size:1.05rem; font-weight:600;
             color:#1a3a5c; margin-bottom:1rem;">{header}
             <span style="font-size:0.8rem; font-weight:400; color:#8a9ab0;">({len(showing)} source{"s" if len(showing)!=1 else ""})</span>
        </div>
        """, unsafe_allow_html=True)

        if not showing:
            st.markdown("""
            <div style="background:#fff8ec; border:1px solid #e6c87a; border-left:3px solid #c8952a;
                 border-radius:3px; padding:1rem; font-size:0.88rem; color:#5a3a0a;">
                No sources in the corpus currently cover this period. This is a coverage gap.
            </div>
            """, unsafe_allow_html=True)
        else:
            for s in showing:
                cov = s.get("timeline_coverage", [])
                period_str = f"{cov[0]}–{cov[1]}" if len(cov) == 2 else str(s.get("year", ""))
                clusters = s.get("thematic_clusters", [])[:2]
                clusters_html = "".join([f'<span class="tag tag-cluster" style="font-size:0.68rem;">{c}</span>' for c in clusters])
                st.markdown(f"""
                <div style="background:white; border:1px solid #ddd8cc; border-left:3px solid #1a3a5c;
                     border-radius:3px; padding:0.8rem 1rem; margin-bottom:0.6rem;">
                    <div style="font-family:'Playfair Display',serif; font-size:0.9rem; font-weight:600;
                         color:#1a3a5c; margin-bottom:0.2rem;">{s['title']}</div>
                    <div style="font-size:0.78rem; color:#8a9ab0; margin-bottom:0.4rem;">
                        {s['author']} · {s['year']} · <span style="color:#c8952a;">covers {period_str}</span>
                    </div>
                    <div style="font-size:0.82rem; color:#3a3a3a; line-height:1.45; margin-bottom:0.5rem;">
                        {s.get('abstract','')[:150]}{'…' if len(s.get('abstract',''))>150 else ''}
                    </div>
                    <div>{clusters_html}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        total_in_range = len(get_sources_for_period(sources, y_start, y_end))
        density = "rich" if total_in_range >= 3 else ("moderate" if total_in_range >= 1 else "sparse")
        density_color = "#2a7a2a" if density == "rich" else ("#c8952a" if density == "moderate" else "#8b1a1a")
        st.markdown(f"""
        <div style="background:#f5f3ee; border:1px solid #ddd8cc; border-radius:4px; padding:1rem; font-size:0.85rem;">
            <div style="font-weight:600; color:#1a3a5c; margin-bottom:0.3rem;">Period summary: {y_start}–{y_end}</div>
            <div style="color:#4a4a4a;">
                <span style="font-weight:600;">{total_in_range}</span> source{"s" if total_in_range!=1 else ""} · 
                <span style="color:{density_color}; font-weight:600;">{density} coverage</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
