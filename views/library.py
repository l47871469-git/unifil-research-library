import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_utils import (
    load_sources, filter_sources, get_all_tags, get_all_actors,
    get_all_countries, THEMATIC_CLUSTERS, SOURCE_TYPES
)

def render_source_detail(s):
    st.markdown(f"""
    <div style="padding:0.5rem 0 1rem 0;">
        <div style="font-family:'Playfair Display',serif; font-size:1.5rem; font-weight:700; color:#1a3a5c; line-height:1.2; margin-bottom:0.4rem;">{s['title']}</div>
        <div style="font-size:0.9rem; color:#5a6a7a; margin-bottom:1rem;">{s['author']} · {s['year']} · {s['source_type']} · {s.get('publisher','')}</div>
    </div>
    """, unsafe_allow_html=True)

    # Thematic clusters
    clusters_html = "".join([f'<span class="tag tag-cluster">{c}</span>' for c in s.get('thematic_clusters', [])])
    st.markdown(f'<div style="margin-bottom:0.8rem;">{clusters_html}</div>', unsafe_allow_html=True)

    # Tags
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
    if coverage and len(coverage) == 2:
        st.markdown(f'<div style="margin-top:1rem; font-size:0.8rem; color:#8a9ab0;">Period covered: {coverage[0]}–{coverage[1]}</div>', unsafe_allow_html=True)


def show():
    sources = load_sources()
    all_tags = get_all_tags(sources)
    all_actors = get_all_actors(sources)
    all_countries = get_all_countries(sources)
    all_years = [s.get("year", 2000) for s in sources if s.get("year")]

    st.markdown("""
    <div class="library-header">
        <div>
            <p class="library-subtitle">UN DPO · Policy & Best Practices Service</p>
            <h1 class="library-title">UNIFIL Research Library</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Metrics row
    total = len(sources)
    n_clusters = len(set(c for s in sources for c in s.get("thematic_clusters", [])))
    n_lessons = sum(len(s.get("lessons_learned", [])) for s in sources)
    n_actors = len(all_actors)

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-number">{total}</div>
            <div class="metric-label">Sources</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{n_clusters}</div>
            <div class="metric-label">Themes covered</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{n_lessons}</div>
            <div class="metric-label">LL candidates</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{n_actors}</div>
            <div class="metric-label">Actors indexed</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Layout: filters left, results right ──────────────────────────────────
    col_filter, col_results, col_detail = st.columns([1.1, 1.6, 2.2])

    with col_filter:
        st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'Playfair Display\',serif; font-size:1rem; font-weight:600; color:#1a3a5c; margin-bottom:0.8rem;">Filter Sources</div>', unsafe_allow_html=True)

        search = st.text_input("🔍 Search titles, authors, tags", placeholder="e.g. Hezbollah, force protection…", key="search")

        selected_clusters = st.multiselect(
            "Thematic cluster",
            THEMATIC_CLUSTERS,
            key="clusters"
        )
        selected_types = st.multiselect(
            "Source type",
            SOURCE_TYPES,
            key="types"
        )
        selected_countries = st.multiselect(
            "Country of origin",
            all_countries,
            key="countries"
        )
        selected_tags = st.multiselect(
            "Tags",
            all_tags,
            key="tags"
        )

        year_min = min(all_years) if all_years else 1978
        year_max = max(all_years) if all_years else 2026
        year_range = st.slider(
            "Publication year",
            min_value=1978,
            max_value=2026,
            value=(year_min, year_max),
            key="years"
        )

        if st.button("Clear filters"):
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

    with col_results:
        st.markdown(f'<div style="font-size:0.82rem; color:#6b7c8d; margin-bottom:0.8rem; letter-spacing:0.04em; text-transform:uppercase;">{len(filtered)} source{"s" if len(filtered)!=1 else ""} found</div>', unsafe_allow_html=True)

        if "selected_source_id" not in st.session_state:
            st.session_state.selected_source_id = None

        st.markdown('<div class="source-list-container">', unsafe_allow_html=True)
        for s in filtered:
            is_selected = st.session_state.selected_source_id == s["id"]
            border_color = "#c8952a" if is_selected else "#1a3a5c"
            bg_color = "#fdf7ee" if is_selected else "white"

            clusters_preview = " · ".join(s.get("thematic_clusters", [])[:2])
            abstract_preview = s.get("abstract", "")[:130] + "…" if len(s.get("abstract","")) > 130 else s.get("abstract","")

            st.markdown(f"""
            <div class="source-card" style="border-left-color:{border_color}; background:{bg_color};">
                <div class="source-card-title">{s['title']}</div>
                <div class="source-card-meta">{s['author']} · {s['year']} · {s.get('source_type','')} · {s.get('country_of_origin','')}</div>
                <div class="source-card-abstract">{abstract_preview}</div>
                <div style="margin-top:0.5rem; font-size:0.75rem; color:#8a9ab0;">{clusters_preview}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Open →", key=f"btn_{s['id']}"):
                st.session_state.selected_source_id = s["id"]
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with col_detail:
        if st.session_state.selected_source_id:
            selected = next((s for s in sources if s["id"] == st.session_state.selected_source_id), None)
            if selected:
                if st.button("✕ Close", key="close_detail"):
                    st.session_state.selected_source_id = None
                    st.rerun()
                st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
                render_source_detail(selected)
        else:
            st.markdown("""
            <div style="padding: 4rem 2rem; text-align:center; color:#8a9ab0;">
                <div style="font-size:2.5rem; margin-bottom:1rem; opacity:0.4;">📄</div>
                <div style="font-family:'Playfair Display',serif; font-size:1.1rem; color:#5a6a7a; margin-bottom:0.5rem;">Select a source to view its full record</div>
                <div style="font-size:0.85rem;">Use the filters on the left to narrow your search,<br>then click <em>Open →</em> on any source.</div>
            </div>
            """, unsafe_allow_html=True)
