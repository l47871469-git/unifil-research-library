import json
import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_utils import (
    load_sources, filter_sources, get_all_tags, get_all_actors,
    get_all_countries, THEMATIC_CLUSTERS, SOURCE_TYPES
)

DATA_PATH = Path(__file__).parent.parent / "data" / "sources.json"


def get_type_border_color(source_type):
    st_lower = source_type.lower()
    if any(k in st_lower for k in ("think tank", "policy brief")):
        return "#2563eb"
    if any(k in st_lower for k in ("academic", "journal", "book")):
        return "#16a34a"
    if any(k in st_lower for k in ("un/ngo", "ngo statement", "ngo")):
        return "#dc2626"
    if any(k in st_lower for k in ("opinion", "media")):
        return "#ca8a04"
    if any(k in st_lower for k in ("un official", "un document", "un publication")):
        return "#ea580c"
    return "#6b7c8d"


def save_source(updated):
    sources = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    for i, s in enumerate(sources):
        if s["id"] == updated["id"]:
            sources[i] = updated
            break
    DATA_PATH.write_text(json.dumps(sources, indent=2, ensure_ascii=False), encoding="utf-8")


def render_source_edit(s, all_tags):
    sid = s["id"]

    st.markdown('<div style="font-size:0.75rem; font-weight:600; color:#c8952a; letter-spacing:0.06em; margin-bottom:1rem;">EDIT MODE</div>', unsafe_allow_html=True)

    title = st.text_input("Title", value=s.get("title", ""), key=f"e_title_{sid}")
    author = st.text_input("Author", value=s.get("author", ""), key=f"e_author_{sid}")

    ec1, ec2 = st.columns([1, 2])
    with ec1:
        year = st.number_input("Year", value=int(s.get("year", 2000)), min_value=1900, max_value=2030, step=1, key=f"e_year_{sid}")
    with ec2:
        current_type = s.get("source_type", "")
        type_options = SOURCE_TYPES if current_type in SOURCE_TYPES else [current_type] + SOURCE_TYPES
        source_type = st.selectbox("Source type", type_options, index=type_options.index(current_type), key=f"e_stype_{sid}")

    abstract = st.text_area("Abstract", value=s.get("abstract", ""), height=130, key=f"e_abstract_{sid}")

    # Tags — multiselect from known list, current tags always included as options
    tag_options = sorted(set(all_tags) | set(s.get("tags", [])))
    tags = st.multiselect("Tags", options=tag_options, default=s.get("tags", []), key=f"e_tags_{sid}")

    # Thematic clusters
    cluster_defaults = [c for c in s.get("thematic_clusters", []) if c in THEMATIC_CLUSTERS]
    thematic_clusters = st.multiselect("Thematic clusters", options=THEMATIC_CLUSTERS, default=cluster_defaults, key=f"e_clusters_{sid}")

    # Actors — comma-separated free text
    actors_raw = st.text_area(
        "Actors (comma-separated)",
        value=", ".join(s.get("actors", [])),
        height=68,
        key=f"e_actors_{sid}"
    )

    bias_flag = st.text_area("Bias flag", value=s.get("bias_flag", ""), height=90, key=f"e_bias_{sid}")

    # Analytical notes — one per line
    notes_raw = st.text_area(
        "Analytical notes (one per line)",
        value="\n".join(s.get("analytical_notes", [])),
        height=100,
        key=f"e_notes_{sid}"
    )

    # Lessons learned
    st.markdown('<div style="font-size:0.85rem; font-weight:600; color:#1a3a5c; border-bottom:1px solid #ddd8cc; padding-bottom:0.25rem; margin:1rem 0 0.6rem 0;">Lessons Learned</div>', unsafe_allow_html=True)
    lessons_in = s.get("lessons_learned", [])
    edited_lessons = []
    for li, lesson in enumerate(lessons_in):
        lc1, lc2 = st.columns([3, 1])
        with lc1:
            ll_text = st.text_area(f"Lesson {li + 1}", value=lesson.get("text", ""), height=72, key=f"e_ll_text_{sid}_{li}", label_visibility="collapsed")
        with lc2:
            tag_opts = ["SOURCE-DERIVED", "ANALYTICAL INFERENCE"]
            current_tag = lesson.get("tag", "SOURCE-DERIVED")
            tag_idx = tag_opts.index(current_tag) if current_tag in tag_opts else 0
            ll_tag = st.selectbox(f"Tag {li + 1}", tag_opts, index=tag_idx, key=f"e_ll_tag_{sid}_{li}", label_visibility="collapsed")
        edited_lessons.append({"text": ll_text, "tag": ll_tag})

    st.markdown('<div style="margin-top:1rem;"></div>', unsafe_allow_html=True)
    btn_col1, btn_col2, _ = st.columns([1, 1, 2])
    with btn_col1:
        save_clicked = st.button("💾 Save changes", key=f"e_save_{sid}")
    with btn_col2:
        cancel_clicked = st.button("Cancel", key=f"e_cancel_{sid}")

    if save_clicked:
        updated = dict(s)
        updated["title"] = title
        updated["author"] = author
        updated["year"] = int(year)
        updated["source_type"] = source_type
        updated["abstract"] = abstract
        updated["tags"] = tags
        updated["thematic_clusters"] = thematic_clusters
        updated["actors"] = [a.strip() for a in actors_raw.split(",") if a.strip()]
        updated["bias_flag"] = bias_flag
        updated["analytical_notes"] = [ln.strip() for ln in notes_raw.splitlines() if ln.strip()]
        updated["lessons_learned"] = [l for l in edited_lessons if l["text"].strip()]
        save_source(updated)
        st.session_state.editing_source_id = None
        st.success("Saved.")
        st.rerun()

    if cancel_clicked:
        st.session_state.editing_source_id = None
        st.rerun()


