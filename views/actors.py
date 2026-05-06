import streamlit as st
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_utils import load_sources

DATA_PATH = Path(__file__).parent.parent / "data" / "actors_combined.json"

CATEGORY_META = {
    "UN":            {"label": "UN",            "color": "#1a3a5c"},
    "Armed groups":  {"label": "Armed groups",  "color": "#c43838"},
    "Israel":        {"label": "Israel",        "color": "#2196f3"},
    "Member states": {"label": "Member states", "color": "#3a8a4a"},
    "Lebanon":       {"label": "Lebanon",       "color": "#d97a1f"},
    "Other":         {"label": "Other",         "color": "#78909c"},
}

_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {
  --bg:             #f5f4f0;
  --surface:        #faf9f6;
  --surface2:       #f0ede8;
  --border:         rgba(0,0,0,0.07);
  --border2:        rgba(0,0,0,0.12);
  --text-primary:   #1a1916;
  --text-secondary: #4a4740;
  --text-muted:     #8a8680;
  --accent:         #1a3a5c;
  --font:           'IBM Plex Sans', sans-serif;
  --serif:          'Playfair Display', Georgia, serif;
  --mono:           'IBM Plex Mono', monospace;
}

/* Only target the main content area background, NOT the sidebar */
section.main { background: var(--bg) !important; }
.stApp { font-family: var(--font) !important; }

/* ── Header ──────────────────────────────────────────────────── */
.ap-eyebrow {
  font-family: var(--mono); font-size: 10px; font-weight: 500;
  letter-spacing: 0.14em; text-transform: uppercase;
  color: var(--text-muted); margin-bottom: 4px;
}
.ap-h1 {
  font-family: var(--serif); font-size: 32px; font-weight: 700;
  color: var(--text-primary); letter-spacing: -0.02em; margin: 4px 0 12px 0;
}
.ap-desc {
  font-size: 13px; color: var(--text-secondary); line-height: 1.5;
  margin: 4px 0 12px 0; font-family: var(--font); max-width: 680px;
}

/* ── Legend ──────────────────────────────────────────────────── */
.ap-legend {
  display: flex; flex-wrap: wrap; gap: 18px;
  padding-bottom: 14px; border-bottom: 1px solid var(--border2);
  margin-bottom: 14px;
}
.ap-legend-item {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 12px; color: var(--text-secondary); font-family: var(--font);
}

/* ── Inputs ──────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stMultiSelect [data-baseweb="select"] > div:first-child {
  background: var(--surface2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 5px !important;
  font-family: var(--font) !important;
  font-size: 13px !important;
}
.stTextInput > div > div > input:focus {
  border-color: var(--accent) !important; box-shadow: none !important;
}

/* ── Ghost action buttons (primary) ─────────────────────────── */
button[kind="primary"] {
  background: transparent !important;
  border: 1px solid var(--border2) !important;
  color: var(--text-secondary) !important;
  font-family: var(--font) !important;
  font-size: 0.78rem !important;
  font-weight: 500 !important;
  padding: 0.28rem 0.75rem !important;
  border-radius: 4px !important;
  line-height: 1.4 !important;
  min-height: unset !important;
  box-shadow: none !important;
}
button[kind="primary"]:hover {
  border-color: var(--accent) !important;
  color: var(--accent) !important;
  background: rgba(26,58,92,0.04) !important;
}
button[kind="primary"]:focus { box-shadow: none !important; }

/* ── A-Z sidebar (HTML links — full control, no Streamlit buttons) ── */
.ap-az-wrap {
  display: flex; flex-direction: column; align-items: center;
  padding-top: 8px;
}
.ap-az-all {
  display: inline-block;
  font-family: var(--mono); font-size: 11px; font-weight: 700;
  letter-spacing: 0.1em; text-transform: uppercase;
  background: var(--accent); color: white;
  padding: 3px 10px; border-radius: 3px; margin-bottom: 14px;
  text-decoration: none; cursor: pointer;
}
.ap-az-all-inactive {
  background: transparent; color: var(--text-secondary);
  border: 1px solid var(--border2);
}
.ap-az-letter {
  display: block;
  font-family: var(--mono); font-size: 12px; font-weight: 400;
  color: var(--text-secondary);
  padding: 1px 0; line-height: 1.55;
  text-align: center; text-decoration: none;
  cursor: pointer; transition: color 0.1s;
}
.ap-az-letter:hover { color: var(--accent); font-weight: 600; }
.ap-az-letter.active {
  color: var(--accent); font-weight: 700;
}
.ap-az-letter.dim {
  color: var(--text-muted); opacity: 0.3;
  cursor: default; pointer-events: none;
}

