import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_utils import load_sources

ACTOR_PROFILES = {
    "Hezbollah": {
        "full_name": "Hezbollah (Party of God)",
        "type": "Non-state armed actor",
        "description": "Lebanese Shia political party and armed movement founded in 1982 with Iranian support. Operates as both a social movement and a military organisation. Principal armed actor in UNIFIL's area of operations since 2000.",
        "role_in_unifil": "Primary non-state armed actor in UNIFIL's area of operations. Central to UNIFIL's mandate constraints — the mission could not treat Hezbollah as a conventional military adversary given its dual civilian-military identity.",
    },
    "LAF": {
        "full_name": "Lebanese Armed Forces (LAF)",
        "type": "State armed forces",
        "description": "The official military of Lebanon. Key partner in UNIFIL's mandate implementation under UNSCR 1701, responsible for deployment in southern Lebanon alongside UNIFIL.",
        "role_in_unifil": "Primary host-state security partner. UNSCR 1701 mandates LAF deployment alongside UNIFIL in the south. LAF capacity constraints — financial, political, institutional — were a persistent limiting factor throughout the mission.",
    },
    "IDF": {
        "full_name": "Israel Defense Forces (IDF)",
        "type": "State armed forces",
        "description": "Military forces of Israel. Party to the conflict managed by UNIFIL's mandate, responsible for withdrawals in 1985 and 2000, and military operations in 2006 and 2024.",
        "role_in_unifil": "One of the two parties whose cessation of hostilities UNIFIL monitors. Israeli compliance with the Blue Line and UNSCR 1701 obligations is central to the mandate.",
    },
    "UNIFIL": {
        "full_name": "United Nations Interim Force in Lebanon",
        "type": "UN Peacekeeping Mission",
        "description": "Established by UNSCR 425/426 in 1978. Mandate significantly expanded by UNSCR 1701 in 2006. Operates as the primary UN presence in southern Lebanon, with ground and maritime components.",
        "role_in_unifil": "The subject of the lessons learned exercise itself.",
    },
    "UN Security Council": {
        "full_name": "United Nations Security Council",
        "type": "Intergovernmental body",
        "description": "The principal UN body responsible for international peace and security. Established UNIFIL's mandate and renewed it annually. P5 dynamics shaped mandate language and political support.",
        "role_in_unifil": "Mandate authority. Annual renewal debates reflect shifting P5 priorities and directly shaped UNIFIL's operational and political space.",
    },
    "TCCs": {
        "full_name": "Troop Contributing Countries",
        "type": "Member States",
        "description": "Countries contributing military personnel to UNIFIL. Major contributors include France, Italy, Spain, India, Indonesia, and Ghana. European TCCs have been central since 2006.",
        "role_in_unifil": "TCC cohesion, national caveats, and political will are critical variables in UNIFIL's operational effectiveness. TCC solidarity came under strain during the 2024 escalation.",
    },
    "Iran": {
        "full_name": "Islamic Republic of Iran",
        "type": "Regional power",
        "description": "Principal external patron of Hezbollah. Iranian support — financial, military, ideological — is foundational to Hezbollah's capacity and durability.",
        "role_in_unifil": "Indirect but significant actor. Iranian sponsorship of Hezbollah shapes the political-military environment UNIFIL operates in.",
    },
    "SLA": {
        "full_name": "South Lebanon Army (SLA)",
        "type": "Non-state armed actor (defunct)",
        "description": "Israeli-backed Lebanese militia that controlled the southern Security Zone from 1985 to 2000. Collapsed with the Israeli withdrawal in May 2000.",
        "role_in_unifil": "Controlled territory in UNIFIL's area of operations during 1985–2000. SLA collapse created a security vacuum that shaped the post-2000 environment.",
    },
    "Israel": {
        "full_name": "State of Israel",
        "type": "State actor",
        "description": "Party to the conflict managed by UNIFIL's mandate. Conducted military operations in Lebanon in 1978, 1982, 1993, 1996, 2006, and 2024.",
        "role_in_unifil": "One of the two primary parties to the cessation of hostilities framework under UNSCR 1701. Israeli compliance with Blue Line obligations has been persistently contested.",
    },
    "Lebanon": {
        "full_name": "Republic of Lebanon",
        "type": "Host state",
        "description": "The host state for UNIFIL. Lebanese sovereignty, political fragmentation, and state capacity constraints fundamentally shaped UNIFIL's operating environment.",
        "role_in_unifil": "Host state and primary partner. Political fragmentation and state weakness persistently limited what UNIFIL could achieve through the host-state channel.",
    },
}


