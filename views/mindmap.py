import streamlit as st
import plotly.graph_objects as go
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_utils import load_sources, THEMATIC_CLUSTERS


# ── Colours ───────────────────────────────────────────────────────────────────
NAVY   = "#1a3a5c"
GOLD   = "#c8952a"
CREAM  = "#f5f3ee"
GREEN  = "#2a7a2a"
RUST   = "#8b3a1a"
SLATE  = "#4a7ab0"

DIM_A  = 0.10   # opacity for dimmed elements when a node is selected


def _rgba(hex_color, alpha):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ── Radii ─────────────────────────────────────────────────────────────────────
R_CLUSTER       = 2.4
R_SOURCE        = 3.9
R_LESSON        = 5.6
R_LESSON_DIRECT = 4.5


# ── Trace indices (fixed — critical for click-detection) ──────────────────────
T_EDGE_DIM   = 0   # all edges, dimmed when selection active
T_EDGE_BRIGHT= 1   # highlighted edges drawn on top
T_CLUSTER    = 2   # cluster nodes
T_SOURCE     = 3   # source nodes
T_SD         = 4   # source-derived lesson nodes
T_AI         = 5   # analytical-inference lesson nodes
T_CENTER     = 6   # center node (not selectable)
INTERACTIVE  = {T_CLUSTER, T_SOURCE, T_SD, T_AI}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _wrap(text, width=62, max_chars=280):
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
    if n == 1:
        return [center_angle]
    fan = min(max_fan, 0.18 * (n - 1))
    return [center_angle - fan / 2 + i * fan / (n - 1) for i in range(n)]


def _label_anchor(angle):
    c, s = math.cos(angle), math.sin(angle)
    xa = "left" if c > 0.25 else ("right" if c < -0.25 else "center")
    ya = "bottom" if s > 0.25 else ("top" if s < -0.25 else "middle")
    return xa, ya


def _segs_to_xy(segs):
    """Convert list of (x0,y0,x1,y1,...) dicts to None-separated x,y lists."""
    xs, ys = [], []
    for s in segs:
        xs += [s["x0"], s["x1"], None]
        ys += [s["y0"], s["y1"], None]
    return xs, ys


def _opacities(n, highlighted):
    """Return per-node opacity list. highlighted=None → all bright."""
    if highlighted is None:
        return [1.0] * n
    return [1.0 if i in highlighted else DIM_A for i in range(n)]


# ── Highlight computation ─────────────────────────────────────────────────────

def _compute_highlight(sel, cluster_list, source_list, sd_list, ai_list, show_sources):
    """
    sel: (curve_number, point_number) or None
    Returns dict with sets of highlighted indices, or None if no selection.
    """
    if sel is None:
        return None

    curve_num, pt_num = sel
    hi_cl  = set()
    hi_src = set()
    hi_sd  = set()
    hi_ai  = set()

    if curve_num == T_CLUSTER:
        if pt_num >= len(cluster_list):
            return None
        cl_name = cluster_list[pt_num]["name"]
        hi_cl.add(pt_num)
        for si, src in enumerate(source_list):
            if cl_name in src["clusters"]:
                hi_src.add(si)
        for li, l in enumerate(sd_list):
            if cl_name in l["clusters"]:
                hi_sd.add(li)
        for li, l in enumerate(ai_list):
            if cl_name in l["clusters"]:
                hi_ai.add(li)

    elif curve_num == T_SOURCE:
        if pt_num >= len(source_list):
            return None
        src = source_list[pt_num]
        hi_src.add(pt_num)
        for ci, cl in enumerate(cluster_list):
            if cl["name"] in src["clusters"]:
                hi_cl.add(ci)
        for li, l in enumerate(sd_list):
            if l["source_id"] == src["id"]:
                hi_sd.add(li)
        for li, l in enumerate(ai_list):
            if l["source_id"] == src["id"]:
                hi_ai.add(li)

    elif curve_num == T_SD:
        if pt_num >= len(sd_list):
            return None
        l = sd_list[pt_num]
        hi_sd.add(pt_num)
        for si, src in enumerate(source_list):
            if src["id"] == l["source_id"]:
                hi_src.add(si)
                for ci, cl in enumerate(cluster_list):
                    if cl["name"] in src["clusters"]:
                        hi_cl.add(ci)
                break

    elif curve_num == T_AI:
        if pt_num >= len(ai_list):
            return None
        l = ai_list[pt_num]
        hi_ai.add(pt_num)
        for si, src in enumerate(source_list):
            if src["id"] == l["source_id"]:
                hi_src.add(si)
                for ci, cl in enumerate(cluster_list):
                    if cl["name"] in src["clusters"]:
                        hi_cl.add(ci)
                break

    else:
        return None

    return {"cl": hi_cl, "src": hi_src, "sd": hi_sd, "ai": hi_ai}