/* ── Letter section header ───────────────────────────────────── */
.ap-lhdr {
  display: flex; align-items: center; gap: 10px; padding: 18px 0 8px 0;
}
.ap-lhdr-lbl {
  font-family: var(--serif); font-size: 22px; font-weight: 700;
  color: var(--accent); letter-spacing: -0.02em; line-height: 1; min-width: 22px;
}
.ap-lhdr-rule { flex: 1; height: 1px; background: var(--border2); }
.ap-lhdr-cnt {
  font-family: var(--mono); font-size: 10px; color: var(--text-muted);
  letter-spacing: 0.06em;
}

/* ── Actor row ───────────────────────────────────────────────── */
.ap-row {
  display: flex; align-items: stretch;
  border-bottom: 1px solid var(--border);
  background: transparent;
}
.ap-row-bar { width: 3px; flex-shrink: 0; margin: 8px 0; }
.ap-row-inner {
  flex: 1; display: flex; align-items: center;
  gap: 12px; padding: 13px 16px 13px 12px;
}
.ap-row-name {
  flex: 1; font-size: 14px; font-weight: 600; font-family: var(--font);
  color: var(--text-primary); letter-spacing: 0.01em;
}
.ap-row-cat {
  display: flex; align-items: center; gap: 6px;
  font-family: var(--mono); font-size: 11px; color: var(--text-muted);
  letter-spacing: 0.04em; white-space: nowrap;
}
.ap-row-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
.ap-row-srcs {
  font-family: var(--mono); font-size: 11px; color: var(--text-muted);
  min-width: 56px; text-align: right; white-space: nowrap;
}
.ap-row-chev { color: var(--text-muted); flex-shrink: 0; font-size: 10px; margin-left: 4px; }

/* ── Expanded body ───────────────────────────────────────────── */
.ap-expand {
  margin: 0 0 8px 13px; padding: 14px 18px;
  background: var(--surface2); border-radius: 4px;
  border: 1px solid var(--border2);
}
.ap-expand-meta { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.ap-badge {
  display: inline-flex; align-items: center; gap: 5px;
  border-radius: 3px; padding: 2px 8px;
  font-family: var(--mono); font-size: 10px; font-weight: 600;
  letter-spacing: 0.08em; text-transform: uppercase;
}
.ap-badge-dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }
.ap-badge-srcs { font-family: var(--mono); font-size: 11px; color: var(--text-muted); }
.ap-expand-desc {
  font-family: var(--font); font-size: 13px; color: var(--text-secondary);
  line-height: 1.65; margin: 0;
}

/* ── Sources panel ───────────────────────────────────────────── */
.ap-src-panel {
  background: white; border: 1px solid var(--border2);
  border-radius: 4px; padding: 12px 16px; margin-top: 8px;
  margin-left: 13px;
}
.ap-src-hdr {
  font-family: var(--mono); font-size: 9px; font-weight: 700;
  letter-spacing: 0.1em; text-transform: uppercase;
  color: var(--text-muted); margin-bottom: 8px;
}
.ap-src-row {
  display: flex; gap: 12px; align-items: baseline;
  padding: 6px 0; border-bottom: 1px solid var(--border); font-family: var(--font);
}
.ap-src-row:last-child { border-bottom: none; }
.ap-src-year { font-family: var(--mono); font-size: 11px; color: var(--text-muted); flex-shrink: 0; min-width: 36px; }
.ap-src-name { font-size: 12px; color: var(--text-primary); flex: 1; }
.ap-src-type { font-family: var(--mono); font-size: 10px; color: var(--text-muted); flex-shrink: 0; }

