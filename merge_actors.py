#!/usr/bin/env python3
"""merge_actors.py — merge actors_meta.json + actors_profiles.json → actors_combined.json"""
import json
from pathlib import Path

DATA_DIR = Path("data")

with open(DATA_DIR / "actors_meta.json", encoding="utf-8") as f:
    meta = json.load(f)  # {name: {category: ...}}

with open(DATA_DIR / "actors_profiles.json", encoding="utf-8") as f:
    profiles_list = json.load(f)  # [{name, category, description}]

with open(DATA_DIR / "sources.json", encoding="utf-8") as f:
    sources = json.load(f)

profile_by_name = {p["name"]: p for p in profiles_list}

# Build source lookup: actor name (lower) → list of {id, title, year, source_type}
source_index: dict = {}
for s in sources:
    for a in s.get("actors", []):
        source_index.setdefault(a.lower(), []).append({
            "id":          s.get("id", ""),
            "title":       s.get("title", ""),
            "year":        s.get("year", ""),
            "source_type": s.get("source_type", ""),
        })

# ── Auto-assignment keyword rules (applied in priority order) ─────────────────
UN_KEYS = [
    "unifil", "dpko", "dpo", "dppa", "unscol", "untso", "secretary-general",
    "force commander", "un observer", "maritime task force", "strategic military cell",
    "tripartite", "trilateral", "libat", "quintet", "urquhart", "erskine",
    "pellegrini", "graziano", "asarta", "paolo serra", "ridinò", "ridino",
    "guglietta", "pérez de cuéllar", "perez de cuellar", "picco", "higgins",
    "angioni", "miglietta", "angelotti", "security council",
]
ARMED_KEYS = [
    "hezbollah", "south lebanon army", "hamas", "islamic jihad",
    "isis", "jabhat al-nusra", "tufayli", "nasrallah",
    "believer's resistance", "arab socialist union", "revolutionary justice",
    "islamic students union", "al-qwat", "arafat", "habash", "abu nidal",
    "mustafa dirani", "italcon", "plo", "pflp", "dflp",
]
# Exact-name armed groups (checked separately to avoid substring false positives)
ARMED_EXACT = {"amal", "sla"}

ISRAEL_KEYS = [
    "menachem begin", "ariel sharon", "shlomo argov", "uri lubrani",
    "antoine lahad", "sa'ad haddad",
    "israel", " idf",
]
LEBANON_KEYS = [
    "lebanese", "berri", "junblat", "musa al-sadr", "raghib harb",
    "abbas musawi", "gemayel", "fadlallah", "shams al-din",
    "harakat al-mahrumin", "supreme islamic shia", "daoud sulaiman",
    "elias sarkis", "lebanese front", "lebanese national movement",
    "harakat", "mahrumin",
]
MEMBER_KEYS = [
    "united states", "european union", "multinational force",
    "arab deterrent force", "arab league",
    "george shultz", "caspar weinberger", "philip habib",
    "hafez al-assad", "anwar sadat", "jimmy carter",
    "france", "italy", "spain", "egypt", "saudi arabia",
    "norway", "finland", "ireland", "belgium", "estonia", "fiji",
]


def auto_category(name: str) -> str:
    n = name.lower()
    if n in ARMED_EXACT:
        return "Armed groups"
    for k in UN_KEYS:
        if k in n:
            return "UN"
    for k in ARMED_KEYS:
        if k in n:
            return "Armed groups"
    for k in ISRAEL_KEYS:
        if k in n:
            return "Israel"
    for k in LEBANON_KEYS:
        if k in n:
            return "Lebanon"
    for k in MEMBER_KEYS:
        if k in n:
            return "Member states"
    return "Other"


# ── Merge ──────────────────────────────────────────────────────────────────────
all_names = sorted(set(meta.keys()) | {p["name"] for p in profiles_list})

combined      = []
meta_only     = []
profiles_only = []   # (name, assigned_category)
merged_both   = []

for name in all_names:
    in_meta    = name in meta
    in_profile = name in profile_by_name

    if in_meta:
        category = meta[name].get("category", "Other")
    else:
        category = auto_category(name)

    description = profile_by_name[name]["description"] if in_profile else ""

    # Case-insensitive match to sources.json actors field
    matched_sources = source_index.get(name.lower(), [])

    combined.append({
        "name":        name,
        "category":    category,
        "description": description,
        "sources":     matched_sources,
    })

    if in_meta and not in_profile:
        meta_only.append(name)
    elif in_profile and not in_meta:
        profiles_only.append((name, category))
    else:
        merged_both.append(name)

# Write output
with open(DATA_DIR / "actors_combined.json", "w", encoding="utf-8") as f:
    json.dump(combined, f, indent=2, ensure_ascii=False)

# ── Report ─────────────────────────────────────────────────────────────────────
W = 62
print(f"\n{'='*W}")
print(f"  MERGE SUMMARY")
print(f"{'='*W}")
print(f"  Total actors in actors_combined.json : {len(combined)}")
print(f"  From meta only  (no profile desc)    : {len(meta_only)}")
print(f"  From profiles only (no meta, auto-cat): {len(profiles_only)}")
print(f"  In both meta + profiles               : {len(merged_both)}")

print(f"\n{'='*W}")
print(f"  META-ONLY ACTORS  (category from meta, no description)")
print(f"{'='*W}")
for n in sorted(meta_only):
    print(f"  {n:<40s} → {meta[n].get('category','Other')}")

print(f"\n{'='*W}")
print(f"  AUTO-ASSIGNED CATEGORIES  (in profiles, not in meta)")
print(f"{'='*W}")
for name, cat in sorted(profiles_only):
    print(f"  {name:<52s} → {cat}")

others = [n for n, c in profiles_only if c == "Other"]
print(f"\n{'='*W}")
print(f"  ACTORS LEFT AS 'Other' — review manually ({len(others)})")
print(f"{'='*W}")
for n in sorted(others):
    print(f"  {n}")

print()
