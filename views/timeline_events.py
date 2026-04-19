import re
import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_utils import load_sources


# ── Data extraction ───────────────────────────────────────────────────────────

def _extract_year(date_str):
    """Return the first 4-digit year found in a date string, or None."""
    m = re.search(r'\b(1\d{3}|20\d{2})\b', str(date_str))
    return int(m.group(1)) if m else None


def build_events(sources):
    """
    Collect all timeline_events entries from every source.
    Deduplicate on (exact date, first 6 words of event text).
    Sort chronologically; events with no parseable year go to the end.
    Returns list of dicts: date, event, sort_year, source_author, source_year.
    """
    seen   = set()
    events = []
    for s in sources:
        for e in s.get("timeline_events", []):
            date = str(e.get("date",  "")).strip()
            text = str(e.get("event", "")).strip()
            if not text:
                continue
            key = (date, " ".join(text.lower().split()[:6]))
            if key in seen:
                continue
            seen.add(key)
            events.append({
                "date":          date,
                "event":         text,
                "sort_year":     _extract_year(date),
                "source_author": s.get("author", ""),
                "source_year":   s.get("year", ""),
            })

    events.sort(key=lambda e: (e["sort_year"] is None, e["sort_year"] or 9999))
    return events


# ── Card renderer ─────────────────────────────────────────────────────────────

def _card(event, side):
    align = "right" if side == "left" else "left"
    border_css = (
        "border-right:3px solid #1a3a5c;" if side == "left"
        else "border-left:3px solid #1a3a5c;"
    )
    attr = f"{event['source_author']} · {event['source_year']}" if event["source_author"] else ""
    attr_html = (
        f'<div style="font-size:0.72rem;color:#8a9ab0;margin-top:0.3rem;">{attr}</div>'
        if attr else ""
    )
    st.markdown(f"""
    <div style="background:white;border:1px solid #ddd8cc;{border_css}border-radius:5px;
         padding:0.9rem 1.1rem;box-shadow:0 1px 6px rgba(26,58,92,0.06);
         text-align:{align};margin-bottom:0.3rem;">
        <div style="font-size:0.75rem;font-weight:600;color:#8a9ab0;
             letter-spacing:0.06em;text-transform:uppercase;margin-bottom:0.25rem;">
            {event['date']}
        </div>
        <div style="font-family:'Playfair Display',serif;font-size:0.95rem;font-weight:700;
             color:#1a3a5c;margin-bottom:0.3rem;line-height:1.3;">
            {event['event']}
        </div>
        {attr_html}
    </div>
    """, unsafe_allow_html=True)


def _dot():
    st.markdown("""
    <div style="display:flex;justify-content:center;align-items:flex-start;
         padding-top:1rem;height:100%;">
        <div style="width:12px;height:12px;border-radius:50%;
             background:#1a3a5c;border:2px solid white;
             box-shadow:0 0 0 2px #1a3a5c;flex-shrink:0;"></div>
    </div>
    """, unsafe_allow_html=True)


# ── Page ──────────────────────────────────────────────────────────────────────

def show():
    sources    = load_sources()
    all_events = build_events(sources)

    st.markdown("""
    <div class="library-header">
        <div>
            <h1 class="library-title">Event Timeline</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)

    total = len(all_events)
    years_with_events = len(set(e["sort_year"] for e in all_events if e["sort_year"]))
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-number">{total}</div>
            <div class="metric-label">Events</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{years_with_events}</div>
            <div class="metric-label">Years covered</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{len(sources)}</div>
            <div class="metric-label">Sources indexed</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.9rem; color:#5a6a7a; margin-bottom:1.2rem; max-width:680px;">
        Historical events documented across all sources in the corpus, deduplicated and
        sorted chronologically. Each entry is drawn from the
        <em>timeline_events</em> field of a source record.
    </div>
    """, unsafe_allow_html=True)

    # Optional year-range filter
    parseable = [e["sort_year"] for e in all_events if e["sort_year"] is not None]
    if parseable:
        y_min, y_max = min(parseable), max(parseable)
        year_range = st.slider(
            "Filter by year",
            min_value=y_min, max_value=y_max,
            value=(y_min, y_max), step=1, format="%d",
            key="events_timeline_years",
        )
        y_start, y_end = year_range
        filtered = [
            e for e in all_events
            if e["sort_year"] is not None and y_start <= e["sort_year"] <= y_end
        ]
    else:
        filtered = list(all_events)
        y_start = y_end = "—"

    st.markdown(
        f'<div style="font-size:0.82rem;color:#6b7c8d;margin:0.6rem 0 1rem 0;'
        f'letter-spacing:0.04em;text-transform:uppercase;">'
        f'{len(filtered)} event{"s" if len(filtered) != 1 else ""}</div>',
        unsafe_allow_html=True,
    )

    if not filtered:
        st.markdown(
            '<div style="padding:3rem;text-align:center;color:#8a9ab0;">'
            'No events found for this period.</div>',
            unsafe_allow_html=True,
        )
        return

    # Alternating two-column timeline
    for idx, event in enumerate(filtered):
        side = "left" if idx % 2 == 0 else "right"

        if idx > 0:
            conn = st.columns([5, 1, 5])
            with conn[1]:
                st.markdown(
                    '<div style="height:20px;border-left:2px solid #1a3a5c;'
                    'margin:0 auto;width:2px;opacity:0.2;"></div>',
                    unsafe_allow_html=True,
                )

        row = st.columns([5, 1, 5])
        with row[0]:
            if side == "left":
                _card(event, "left")
            else:
                st.markdown("<div></div>", unsafe_allow_html=True)
        with row[1]:
            _dot()
        with row[2]:
            if side == "right":
                _card(event, "right")
            else:
                st.markdown("<div></div>", unsafe_allow_html=True)
