import streamlit as st
import plotly.graph_objects as go
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_utils import load_sources, THEMATIC_CLUSTERS


# ── Layout constants ──────────────────────────────────────────────────────────
R_CLUSTER = 2.4
R_SOURCE  = 3.9
R_LESSON  = 5.6   # with source ring
R_LESSON_DIRECT = 4.5  # without source ring

NAVY   = "#1a3a5c"
GOLD   = "#c8952a"
CREAM  = "#f5f3ee"
GREEN  = "#2a7a2a"
RUST   = "#8b3a1a"
SLATE  = "#4a7ab0"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _circular_mean(angles):
    """Stable circular mean of a list of angles in radians."""
    sx = sum(math.cos(a) for a in angles)
    sy = sum(math.sin(a) for a in angles)
    return math.atan2(sy, sx)


def _wrap(text, width=62, max_chars=280):
    """Word-wrap text for plotly hover labels."""
    if len(text) > max_chars:
        text = text[:max_chars] + "…"
    lines, buf = [], ""
    for word in text.split():
        if len(buf) + len(word) + 1 <= width:
            buf = (buf + " " + word).strip()
        else:
            if buf:
                lines.append(buf)
            buf = word
    if buf:
        lines.append(buf)
    return "<br>".join(lines)


def _fan_angles(center_angle, n, max_fan=0.72):
    """Return n evenly spaced angles in a fan around center_angle."""
    if n == 1:
        return [center_angle]
    fan = min(max_fan, 0.18 * (n - 1))
    return [center_angle - fan / 2 + i * fan / (n - 1) for i in range(n)]


def _label_anchor(angle):
    """Return (xanchor, yanchor) for a label positioned radially at angle."""
    c, s = math.cos(angle), math.sin(angle)
    xanchor = "left" if c > 0.25 else ("right" if c < -0.25 else "center")
    yanchor = "bottom" if s > 0.25 else ("top" if s < -0.25 else "middle")
    return xanchor, yanchor


# ── Main view ─────────────────────────────────────────────────────────────────