def render_source_detail(s):
    st.markdown(f"""
    <div style="padding:0.5rem 0 1rem 0;">
        <div style="font-family:'Playfair Display',serif; font-size:1.5rem; font-weight:700; color:#1a3a5c; line-height:1.2; margin-bottom:0.4rem;">{s['title']}</div>
        <div style="font-size:0.9rem; color:#5a6a7a; margin-bottom:1rem;">{s['author']} · {s['year']} · {s['source_type']} · {s.get('publisher','')}</div>
    </div>
    """, unsafe_allow_html=True)

    clusters_html = "".join([f'<span class="tag tag-cluster">{c}</span>' for c in s.get('thematic_clusters', [])])
    st.markdown(f'<div style="margin-bottom:0.8rem;">{clusters_html}</div>', unsafe_allow_html=True)

    tags_html = "".join([f'<span class="tag">{t}</span>' for t in s.get('tags', [])])
    if tags_html:
        st.markdown(f'<div style="margin-bottom:1rem;">{tags_html}</div>', unsafe_allow_html=True)

    st.markdown('<div class="detail-section-title">Abstract</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="detail-body">{s.get("abstract","")}</div>', unsafe_allow_html=True)

    st.markdown('<div class="detail-section-title">Key Arguments</div>', unsafe_allow_html=True)
    for arg in s.get("key_arguments", []):
        st.markdown(f'<div class="detail-body" style="padding-left:1rem; border-left:2px solid #c8d4e0; margin-bottom:0.5rem;">— {arg}</div>', unsafe_allow_html=True)

    st.markdown('<div class="detail-section-title">Relevance to UNIFIL LL Exercise</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="detail-body">{s.get("unifil_relevance","")}</div>', unsafe_allow_html=True)

    if s.get("bias_flag"):
        st.markdown('<div class="detail-section-title">Bias Assessment</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="bias-flag">{s["bias_flag"]}</div>', unsafe_allow_html=True)

    notes = s.get("analytical_notes", [])
    if notes:
        st.markdown('<div class="detail-section-title">Analytical Notes</div>', unsafe_allow_html=True)
        for note in notes:
            st.markdown(f'<div class="detail-body" style="padding-left:1rem; border-left:2px solid #e0dbd2; margin-bottom:0.5rem;">{note}</div>', unsafe_allow_html=True)

    lessons = s.get("lessons_learned", [])
    if lessons:
        st.markdown('<div class="detail-section-title">Lessons Learned Candidates</div>', unsafe_allow_html=True)
        for l in lessons:
            tag_class = "tag-lesson-sd" if l.get("tag") == "SOURCE-DERIVED" else "tag-lesson-ai"
            tag_label = l.get("tag", "")
            st.markdown(f"""
            <div style="margin-bottom:0.7rem; padding:0.7rem; background:#fafaf8; border:1px solid #e0dbd2; border-radius:3px;">
                <span class="tag {tag_class}">{tag_label}</span>
                <div class="detail-body" style="margin-top:0.4rem;">{l['text']}</div>
            </div>
            """, unsafe_allow_html=True)

    timeline = s.get("timeline_events", [])
    if timeline:
        st.markdown('<div class="detail-section-title">Timeline Events</div>', unsafe_allow_html=True)
        for e in timeline:
            st.markdown(f"""
            <div style="display:flex; gap:1rem; margin-bottom:0.4rem; font-size:0.88rem;">
                <span style="font-weight:600; color:#1a3a5c; min-width:60px;">{e.get('date','')}</span>
                <span style="color:#3a3a3a;">{e.get('event','')}</span>
            </div>
            """, unsafe_allow_html=True)

    actors = s.get("actors", [])
    if actors:
        st.markdown('<div class="detail-section-title">Key Actors</div>', unsafe_allow_html=True)
        actors_html = "".join([f'<span class="tag tag-actor">{a}</span>' for a in actors])
        st.markdown(f'<div>{actors_html}</div>', unsafe_allow_html=True)

    coverage = s.get("timeline_coverage", [])
    if isinstance(coverage, dict):
        cov_start, cov_end = coverage.get("start", ""), coverage.get("end", "")
        if cov_start or cov_end:
            st.markdown(f'<div style="margin-top:1rem; font-size:0.8rem; color:#8a9ab0;">Period covered: {cov_start}–{cov_end}</div>', unsafe_allow_html=True)
    elif isinstance(coverage, list) and len(coverage) == 2:
        st.markdown(f'<div style="margin-top:1rem; font-size:0.8rem; color:#8a9ab0;">Period covered: {coverage[0]}–{coverage[1]}</div>', unsafe_allow_html=True)


