import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_utils import load_sources, THEMATIC_CLUSTERS

def get_all_lessons(sources, clusters=None, tag_filter=None, search=None):
    lessons = []
    for s in sources:
        for l in s.get("lessons_learned", []):
            text = l.get("text", "")
            tag = l.get("tag", "")
            source_clusters = s.get("thematic_clusters", [])

            if clusters and not any(c in source_clusters for c in clusters):
                continue
            if tag_filter and tag not in tag_filter:
                continue
            if search and search.lower() not in text.lower():
                continue

            lessons.append({
                "text": text,
                "tag": tag,
                "source_id": s.get("id", ""),
                "source_title": s.get("title", ""),
                "source_author": s.get("author", ""),
                "source_year": s.get("year", ""),
                "source_type": s.get("source_type", ""),
                "thematic_clusters": source_clusters,
            })
    return lessons

def show():
    sources = load_sources()
    all_lessons = get_all_lessons(sources)

    st.markdown("""
    <div class="library-header">
        <div>
            <p class="library-subtitle">Extracted from the Corpus</p>
            <h1 class="library-title">Lessons Log</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.9rem; color:#5a6a7a; margin-bottom:1.5rem; max-width:680px;">
        All lessons learned candidates extracted from the corpus, organised by theme.
        <span style="color:#2a7a2a; font-weight:600;">Source-derived</span> lessons come directly from what authors argue.
        <span style="color:#8b3a1a; font-weight:600;">Analytical inferences</span> are conclusions drawn by the researcher from the source material.
    </div>
    """, unsafe_allow_html=True)

    # Metrics
    n_total = len(all_lessons)
    n_sd = sum(1 for l in all_lessons if l["tag"] == "SOURCE-DERIVED")
    n_ai = sum(1 for l in all_lessons if l["tag"] == "ANALYTICAL INFERENCE")
    n_sources = len(set(l["source_id"] for l in all_lessons))

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-number">{n_total}</div>
            <div class="metric-label">Total LL candidates</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{n_sd}</div>
            <div class="metric-label">Source-derived</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{n_ai}</div>
            <div class="metric-label">Analytical inferences</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{n_sources}</div>
            <div class="metric-label">Contributing sources</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Filters ───────────────────────────────────────────────────────────────
    col_f1, col_f2, col_f3 = st.columns([2, 1, 1.5])
    with col_f1:
        search = st.text_input("Search lessons", placeholder="e.g. force protection, civilian, mandate…", key="ll_search")
    with col_f2:
        tag_filter = st.multiselect(
            "Type",
            ["SOURCE-DERIVED", "ANALYTICAL INFERENCE"],
            key="ll_tag"
        )
    with col_f3:
        cluster_filter = st.multiselect(
            "Thematic cluster",
            THEMATIC_CLUSTERS,
            key="ll_cluster"
        )

    filtered = get_all_lessons(
        sources,
        clusters=cluster_filter if cluster_filter else None,
        tag_filter=tag_filter if tag_filter else None,
        search=search if search else None,
    )

    st.markdown(f'<div style="font-size:0.82rem; color:#6b7c8d; margin: 0.8rem 0; letter-spacing:0.04em; text-transform:uppercase;">{len(filtered)} lesson{"s" if len(filtered)!=1 else ""} shown</div>', unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── View toggle: by theme or flat list ───────────────────────────────────
    view_mode = st.radio(
        "View as",
        ["By theme", "Flat list"],
        horizontal=True,
        key="ll_view"
    )

    if view_mode == "By theme":
        # Group lessons by thematic cluster
        cluster_lessons = {c: [] for c in THEMATIC_CLUSTERS}
        untagged = []
        for l in filtered:
            placed = False
            for c in l["thematic_clusters"]:
                if c in cluster_lessons:
                    cluster_lessons[c].append(l)
                    placed = True
            if not placed:
                untagged.append(l)

        for cluster, lessons in cluster_lessons.items():
            if not lessons:
                continue

            st.markdown(f"""
            <div style="font-family:'Playfair Display',serif; font-size:1.1rem; font-weight:600;
                 color:#1a3a5c; margin: 1.5rem 0 0.8rem 0; padding-bottom:0.3rem;
                 border-bottom:2px solid #1a3a5c;">{cluster}
                 <span style="font-size:0.8rem; font-weight:400; color:#8a9ab0; margin-left:0.5rem;">{len(lessons)}</span>
            </div>
            """, unsafe_allow_html=True)

            for l in lessons:
                render_lesson_card(l)

        if untagged:
            st.markdown('<div style="font-family:\'Playfair Display\',serif; font-size:1rem; font-weight:600; color:#8a9ab0; margin:1.5rem 0 0.8rem 0;">Other</div>', unsafe_allow_html=True)
            for l in untagged:
                render_lesson_card(l)

    else:
        # Flat list
        if not filtered:
            st.markdown('<div style="font-size:0.9rem; color:#8a9ab0; padding:2rem 0;">No lessons match the current filters.</div>', unsafe_allow_html=True)
        for l in filtered:
            render_lesson_card(l)


def render_lesson_card(l):
    tag = l.get("tag", "")
    is_sd = tag == "SOURCE-DERIVED"
    tag_class = "tag-lesson-sd" if is_sd else "tag-lesson-ai"
    border_color = "#9ac99a" if is_sd else "#c99a8a"
    bg_color = "#f8fdf8" if is_sd else "#fdf8f6"

    clusters_html = "".join([
        f'<span class="tag tag-cluster" style="font-size:0.68rem;">{c}</span>'
        for c in l.get("thematic_clusters", [])[:2]
    ])

    st.markdown(f"""
    <div style="background:{bg_color}; border:1px solid #e0dbd2; border-left:3px solid {border_color};
         border-radius:3px; padding:0.9rem 1.1rem; margin-bottom:0.6rem;">
        <div style="margin-bottom:0.5rem;">
            <span class="tag {tag_class}">{tag}</span>
        </div>
        <div style="font-size:0.92rem; color:#1c1c1c; line-height:1.6; margin-bottom:0.6rem;">
            {l['text']}
        </div>
        <div style="display:flex; align-items:center; gap:0.8rem; flex-wrap:wrap;">
            <span style="font-size:0.75rem; color:#8a9ab0; font-style:italic;">
                — {l['source_author']}, {l['source_year']} · {l['source_type']}
            </span>
            {clusters_html}
        </div>
    </div>
    """, unsafe_allow_html=True)