/* ── Misc ────────────────────────────────────────────────────── */
.ap-gap { margin-bottom: 0.5rem; }
.ap-noactors {
  font-family: var(--font); font-size: 14px; color: var(--text-muted);
  padding: 60px 0; text-align: center;
}
</style>"""


def _load():
    if not DATA_PATH.exists():
        return []
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def _save(actors):
    DATA_PATH.write_text(json.dumps(actors, indent=2, ensure_ascii=False), encoding="utf-8")


def _badge_html(category):
    meta = CATEGORY_META.get(category, {"label": category, "color": "#78909c"})
    c, lbl = meta["color"], meta["label"]
    return (
        f'<span class="ap-badge" style="background:{c}22;border:1px solid {c}55;color:{c};">'
        f'<span class="ap-badge-dot" style="background:{c};"></span>{lbl}</span>'
    )


def show():
    st.markdown(_CSS, unsafe_allow_html=True)

    # Initialise session state
    defaults = {
        "actor_letter":   "All",
        "actor_expanded": None,
        "actor_src_open": None,
        "actor_editing":  None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Read query param to set letter
    qp = st.query_params
    if "letter" in qp:
        st.session_state.actor_letter = qp["letter"]
        st.query_params.clear()
        st.rerun()

    # ── Header ─────────────────────────────────────────────────────
    st.markdown("""
    <div class="ap-eyebrow">Key Actors &amp; Entities</div>
    <div class="ap-h1">Actors</div>
    <div class="ap-desc">Browse all actors and entities in the UNIFIL operating environment. Click an actor to view the profile and linked sources.</div>
    """, unsafe_allow_html=True)

    actors  = _load()
    sources = load_sources()

    src_by_actor: dict = {}
    for s in sources:
        for a in s.get("actors", []):
            src_by_actor.setdefault(a.lower(), []).append(s)

    ltr = st.session_state.actor_letter

    # ── Legend ────────────────────────────────────────────────────
    items_html = "".join(
        f'<span class="ap-legend-item">'
        f'<span style="width:9px;height:9px;border-radius:50%;background:{m["color"]};'
        f'display:inline-block;flex-shrink:0;"></span>{m["label"]}</span>'
        for m in CATEGORY_META.values()
    )
    st.markdown(f'<div class="ap-legend">{items_html}</div>', unsafe_allow_html=True)

    # ── Search + category filter ───────────────────────────────────
    fc1, fc2 = st.columns([3, 1])
    with fc1:
        search = st.text_input("Search", placeholder="Search by name or description…",
                               label_visibility="collapsed")
    with fc2:
        sel_cats = st.multiselect("Category", list(CATEGORY_META.keys()),
                                  label_visibility="collapsed", placeholder="Filter by category…")

    # ── Filter ────────────────────────────────────────────────────
    filtered = list(actors)
    if search:
        q = search.lower()
        filtered = [a for a in filtered
                    if q in a["name"].lower() or q in a.get("description", "").lower()]
    if sel_cats:
        filtered = [a for a in filtered if a["category"] in sel_cats]
    if ltr != "All":
        filtered = [a for a in filtered if a["name"].upper().startswith(ltr)]

    # ── Layout: A-Z column on left (narrow), actors on right ──────
    az_col, main_col = st.columns([1, 14])

    # ── A-Z sidebar (HTML <a> links with query params, no buttons) ─
    with az_col:
        active_letters = {a["name"][0].upper() for a in actors if a["name"]}

        # Build A-Z column entirely as HTML
        all_class = "ap-az-all" if ltr == "All" else "ap-az-all ap-az-all-inactive"
        az_html = f'<div class="ap-az-wrap"><a href="?letter=All" class="{all_class}" target="_self">All</a>'

        for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if ch in active_letters:
                cls = "ap-az-letter active" if ch == ltr else "ap-az-letter"
                az_html += f'<a href="?letter={ch}" class="{cls}" target="_self">{ch}</a>'
            else:
                az_html += f'<span class="ap-az-letter dim">{ch}</span>'

        az_html += '</div>'
        st.markdown(az_html, unsafe_allow_html=True)

    # ── Actor list ────────────────────────────────────────────────
    with main_col:
        if not filtered:
            st.markdown('<div class="ap-noactors">No actors match the current filters.</div>',
                        unsafe_allow_html=True)
        else:
            # Group by first letter
            groups: dict = {}
            for actor in filtered:
                letter = actor["name"][0].upper() if actor["name"] else "#"
                groups.setdefault(letter, []).append(actor)
            groups = dict(sorted(groups.items()))

            for letter, letter_actors in groups.items():
                st.markdown(f"""
                <div class="ap-lhdr">
                  <span class="ap-lhdr-lbl">{letter}</span>
                  <div class="ap-lhdr-rule"></div>
                  <span class="ap-lhdr-cnt">{len(letter_actors)}</span>
                </div>
                """, unsafe_allow_html=True)

                for actor in letter_actors:
                    name        = actor["name"]
                    category    = actor["category"]
                    description = actor.get("description", "")
                    meta        = CATEGORY_META.get(category, {"label": category, "color": "#78909c"})
                    color       = meta["color"]
                    label       = meta["label"]
                    a_sources   = src_by_actor.get(name.lower(), [])
                    n_src       = len(a_sources)

                    is_expanded = st.session_state.actor_expanded == name
                    src_open    = st.session_state.actor_src_open == name
                    is_editing  = st.session_state.actor_editing  == name

                    chev = "▲" if is_expanded else "▼"

                    # Visual row (HTML) — preserves coloured dots and styling
                    st.markdown(f"""
                    <div class="ap-row">
                      <div class="ap-row-bar" style="background:{color};"></div>
                      <div class="ap-row-inner">
                        <span class="ap-row-name">{name}</span>
                        <span class="ap-row-cat">
                          <span class="ap-row-dot" style="background:{color};"></span>
                          {label}
                        </span>
                        <span class="ap-row-srcs">{n_src} src{"s" if n_src != 1 else ""}</span>
                        <span class="ap-row-chev">{chev}</span>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Small subtle expand toggle below the row
                    if st.button(
                        ("▲ Hide" if is_expanded else "▼ Open"),
                        key=f"toggle_{name}",
                        type="primary",
                    ):
                        if is_expanded:
                            st.session_state.actor_expanded = None
                            st.session_state.actor_src_open = None
                            st.session_state.actor_editing  = None
                        else:
                            st.session_state.actor_expanded = name
                            st.session_state.actor_src_open = None
                            st.session_state.actor_editing  = None
                        st.rerun()

                    if is_expanded:
                        desc_html = (
                            f'<p class="ap-expand-desc">{description}</p>'
                            if description else
                            '<p class="ap-expand-desc" style="color:var(--text-muted);">No description available.</p>'
                        )
                        srcs_label = f'{n_src} source{"s" if n_src != 1 else ""} in corpus'
                        st.markdown(f"""
                        <div class="ap-expand">
                          <div class="ap-expand-meta">
                            {_badge_html(category)}
                            <span class="ap-badge-srcs">{srcs_label}</span>
                          </div>
                          {desc_html}
                        </div>
                        """, unsafe_allow_html=True)

                        if not src_open and not is_editing:
                            arr_c, _ = st.columns([1, 8])
                            with arr_c:
                                if st.button("→ Sources", key=f"src_open_{name}", type="primary"):
                                    st.session_state.actor_src_open = name
                                    st.rerun()

                        if src_open or is_editing:
                            if not a_sources:
                                rows_html = '<p style="font-size:0.82rem;color:var(--text-muted);margin:0;">No sources reference this actor.</p>'
                            else:
                                rows_html = "".join(
                                    f'<div class="ap-src-row">'
                                    f'<span class="ap-src-year">{s.get("year","")}</span>'
                                    f'<span class="ap-src-name">{s.get("title","")}</span>'
                                    f'<span class="ap-src-type">{s.get("source_type","")}</span>'
                                    f'</div>'
                                    for s in a_sources
                                )

                            st.markdown(f"""
                            <div class="ap-src-panel">
                              <div class="ap-src-hdr">Sources</div>
                              {rows_html}
                            </div>
                            """, unsafe_allow_html=True)

                            if not is_editing:
                                ea_c, cl_c, _ = st.columns([1, 1, 7])
                                with ea_c:
                                    if st.button("Edit actor", key=f"edit_open_{name}", type="primary"):
                                        st.session_state.actor_editing = name
                                        st.rerun()
                                with cl_c:
                                    if st.button("✕ Close", key=f"src_close_{name}", type="primary"):
                                        st.session_state.actor_src_open = None
                                        st.rerun()

                            if is_editing:
                                st.markdown('<div style="margin-top:0.6rem;"></div>', unsafe_allow_html=True)
                                new_name = st.text_input("Name",        value=name,        key=f"ed_name_{name}")
                                new_cat  = st.selectbox(
                                    "Category",
                                    options=list(CATEGORY_META.keys()),
                                    index=list(CATEGORY_META.keys()).index(category)
                                          if category in CATEGORY_META else 5,
                                    key=f"ed_cat_{name}",
                                )
                                new_desc = st.text_area("Description", value=description,
                                                        height=100, key=f"ed_desc_{name}")

                                sv_c, cn_c, _ = st.columns([1, 1, 7])
                                with sv_c:
                                    if st.button("Save", key=f"ed_save_{name}", type="primary"):
                                        all_a = _load()
                                        for a in all_a:
                                            if a["name"] == name:
                                                a["name"]        = new_name
                                                a["category"]    = new_cat
                                                a["description"] = new_desc
                                                break
                                        _save(all_a)
                                        st.session_state.actor_expanded = new_name
                                        st.session_state.actor_src_open = new_name
                                        st.session_state.actor_editing  = None
                                        st.rerun()
                                with cn_c:
                                    if st.button("Cancel", key=f"ed_cancel_{name}", type="primary"):
                                        st.session_state.actor_editing = None
                                        st.rerun()

                    st.markdown('<div class="ap-gap"></div>', unsafe_allow_html=True)