def show():
    sources = load_sources()
    all_tags = get_all_tags(sources)
    all_actors = get_all_actors(sources)
    all_countries = get_all_countries(sources)
    all_years = [s.get("year", 2000) for s in sources if s.get("year")]

    if "selected_source_id" not in st.session_state:
        st.session_state.selected_source_id = None
    if "editing_source_id" not in st.session_state:
        st.session_state.editing_source_id = None

    st.markdown("""
    <div class="library-header">
        <div>
            <p class="library-subtitle">UN DPO · Policy & Best Practices Service</p>
            <h1 class="library-title">UNIFIL Research Library</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)

    total = len(sources)
    n_clusters = len(set(c for s in sources for c in s.get("thematic_clusters", [])))
    n_lessons = sum(len(s.get("lessons_learned", [])) for s in sources)
    n_actors = len(all_actors)

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card"><div class="metric-number">{total}</div><div class="metric-label">Sources</div></div>
        <div class="metric-card"><div class="metric-number">{n_clusters}</div><div class="metric-label">Themes covered</div></div>
        <div class="metric-card"><div class="metric-number">{n_lessons}</div><div class="metric-label">LL candidates</div></div>
        <div class="metric-card"><div class="metric-number">{n_actors}</div><div class="metric-label">Actors indexed</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Horizontal filter bar ─────────────────────────────────────────────────
    year_min = min(all_years) if all_years else 1978
    year_max = max(all_years) if all_years else 2026

    with st.container():
        st.markdown('<div style="background:#f4f1eb; border:1px solid #ddd8cc; border-radius:4px; padding:0.75rem 1rem 0.5rem 1rem; margin-bottom:0.5rem;">', unsafe_allow_html=True)
        fc = st.columns([2.2, 1.4, 1.2, 1.2, 1.4, 2.0, 0.65])
        with fc[0]:
            st.markdown('<div style="font-size:0.72rem; color:#6b7c8d; margin-bottom:0.2rem; font-weight:500;">SEARCH</div>', unsafe_allow_html=True)
            search = st.text_input("search", placeholder="Titles, authors, tags…", key="search", label_visibility="collapsed")
        with fc[1]:
            st.markdown('<div style="font-size:0.72rem; color:#6b7c8d; margin-bottom:0.2rem; font-weight:500;">CLUSTER</div>', unsafe_allow_html=True)
            selected_clusters = st.multiselect("cluster", THEMATIC_CLUSTERS, key="clusters", placeholder="All…", label_visibility="collapsed")
        with fc[2]:
            st.markdown('<div style="font-size:0.72rem; color:#6b7c8d; margin-bottom:0.2rem; font-weight:500;">TYPE</div>', unsafe_allow_html=True)
            selected_types = st.multiselect("type", SOURCE_TYPES, key="types", placeholder="All…", label_visibility="collapsed")
        with fc[3]:
            st.markdown('<div style="font-size:0.72rem; color:#6b7c8d; margin-bottom:0.2rem; font-weight:500;">COUNTRY</div>', unsafe_allow_html=True)
            selected_countries = st.multiselect("country", all_countries, key="countries", placeholder="All…", label_visibility="collapsed")
        with fc[4]:
            st.markdown('<div style="font-size:0.72rem; color:#6b7c8d; margin-bottom:0.2rem; font-weight:500;">TAGS</div>', unsafe_allow_html=True)
            selected_tags = st.multiselect("tags", all_tags, key="tags", placeholder="All…", label_visibility="collapsed")
        with fc[5]:
            st.markdown('<div style="font-size:0.72rem; color:#6b7c8d; margin-bottom:0.2rem; font-weight:500;">YEAR RANGE</div>', unsafe_allow_html=True)
            year_range = st.slider("year", min_value=1978, max_value=2026, value=(year_min, year_max), key="years", label_visibility="collapsed")
        with fc[6]:
            st.markdown('<div style="font-size:0.72rem; color:transparent; margin-bottom:0.2rem;">.</div>', unsafe_allow_html=True)
            if st.button("✕ Clear", key="clear_filters"):
                for k in ["search", "clusters", "types", "countries", "tags"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    filtered = filter_sources(
        sources,
        clusters=selected_clusters if selected_clusters else None,
        source_types=selected_types if selected_types else None,
        countries=selected_countries if selected_countries else None,
        search_query=search if search else None,
        year_range=year_range,
        tags=selected_tags if selected_tags else None
    )

    # Colour legend
    st.markdown("""
    <div style="display:flex; flex-wrap:wrap; gap:0.3rem 1.1rem; margin-bottom:0.7rem; font-size:0.73rem; color:#5a6a7a;">
        <span><span style="display:inline-block; width:9px; height:9px; border-radius:2px; background:#2563eb; margin-right:3px; vertical-align:middle;"></span>Think Tank / Policy Brief</span>
        <span><span style="display:inline-block; width:9px; height:9px; border-radius:2px; background:#16a34a; margin-right:3px; vertical-align:middle;"></span>Academic / Book</span>
        <span><span style="display:inline-block; width:9px; height:9px; border-radius:2px; background:#dc2626; margin-right:3px; vertical-align:middle;"></span>UN/NGO Statement</span>
        <span><span style="display:inline-block; width:9px; height:9px; border-radius:2px; background:#ca8a04; margin-right:3px; vertical-align:middle;"></span>Opinion / Media</span>
        <span><span style="display:inline-block; width:9px; height:9px; border-radius:2px; background:#ea580c; margin-right:3px; vertical-align:middle;"></span>UN Official Publication</span>
        <span><span style="display:inline-block; width:9px; height:9px; border-radius:2px; background:#6b7c8d; margin-right:3px; vertical-align:middle;"></span>Other</span>
    </div>
    """, unsafe_allow_html=True)

    col_results, col_detail = st.columns([3.2, 2.4])

    with col_results:
        st.markdown(f'<div style="font-size:0.82rem; color:#6b7c8d; margin-bottom:0.6rem; letter-spacing:0.04em; text-transform:uppercase;">{len(filtered)} source{"s" if len(filtered)!=1 else ""} found</div>', unsafe_allow_html=True)

        st.markdown('<div class="source-grid-container">', unsafe_allow_html=True)

        for i in range(0, len(filtered), 2):
            left_s = filtered[i]
            right_s = filtered[i + 1] if i + 1 < len(filtered) else None

            grid_cols = st.columns(2, gap="small")

            for col_idx, s in enumerate([left_s, right_s]):
                if s is None:
                    continue
                with grid_cols[col_idx]:
                    is_selected = st.session_state.selected_source_id == s["id"]
                    border_color = "#c8952a" if is_selected else get_type_border_color(s.get("source_type", ""))
                    bg_color = "#fdf7ee" if is_selected else "white"

                    abstract_preview = s.get("abstract", "")[:110] + "…" if len(s.get("abstract", "")) > 110 else s.get("abstract", "")
                    clusters_html = "".join([
                        f'<span style="display:inline-block; background:#1a3a5c; color:#e8e0d0; border-radius:2px; font-size:0.68rem; padding:0.1rem 0.4rem; margin:0.1rem;">{c}</span>'
                        for c in s.get("thematic_clusters", [])[:2]
                    ])

                    st.markdown(f"""
                    <div class="source-card" style="border-left-color:{border_color}; background:{bg_color}; height:100%; min-height:160px;">
                        <div class="source-card-title" style="font-size:0.92rem;">{s['title']}</div>
                        <div class="source-card-meta">{s['author']} · {s['year']}</div>
                        <div class="source-card-meta" style="margin-bottom:0.4rem;">{s.get('source_type','')}</div>
                        <div class="source-card-abstract">{abstract_preview}</div>
                        <div style="margin-top:0.5rem;">{clusters_html}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("Open →", key=f"btn_{s['id']}"):
                        st.session_state.selected_source_id = s["id"]
                        st.session_state.editing_source_id = None
                        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with col_detail:
        st.markdown('<div class="detail-sticky-wrapper">', unsafe_allow_html=True)

        if st.session_state.selected_source_id:
            selected = next((s for s in sources if s["id"] == st.session_state.selected_source_id), None)
            if selected:
                is_editing = st.session_state.editing_source_id == selected["id"]

                # Header row: Close | Edit (or just Close in edit mode)
                hc1, hc2 = st.columns([1, 1])
                with hc1:
                    if st.button("✕ Close", key="close_detail"):
                        st.session_state.selected_source_id = None
                        st.session_state.editing_source_id = None
                        st.rerun()
                with hc2:
                    if not is_editing:
                        if st.button("✎ Edit", key="edit_detail"):
                            st.session_state.editing_source_id = selected["id"]
                            st.rerun()

                st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

                if is_editing:
                    render_source_edit(selected, all_tags)
                else:
                    render_source_detail(selected)
        else:
            st.markdown("""
            <div style="padding: 4rem 2rem; text-align:center; color:#8a9ab0;">
                <div style="font-size:2.5rem; margin-bottom:1rem; opacity:0.4;">📄</div>
                <div style="font-family:'Playfair Display',serif; font-size:1.1rem; color:#5a6a7a; margin-bottom:0.5rem;">Select a source to view its full record</div>
                <div style="font-size:0.85rem;">Use the filters on the left to narrow your search,<br>then click <em>Open →</em> on any source.</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