def _hi_segs(segs, predicate):
    """Filter edge segments by predicate."""
    return [s for s in segs if predicate(s)]


# ── Main view ─────────────────────────────────────────────────────────────────

def show():
    sources = load_sources()

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
        Click a node to highlight its connections · Click background to reset.
        Scroll to zoom · Drag to pan.
    </div>
    """, unsafe_allow_html=True)

    # ── Filters ───────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 1.2, 1])
    with col1:
        cluster_filter = st.multiselect("Filter by cluster", THEMATIC_CLUSTERS, key="mm_cluster")
    with col2:
        type_filter = st.multiselect("Lesson type", ["SOURCE-DERIVED", "ANALYTICAL INFERENCE"], key="mm_type")
    with col3:
        show_sources = st.checkbox("Show source nodes", value=True, key="mm_sources")

    # ── Selection state ───────────────────────────────────────────────────────
    if "mm_selected" not in st.session_state:
        st.session_state.mm_selected = None
    mm_sel = st.session_state.mm_selected  # (curve_num, point_num) or None

    # ── Build lesson list ─────────────────────────────────────────────────────
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
    clusters_used = sorted(
        {c for l in all_lessons for c in l["clusters"] if c in active_clusters},
        key=lambda c: active_clusters.index(c),
    )

    if not all_lessons:
        st.info("No lessons match the current filters.")
        return

    n_c = len(clusters_used)

    # ── Angular positions ─────────────────────────────────────────────────────
    cluster_angle = {
        c: 2 * math.pi * i / n_c - math.pi / 2
        for i, c in enumerate(clusters_used)
    }

    active_source_ids = {l["source_id"] for l in all_lessons}
    source_map = {s["id"]: s for s in sources if s["id"] in active_source_ids}

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

    R_L = R_LESSON if show_sources else R_LESSON_DIRECT

    # ── Build indexed node lists ──────────────────────────────────────────────
    cluster_list = []
    for cluster in clusters_used:
        θ = cluster_angle[cluster]
        n_ll = sum(1 for l in all_lessons if cluster in l["clusters"])
        cluster_list.append({
            "name": cluster, "angle": θ,
            "x": R_CLUSTER * math.cos(θ),
            "y": R_CLUSTER * math.sin(θ),
            "hover": f"<b>{cluster}</b><br>{n_ll} lesson{'s' if n_ll != 1 else ''}",
        })

    source_list = []
    source_idx_map = {}  # source_id → index in source_list
    for sid, s in source_map.items():
        θ = source_angle.get(sid, 0)
        short = s["title"][:55] + "…" if len(s["title"]) > 55 else s["title"]
        source_list.append({
            "id": sid, "angle": θ,
            "x": R_SOURCE * math.cos(θ),
            "y": R_SOURCE * math.sin(θ),
            "clusters": s.get("thematic_clusters", []),
            "hover": (
                f"<b>{short}</b><br>"
                f"{s.get('author','')}, {s.get('year','')}<br>"
                f"{s.get('source_type','')}"
            ),
        })
        source_idx_map[sid] = len(source_list) - 1

    sd_list, ai_list = [], []
    for sid, lessons in {l["source_id"]: [] for l in all_lessons}.items():
        pass  # rebuild properly below

    source_lessons = {}
    for l in all_lessons:
        source_lessons.setdefault(l["source_id"], []).append(l)

    for sid, lessons in source_lessons.items():
        θ_src = source_angle.get(sid, cluster_angle.get(
            next((c for c in lessons[0]["clusters"] if c in cluster_angle), None), 0
        ))
        sx = R_SOURCE * math.cos(θ_src)
        sy = R_SOURCE * math.sin(θ_src)
        for θ_l, l in zip(_fan_angles(θ_src, len(lessons)), lessons):
            lx = R_L * math.cos(θ_l)
            ly = R_L * math.sin(θ_l)
            hover = (
                f"<b>{l['tag']}</b><br>"
                f"{_wrap(l['text'])}<br><br>"
                f"<i>— {l['source_author']}, {l['source_year']}</i>"
            )
            entry = {"source_id": sid, "clusters": l["clusters"], "x": lx, "y": ly, "hover": hover,
                     "sx": sx, "sy": sy, "θ_src": θ_src}
            if l["tag"] == "SOURCE-DERIVED":
                sd_list.append(entry)
            else:
                ai_list.append(entry)

    # ── Build edge segments with metadata ─────────────────────────────────────
    cc_segs = []  # center → cluster
    cs_segs = []  # cluster → source
    sl_segs = []  # source → lesson (or cluster → lesson if not show_sources)

    for ci, cl in enumerate(cluster_list):
        cc_segs.append({"x0": 0, "y0": 0, "x1": cl["x"], "y1": cl["y"], "ci": ci})

    if show_sources:
        for si, src in enumerate(source_list):
            for ci, cl in enumerate(cluster_list):
                if cl["name"] in src["clusters"]:
                    cs_segs.append({"x0": cl["x"], "y0": cl["y"], "x1": src["x"], "y1": src["y"],
                                    "ci": ci, "si": si})
        for li, l in enumerate(sd_list):
            si = source_idx_map.get(l["source_id"])
            if si is not None:
                sl_segs.append({"x0": l["sx"], "y0": l["sy"], "x1": l["x"], "y1": l["y"],
                                 "si": si, "sd": True, "li": li})
        for li, l in enumerate(ai_list):
            si = source_idx_map.get(l["source_id"])
            if si is not None:
                sl_segs.append({"x0": l["sx"], "y0": l["sy"], "x1": l["x"], "y1": l["y"],
                                 "si": si, "sd": False, "li": li})
    else:
        # Direct cluster → lesson edges
        for li, l in enumerate(sd_list):
            primary = next((c for c in l["clusters"] if c in cluster_angle), None)
            if primary:
                ci = next(i for i, cl in enumerate(cluster_list) if cl["name"] == primary)
                cl = cluster_list[ci]
                sl_segs.append({"x0": cl["x"], "y0": cl["y"], "x1": l["x"], "y1": l["y"],
                                 "ci": ci, "sd": True, "li": li})
        for li, l in enumerate(ai_list):
            primary = next((c for c in l["clusters"] if c in cluster_angle), None)
            if primary:
                ci = next(i for i, cl in enumerate(cluster_list) if cl["name"] == primary)
                cl = cluster_list[ci]
                sl_segs.append({"x0": cl["x"], "y0": cl["y"], "x1": l["x"], "y1": l["y"],
                                 "ci": ci, "sd": False, "li": li})

    all_segs = cc_segs + cs_segs + sl_segs

    # ── Compute highlight ─────────────────────────────────────────────────────
    hi = _compute_highlight(mm_sel, cluster_list, source_list, sd_list, ai_list, show_sources)

    is_selecting = hi is not None

    def _seg_highlighted(seg):
        """True if this edge segment connects two highlighted nodes."""
        if "ci" in seg and "si" in seg:       # cluster→source
            return seg["ci"] in hi["cl"] and seg["si"] in hi["src"]
        if "ci" in seg and "li" in seg:       # cluster→lesson (direct)
            return seg["ci"] in hi["cl"] and (
                (seg.get("sd") and seg["li"] in hi["sd"]) or
                (not seg.get("sd") and seg["li"] in hi["ai"])
            )
        if "si" in seg and "li" in seg:       # source→lesson
            return seg["si"] in hi["src"] and (
                (seg.get("sd") and seg["li"] in hi["sd"]) or
                (not seg.get("sd") and seg["li"] in hi["ai"])
            )
        if "ci" in seg and "si" not in seg and "li" not in seg:  # center→cluster
            return seg["ci"] in hi["cl"]
        return False

    # ── Per-node opacities ────────────────────────────────────────────────────
    op_cl  = _opacities(len(cluster_list),  hi["cl"]  if hi else None)
    op_src = _opacities(len(source_list),   hi["src"] if hi else None)
    op_sd  = _opacities(len(sd_list),       hi["sd"]  if hi else None)
    op_ai  = _opacities(len(ai_list),       hi["ai"]  if hi else None)

    # ── Edge x/y arrays ───────────────────────────────────────────────────────
    dim_color_cc  = _rgba(NAVY,  DIM_A if is_selecting else 1.0)
    dim_color_cs  = _rgba(GOLD,  DIM_A if is_selecting else 1.0)
    dim_color_sl  = _rgba("#b8c8d8", DIM_A if is_selecting else 1.0)

    # Build single unified dim edge trace (all edges at dim alpha when selecting)
    all_x_dim, all_y_dim = _segs_to_xy(all_segs)

    # Build highlighted edge traces (per type, filtered)
    if is_selecting:
        hi_cc = [s for s in cc_segs if _seg_highlighted(s)]
        hi_cs = [s for s in cs_segs if _seg_highlighted(s)]
        hi_sl = [s for s in sl_segs if _seg_highlighted(s)]
        hi_cc_x, hi_cc_y = _segs_to_xy(hi_cc)
        hi_cs_x, hi_cs_y = _segs_to_xy(hi_cs)
        hi_sl_x, hi_sl_y = _segs_to_xy(hi_sl)
    else:
        hi_cc_x = hi_cc_y = hi_cs_x = hi_cs_y = hi_sl_x = hi_sl_y = []

    # ── Annotations ───────────────────────────────────────────────────────────
    annotations = []
    for ci, cl in enumerate(cluster_list):
        θ = cl["angle"]
        lr = R_CLUSTER + 0.52
        lx, ly = lr * math.cos(θ), lr * math.sin(θ)
        xa, ya = _label_anchor(θ)
        font_color = NAVY if (not is_selecting or ci in hi["cl"]) else _rgba(NAVY, DIM_A * 2)
        annotations.append(dict(
            x=lx, y=ly, text=cl["name"],
            showarrow=False,
            font=dict(family="Source Sans 3, sans-serif", size=9.5, color=font_color),
            xanchor=xa, yanchor=ya,
            bgcolor="rgba(245,243,238,0.75)",
        ))

    # ── Build figure ──────────────────────────────────────────────────────────
    fig = go.Figure()
    HL = dict(bgcolor="white", font=dict(family="Source Sans 3, sans-serif", size=12, color=NAVY), namelength=-1)

    # T0 — all edges (dim colour when selecting, normal when not)
    fig.add_trace(go.Scatter(
        x=all_x_dim, y=all_y_dim, mode="lines",
        line=dict(color=_rgba("#607080", DIM_A if is_selecting else 0.45), width=1.0),
        hoverinfo="none", showlegend=False,
    ))

    # T1 — highlighted edges on top (empty when not selecting)
    # We add separate sub-traces for cc / cs / sl colours, all sharing trace slot 1
    # (Plotly allows only one trace per slot, so we concatenate with different colours
    # by using a single trace with mixed segments — not ideal but workable since
    # colour varies only by edge type, not per-segment)
    hi_x_all = hi_cc_x + hi_cs_x + hi_sl_x
    hi_y_all = hi_cc_y + hi_cs_y + hi_sl_y
    fig.add_trace(go.Scatter(
        x=hi_x_all if is_selecting else [],
        y=hi_y_all if is_selecting else [],
        mode="lines",
        line=dict(color=NAVY, width=1.6),
        hoverinfo="none", showlegend=False,
    ))

    # T2 — Cluster nodes
    fig.add_trace(go.Scatter(
        x=[cl["x"] for cl in cluster_list],
        y=[cl["y"] for cl in cluster_list],
        mode="markers",
        marker=dict(
            color=GOLD, size=18,
            opacity=op_cl,
            line=dict(color="white", width=2.5),
        ),
        hovertext=[cl["hover"] for cl in cluster_list],
        hoverinfo="text",
        hoverlabel=dict(**HL, bordercolor=GOLD),
        showlegend=False,
    ))

    # T3 — Source nodes
    if show_sources and source_list:
        fig.add_trace(go.Scatter(
            x=[src["x"] for src in source_list],
            y=[src["y"] for src in source_list],
            mode="markers",
            marker=dict(
                color=SLATE, size=12,
                opacity=op_src,
                line=dict(color="white", width=1.5),
            ),
            hovertext=[src["hover"] for src in source_list],
            hoverinfo="text",
            hoverlabel=dict(**HL, bordercolor=SLATE),
            showlegend=False,
        ))
    else:
        fig.add_trace(go.Scatter(x=[], y=[], mode="markers", showlegend=False, hoverinfo="none"))

    # T4 — SD lesson nodes
    if sd_list:
        fig.add_trace(go.Scatter(
            x=[l["x"] for l in sd_list],
            y=[l["y"] for l in sd_list],
            mode="markers",
            marker=dict(
                color=GREEN, size=10,
                opacity=op_sd,
                line=dict(color="white", width=1.2),
            ),
            hovertext=[l["hover"] for l in sd_list],
            hoverinfo="text",
            hoverlabel=dict(**HL, bordercolor=GREEN),
            showlegend=False,
        ))
    else:
        fig.add_trace(go.Scatter(x=[], y=[], mode="markers", showlegend=False, hoverinfo="none"))

    # T5 — AI lesson nodes
    if ai_list:
        fig.add_trace(go.Scatter(
            x=[l["x"] for l in ai_list],
            y=[l["y"] for l in ai_list],
            mode="markers",
            marker=dict(
                color=RUST, size=10,
                opacity=op_ai,
                line=dict(color="white", width=1.2),
            ),
            hovertext=[l["hover"] for l in ai_list],
            hoverinfo="text",
            hoverlabel=dict(**HL, bordercolor=RUST),
            showlegend=False,
        ))
    else:
        fig.add_trace(go.Scatter(x=[], y=[], mode="markers", showlegend=False, hoverinfo="none"))

    # T6 — Centre node (drawn last, on top; not interactive)
    fig.add_trace(go.Scatter(
        x=[0], y=[0], mode="markers+text",
        marker=dict(color=NAVY, size=62, line=dict(color="white", width=3),
                    opacity=1.0),
        text=["UNIFIL<br>Lessons<br>Learned"],
        textposition="middle center",
        textfont=dict(family="Source Sans 3, sans-serif", size=8.5, color="white"),
        hoverinfo="skip", showlegend=False,
    ))

    # ── Layout ────────────────────────────────────────────────────────────────
    axis = dict(visible=False, zeroline=False, showgrid=False, showticklabels=False, range=[-8.2, 8.2])
    fig.update_layout(
        paper_bgcolor=CREAM,
        plot_bgcolor=CREAM,
        margin=dict(l=10, r=10, t=10, b=10),
        height=780,
        xaxis=dict(**axis),
        yaxis=dict(**axis, scaleanchor="x", scaleratio=1),
        dragmode="pan",
        clickmode="event+select",
        annotations=annotations,
        showlegend=False,
        hoverdistance=14,
    )

    # ── Render chart with selection support ───────────────────────────────────
    event = st.plotly_chart(
        fig,
        use_container_width=True,
        on_select="rerun",
        key="mm_chart",
        config={
            "scrollZoom": True,
            "displayModeBar": True,
            "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
            "displaylogo": False,
            "toImageButtonOptions": {"format": "png", "filename": "unifil_lessons_mindmap", "scale": 2},
        },
    )

    # ── Process click event ───────────────────────────────────────────────────
    pts = event.selection.points if (event and hasattr(event, "selection") and event.selection) else []
    if pts:
        p = pts[0]
        cn = p.get("curve_number", -1)
        pn = p.get("point_number", p.get("point_index", -1))
        new_sel = (cn, pn) if cn in INTERACTIVE else None
    else:
        new_sel = None

    if new_sel != mm_sel:
        st.session_state.mm_selected = new_sel
        st.rerun()

    # ── Legend bar ────────────────────────────────────────────────────────────
    def _dot(color):
        return (f'<span style="display:inline-block; width:11px; height:11px; '
                f'border-radius:50%; background:{color}; margin-right:5px; '
                f'vertical-align:middle;"></span>')

    legend_items = [
        (NAVY,  "Thematic cluster"),
        (GOLD,  "UNIFIL LL / centre"),
        (SLATE, "Source document"),
        (GREEN, "Source-derived lesson"),
        (RUST,  "Analytical inference"),
    ]
    legend_html = " &nbsp;·&nbsp; ".join(
        f'{_dot(c)}<span style="font-size:0.76rem; color:#5a6a7a;">{label}</span>'
        for c, label in legend_items
    )
    st.markdown(
        f'<div style="display:flex; flex-wrap:wrap; align-items:center; gap:0.3rem; '
        f'justify-content:center; margin-top:0.5rem; padding:0.5rem 1rem; '
        f'background:#eee9de; border-radius:4px; border:1px solid #ddd8cc;">'
        f'{legend_html}</div>',
        unsafe_allow_html=True,
    )

    # ── Footer stats ──────────────────────────────────────────────────────────
    n_shown = len(sd_list) + len(ai_list)
    n_src   = len(source_list)
    n_cl    = len(cluster_list)
    parts   = [f"<b>{n_shown}</b> lesson{'s' if n_shown != 1 else ''}",
               f"<b>{n_cl}</b> cluster{'s' if n_cl != 1 else ''}"]
    if show_sources:
        parts.append(f"<b>{n_src}</b> source document{'s' if n_src != 1 else ''}")
    if is_selecting:
        parts.append("<span style='color:#c8952a;'>node highlighted — click background to reset</span>")
    st.markdown(
        '<div style="font-size:0.8rem; color:#8a9ab0; text-align:center; margin-top:0.6rem;">'
        + " · ".join(parts) + "</div>",
        unsafe_allow_html=True,
    )