def get_actor_color(actor_name, actor_type):
    """Color by category: UN=navy, armed groups=red, Israeli=bright blue, member states=green, other=grey."""
    name_lower = actor_name.lower()
    type_lower = actor_type.lower()
    if any(k in name_lower for k in ("israel", "idf")):
        return "#0ea5e9"   # bright blue — Israeli actors
    if any(k in name_lower for k in ("unifil", "united nations")) or \
       any(k in type_lower for k in ("peacekeeping", "intergovernmental")):
        return "#1a3a5c"   # UN navy
    if "armed actor" in type_lower or any(k in name_lower for k in ("hezbollah", "hamas", "sla", "amal")):
        return "#dc2626"   # red — armed groups
    if any(k in type_lower for k in ("member state", "host state", "state armed")) or \
       actor_name in ("TCCs", "Lebanon", "LAF"):
        return "#16a34a"   # green — member states
    return "#6b7c8d"       # grey


def get_actor_category(actor_name, actor_type):
    color = get_actor_color(actor_name, actor_type)
    return {
        "#0ea5e9": "Israeli actors",
        "#1a3a5c": "UN",
        "#dc2626": "Armed groups",
        "#16a34a": "Member states",
        "#6b7c8d": "Other",
    }.get(color, "Other")


def show():
    sources = load_sources()
    all_actors = sorted(set(a for s in sources for a in s.get("actors", [])))
    all_known = sorted(set(list(all_actors) + list(ACTOR_PROFILES.keys())))

    st.markdown("""
    <div class="library-header">
        <div>
            <p class="library-subtitle">Key Actors & Entities</p>
            <h1 class="library-title">Actors Index</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.9rem; color:#5a6a7a; margin-bottom:1.5rem; max-width:680px;">
        Browse key actors and entities in the UNIFIL operating environment.
        Select an actor to see their profile and all sources in the corpus that reference them.
    </div>
    """, unsafe_allow_html=True)

    if "selected_actor" not in st.session_state:
        st.session_state.selected_actor = None

    # ── Grid view ─────────────────────────────────────────────────────────────
    if st.session_state.selected_actor is None:

        # Colour legend
        st.markdown("""
        <div style="display:flex; flex-wrap:wrap; gap:0.3rem 1rem; margin-bottom:1rem; font-size:0.73rem; color:#5a6a7a;">
            <span><span style="display:inline-block; width:9px; height:9px; border-radius:2px; background:#1a3a5c; margin-right:3px; vertical-align:middle;"></span>UN</span>
            <span><span style="display:inline-block; width:9px; height:9px; border-radius:2px; background:#dc2626; margin-right:3px; vertical-align:middle;"></span>Armed groups</span>
            <span><span style="display:inline-block; width:9px; height:9px; border-radius:2px; background:#0ea5e9; margin-right:3px; vertical-align:middle;"></span>Israeli actors</span>
            <span><span style="display:inline-block; width:9px; height:9px; border-radius:2px; background:#16a34a; margin-right:3px; vertical-align:middle;"></span>Member states</span>
            <span><span style="display:inline-block; width:9px; height:9px; border-radius:2px; background:#6b7c8d; margin-right:3px; vertical-align:middle;"></span>Other</span>
        </div>
        """, unsafe_allow_html=True)

        # Compute max source count for progress bar normalisation
        counts = {a: sum(1 for s in sources if a in s.get("actors", [])) for a in all_known}
        max_count = max(counts.values(), default=1)

        cols = st.columns(3)
        for i, actor in enumerate(all_known):
            profile = ACTOR_PROFILES.get(actor, {})
            actor_type = profile.get("type", "Other")
            color = get_actor_color(actor, actor_type)
            category = get_actor_category(actor, actor_type)
            n = counts[actor]
            bar_width = max(int((n / max_count) * 100), 4) if max_count else 4

            with cols[i % 3]:
                st.markdown(f"""
                <div style="background:white; border:1px solid #ddd8cc; border-top:3px solid {color};
                     border-radius:4px; padding:1rem; margin-bottom:0.8rem; min-height:110px;">
                    <div style="font-family:'Playfair Display',serif; font-size:1rem; font-weight:600;
                         color:#1a3a5c; line-height:1.3; margin-bottom:0.3rem;">{actor}</div>
                    <div style="font-size:0.72rem; font-weight:600; color:{color}; letter-spacing:0.04em;
                         text-transform:uppercase; margin-bottom:0.4rem;">{category}</div>
                    <div style="font-size:0.78rem; color:#8a9ab0; margin-bottom:0.5rem;">{n} source{"s" if n!=1 else ""} in corpus</div>
                    <div style="background:#eef2f7; border-radius:2px; height:4px; width:100%;">
                        <div style="background:{color}; height:4px; border-radius:2px; width:{bar_width}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Explore →", key=f"actor_{actor}"):
                    st.session_state.selected_actor = actor
                    st.rerun()

    # ── Detail view ───────────────────────────────────────────────────────────
    else:
        actor = st.session_state.selected_actor
        profile = ACTOR_PROFILES.get(actor, {})
        actor_type = profile.get("type", "Other")
        color = get_actor_color(actor, actor_type)
        category = get_actor_category(actor, actor_type)

        if st.button("← Back to all actors"):
            st.session_state.selected_actor = None
            st.rerun()

        st.markdown(f"""
        <div style="margin:0.8rem 0 1.5rem 0;">
            <div style="font-family:'Playfair Display',serif; font-size:1.8rem; font-weight:700;
                 color:#1a3a5c; margin-bottom:0.3rem;">{actor}</div>
            <div style="font-size:0.82rem; font-weight:600; color:{color}; letter-spacing:0.04em;
                 text-transform:uppercase;">{category} · {actor_type}</div>
        </div>
        """, unsafe_allow_html=True)

        actor_sources = [s for s in sources if actor in s.get("actors", [])]

        col_profile, col_sources = st.columns([1, 1.6])

        with col_profile:
            if profile.get("full_name") and profile["full_name"] != actor:
                st.markdown(f'<div style="font-size:0.85rem; color:#5a6a7a; margin-bottom:0.8rem;"><em>{profile["full_name"]}</em></div>', unsafe_allow_html=True)

            if profile.get("description"):
                st.markdown('<div class="detail-section-title">Background</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="detail-body">{profile["description"]}</div>', unsafe_allow_html=True)

            if profile.get("role_in_unifil"):
                st.markdown('<div class="detail-section-title">Role in UNIFIL Context</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="detail-body">{profile["role_in_unifil"]}</div>', unsafe_allow_html=True)

            co_actors = sorted(set(a for s in actor_sources for a in s.get("actors", []) if a != actor))
            if co_actors:
                st.markdown('<div class="detail-section-title">Co-occurs with</div>', unsafe_allow_html=True)
                co_html = "".join([f'<span class="tag tag-actor">{a}</span>' for a in co_actors])
                st.markdown(f'<div style="margin-top:0.3rem;">{co_html}</div>', unsafe_allow_html=True)

        with col_sources:
            st.markdown(f'<div style="font-family:\'Playfair Display\',serif; font-size:1rem; font-weight:600; color:#1a3a5c; margin-bottom:0.8rem;">Sources ({len(actor_sources)})</div>', unsafe_allow_html=True)

            if not actor_sources:
                st.markdown('<div style="font-size:0.85rem; color:#8a9ab0; padding:0.5rem 0;">No sources currently reference this actor directly.</div>', unsafe_allow_html=True)
            else:
                for s in actor_sources:
                    clusters = s.get("thematic_clusters", [])[:2]
                    clusters_html = "".join([f'<span class="tag tag-cluster" style="font-size:0.68rem;">{c}</span>' for c in clusters])
                    cov = s.get("timeline_coverage", [])
                    if isinstance(cov, dict):
                        period_str = f"{cov.get('start','')}–{cov.get('end','')}"
                    elif isinstance(cov, list) and len(cov) == 2:
                        period_str = f"{cov[0]}–{cov[1]}"
                    else:
                        period_str = str(s.get("year", ""))
                    st.markdown(f"""
                    <div style="background:white; border:1px solid #ddd8cc; border-left:3px solid {color};
                         border-radius:3px; padding:0.8rem 1rem; margin-bottom:0.6rem;">
                        <div style="font-family:'Playfair Display',serif; font-size:0.9rem; font-weight:600;
                             color:#1a3a5c; margin-bottom:0.2rem;">{s['title']}</div>
                        <div style="font-size:0.78rem; color:#8a9ab0; margin-bottom:0.4rem;">{s['author']} · {s['year']} · covers {period_str}</div>
                        <div style="font-size:0.82rem; color:#3a3a3a; line-height:1.45; margin-bottom:0.5rem;">{s.get('abstract','')[:160]}{'…' if len(s.get('abstract',''))>160 else ''}</div>
                        <div>{clusters_html}</div>
                    </div>
                    """, unsafe_allow_html=True)