def show():
    sources = load_sources()

    # ── Header ───────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="library-header">
        <div>
            <p class="library-subtitle">Visual Overview</p>
            <h1 class="library-title">Lessons Mind Map</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.9rem; color:#5a6a7a; margin-bottom:1.5rem; max-width:700px;">
        Radial concept map connecting lessons learned candidates to their thematic clusters
        and source documents. Hover any node to read full text.
        Scroll to zoom · Drag to pan · Double-click to reset view.
    </div>
    """, unsafe_allow_html=True)

    # ── Filters ───────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 1.2, 1])
    with col1:
        cluster_filter = st.multiselect(
            "Filter by cluster", THEMATIC_CLUSTERS, key="mm_cluster"
        )
    with col2:
        type_filter = st.multiselect(
            "Lesson type",
            ["SOURCE-DERIVED", "ANALYTICAL INFERENCE"],
            key="mm_type",
        )
    with col3:
        show_sources = st.checkbox("Show source nodes", value=True, key="mm_sources")

    # ── Build filtered lesson list ────────────────────────────────────────────
    all_lessons = []
    for s in sources:
        for l in s.get("lessons_learned", []):
            s_clusters = s.get("thematic_clusters", [])
            tag = l.get("tag", "")
            if cluster_filter and not any(c in s_clusters for c in cluster_filter):
                continue
            if type_filter and tag not in type_filter:
                continue
            all_lessons.append({
                "text":          l.get("text", ""),
                "tag":           tag,
                "source_id":     s.get("id", ""),
                "source_title":  s.get("title", ""),
                "source_author": s.get("author", ""),
                "source_year":   s.get("year", ""),
                "clusters":      s_clusters,
            })

    active_clusters = cluster_filter if cluster_filter else THEMATIC_CLUSTERS
    clusters_used   = sorted(
        {c for l in all_lessons for c in l["clusters"] if c in active_clusters},
        key=lambda c: active_clusters.index(c),
    )

    if not all_lessons:
        st.info("No lessons match the current filters.")
        return

    n_c = len(clusters_used)

    # ── Cluster angular positions ─────────────────────────────────────────────
    cluster_angle = {
        c: 2 * math.pi * i / n_c - math.pi / 2
        for i, c in enumerate(clusters_used)
    }

    # ── Source positions (primary-cluster fan) ─────────────────────────────────
    active_source_ids = {l["source_id"] for l in all_lessons}
    source_map = {s["id"]: s for s in sources if s["id"] in active_source_ids}

    # Assign each source to its first active cluster, then fan within that cluster
    cluster_sources = {}
    source_primary = {}
    for sid, s in source_map.items():
        for c in s.get("thematic_clusters", []):
            if c in cluster_angle:
                cluster_sources.setdefault(c, []).append(sid)
                source_primary[sid] = c
                break

    source_angle = {}
    for cluster, sids in cluster_sources.items():
        for angle, sid in zip(_fan_angles(cluster_angle[cluster], len(sids), 0.55), sids):
            source_angle[sid] = angle

    # ── Collect graph elements ────────────────────────────────────────────────
    edge_cc_x, edge_cc_y  = [], []   # center → cluster
    edge_cs_x, edge_cs_y  = [], []   # cluster → source
    edge_sl_x, edge_sl_y  = [], []   # source  → lesson
    edge_cl_x, edge_cl_y  = [], []   # cluster → lesson (direct mode)

    c_x, c_y, c_hover = [], [], []
    s_x, s_y, s_hover = [], [], []
    l_sd_x, l_sd_y, l_sd_hover = [], [], []
    l_ai_x, l_ai_y, l_ai_hover = [], [], []
    annotations = []

    R_L = R_LESSON if show_sources else R_LESSON_DIRECT

    # Cluster nodes
    for cluster in clusters_used:
        θ = cluster_angle[cluster]
        cx, cy = R_CLUSTER * math.cos(θ), R_CLUSTER * math.sin(θ)
        c_x.append(cx); c_y.append(cy)
        n_ll = sum(1 for l in all_lessons if cluster in l["clusters"])
        c_hover.append(f"<b>{cluster}</b><br>{n_ll} lesson(s)")

        edge_cc_x += [0, cx, None]
        edge_cc_y += [0, cy, None]

        # Annotation label
        lr = R_CLUSTER + 0.52
        lx, ly = lr * math.cos(θ), lr * math.sin(θ)
        xa, ya = _label_anchor(θ)
        annotations.append(dict(
            x=lx, y=ly, text=cluster,
            showarrow=False,
            font=dict(family="Source Sans 3, sans-serif", size=9.5, color=NAVY),
            xanchor=xa, yanchor=ya,
            bgcolor="rgba(245,243,238,0.75)",
        ))

    # Source nodes + edges
    for sid, s in source_map.items():
        θ = source_angle.get(sid, 0)
        sx, sy = R_SOURCE * math.cos(θ), R_SOURCE * math.sin(θ)
        s_x.append(sx); s_y.append(sy)

        short = s["title"][:55] + "…" if len(s["title"]) > 55 else s["title"]
        s_hover.append(
            f"<b>{short}</b><br>"
            f"{s.get('author','')}, {s.get('year','')}<br>"
            f"{s.get('source_type','')}"
        )

        # Cluster → source edges (for each cluster the source belongs to)
        for c in s.get("thematic_clusters", []):
            if c in cluster_angle:
                θc = cluster_angle[c]
                edge_cs_x += [R_CLUSTER * math.cos(θc), sx, None]
                edge_cs_y += [R_CLUSTER * math.sin(θc), sy, None]

    # Lesson nodes + edges
    source_lessons_map = {}
    for l in all_lessons:
        source_lessons_map.setdefault(l["source_id"], []).append(l)

    for sid, lessons in source_lessons_map.items():
        θ_src = source_angle.get(sid, cluster_angle.get(
            next((c for c in lessons[0]["clusters"] if c in cluster_angle), None), 0
        ))
        sx, sy = R_SOURCE * math.cos(θ_src), R_SOURCE * math.sin(θ_src)

        for θ_l, l in zip(_fan_angles(θ_src, len(lessons)), lessons):
            lx = R_L * math.cos(θ_l)
            ly = R_L * math.sin(θ_l)

            hover = (
                f"<b>{l['tag']}</b><br>"
                f"{_wrap(l['text'])}<br><br>"
                f"<i>— {l['source_author']}, {l['source_year']}</i>"
            )

            if show_sources:
                edge_sl_x += [sx, lx, None]
                edge_sl_y += [sy, ly, None]
            else:
                primary = next((c for c in l["clusters"] if c in cluster_angle), None)
                if primary:
                    θc = cluster_angle[primary]
                    edge_cl_x += [R_CLUSTER * math.cos(θc), lx, None]
                    edge_cl_y += [R_CLUSTER * math.sin(θc), ly, None]

            if l["tag"] == "SOURCE-DERIVED":
                l_sd_x.append(lx); l_sd_y.append(ly); l_sd_hover.append(hover)
            else:
                l_ai_x.append(lx); l_ai_y.append(ly); l_ai_hover.append(hover)

    # ── Build figure ──────────────────────────────────────────────────────────
    fig = go.Figure()

    HL = dict(
        bgcolor="white",
        font=dict(family="Source Sans 3, sans-serif", size=12, color=NAVY),
        namelength=-1,
    )

    # --- Edges (drawn first / behind) ---
    fig.add_trace(go.Scatter(
        x=edge_cc_x, y=edge_cc_y, mode="lines",
        line=dict(color=NAVY, width=1.6),
        hoverinfo="none", showlegend=False,
    ))

    if show_sources:
        fig.add_trace(go.Scatter(
            x=edge_cs_x, y=edge_cs_y, mode="lines",
            line=dict(color=GOLD, width=0.8, dash="dot"),
            hoverinfo="none", showlegend=False,
        ))
        fig.add_trace(go.Scatter(
            x=edge_sl_x, y=edge_sl_y, mode="lines",
            line=dict(color="#b8c8d8", width=0.7),
            hoverinfo="none", showlegend=False,
        ))
    else:
        fig.add_trace(go.Scatter(
            x=edge_cl_x, y=edge_cl_y, mode="lines",
            line=dict(color="#b8c8d8", width=0.8),
            hoverinfo="none", showlegend=False,
        ))

    # --- Cluster nodes ---
    fig.add_trace(go.Scatter(
        x=c_x, y=c_y, mode="markers",
        marker=dict(color=GOLD, size=18, line=dict(color="white", width=2.5)),
        hovertext=c_hover, hoverinfo="text",
        hoverlabel=dict(**HL, bordercolor=GOLD),
        showlegend=False,
    ))

    # --- Source nodes ---
    if show_sources and s_x:
        fig.add_trace(go.Scatter(
            x=s_x, y=s_y, mode="markers",
            marker=dict(
                color=SLATE, size=12, symbol="diamond",
                line=dict(color="white", width=1.5),
            ),
            hovertext=s_hover, hoverinfo="text",
            hoverlabel=dict(**HL, bordercolor=SLATE),
            name="Source document", showlegend=True,
        ))

    # --- Lesson nodes ---
    if l_sd_x:
        fig.add_trace(go.Scatter(
            x=l_sd_x, y=l_sd_y, mode="markers",
            marker=dict(color=GREEN, size=10, opacity=0.88,
                        line=dict(color="white", width=1.2)),
            hovertext=l_sd_hover, hoverinfo="text",
            hoverlabel=dict(**HL, bordercolor=GREEN),
            name="Source-derived", showlegend=True,
        ))
    if l_ai_x:
        fig.add_trace(go.Scatter(
            x=l_ai_x, y=l_ai_y, mode="markers",
            marker=dict(color=RUST, size=10, opacity=0.88,
                        line=dict(color="white", width=1.2)),
            hovertext=l_ai_hover, hoverinfo="text",
            hoverlabel=dict(**HL, bordercolor=RUST),
            name="Analytical inference", showlegend=True,
        ))

    # --- Centre node (drawn last so it sits on top) ---
    fig.add_trace(go.Scatter(
        x=[0], y=[0], mode="markers+text",
        marker=dict(color=NAVY, size=40, line=dict(color="white", width=3)),
        text=["Lessons<br>Learned"],
        textposition="middle center",
        textfont=dict(family="Source Sans 3, sans-serif", size=10, color="white"),
        hoverinfo="skip", showlegend=False,
    ))

    # ── Layout ────────────────────────────────────────────────────────────────
    axis = dict(
        visible=False, zeroline=False,
        showgrid=False, showticklabels=False,
        range=[-8.0, 8.0],
    )

    fig.update_layout(
        paper_bgcolor=CREAM,
        plot_bgcolor=CREAM,
        margin=dict(l=10, r=10, t=10, b=10),
        height=760,
        xaxis=dict(**axis),
        yaxis=dict(**axis, scaleanchor="x", scaleratio=1),
        dragmode="pan",
        annotations=annotations,
        legend=dict(
            x=0.01, y=0.01,
            bgcolor="rgba(245,243,238,0.92)",
            bordercolor="#ddd8cc",
            borderwidth=1,
            font=dict(family="Source Sans 3, sans-serif", size=11, color=NAVY),
        ),
        hoverdistance=14,
    )

    st.plotly_chart(fig, use_container_width=True, config={
        "scrollZoom": True,
        "displayModeBar": True,
        "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
        "displaylogo": False,
        "toImageButtonOptions": {
            "format": "png",
            "filename": "unifil_lessons_mindmap",
            "scale": 2,
        },
    })

    # ── Footer stats ──────────────────────────────────────────────────────────
    n_shown = len(l_sd_x) + len(l_ai_x)
    n_src   = len(source_map)
    n_cl    = len(clusters_used)
    parts   = [
        f"<b>{n_shown}</b> lesson{'s' if n_shown != 1 else ''}",
        f"<b>{n_cl}</b> cluster{'s' if n_cl != 1 else ''}",
    ]
    if show_sources:
        parts.append(f"<b>{n_src}</b> source document{'s' if n_src != 1 else ''}")
    st.markdown(
        '<div style="font-size:0.8rem; color:#8a9ab0; text-align:center; '
        'margin-top:0.4rem; letter-spacing:0.02em;">'
        + " · ".join(parts)
        + " · hover nodes to read full text</div>",
        unsafe_allow_html=True,
    )
