"""
One-off script: merge timeline_events from sources.json into unifil_timeline.json.
Deduplicates by event title (case-insensitive). Sorts result by year.
Writes result back to data/unifil_timeline.json. Does NOT touch sources.json.
"""
import json
import re
from pathlib import Path

SOURCES_PATH  = Path("data/sources.json")
TIMELINE_PATH = Path("data/unifil_timeline.json")


def extract_year(date_str):
    """Return the first 4-digit year found in a date string, or 9999 if none."""
    m = re.search(r'\b(1\d{3}|20\d{2})\b', str(date_str))
    return int(m.group(1)) if m else 9999


def sort_key(event):
    """Sort key: year, then original date string for stable secondary sort."""
    return (extract_year(event.get("date", "")), str(event.get("date", "")))


# ── 1 & 2. Load sources and extract timeline_events ──────────────────────────
sources = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))

candidate_events = []
for source in sources:
    for evt in source.get("timeline_events", []):
        # 3. Must have at minimum "date" and "event"
        if not evt.get("date") or not evt.get("event"):
            continue
        candidate_events.append(evt)

# ── 4. Load existing timeline ─────────────────────────────────────────────────
existing = json.loads(TIMELINE_PATH.read_text(encoding="utf-8"))
original_count = len(existing)

# ── 5. Deduplicate and merge ──────────────────────────────────────────────────
# Build a set of normalised titles already in the timeline
existing_titles = {e["event"].strip().lower() for e in existing}

added = 0
skipped = 0

for evt in candidate_events:
    title_norm = evt["event"].strip().lower()
    if title_norm in existing_titles:
        skipped += 1
        continue
    # Build a record matching unifil_timeline.json schema
    existing.append({
        "date":        evt["date"],
        "event":       evt["event"],
        "category":    evt.get("category", ""),
        "description": evt.get("description", evt["event"]),
    })
    existing_titles.add(title_norm)
    added += 1

# ── 6. Sort by date ───────────────────────────────────────────────────────────
existing.sort(key=sort_key)

# ── 7. Write back ─────────────────────────────────────────────────────────────
TIMELINE_PATH.write_text(
    json.dumps(existing, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

# ── 8. Summary ────────────────────────────────────────────────────────────────
print(f"Original events : {original_count}")
print(f"Candidates found: {len(candidate_events)}")
print(f"Added           : {added}")
print(f"Duplicates skipped: {skipped}")
print(f"Total in file   : {len(existing)}")
