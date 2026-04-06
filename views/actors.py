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

TYPE_COLORS = {
    "Non-state armed actor": "#8b1a1a",
    "State armed forces": "#1a3a5c",
    "UN Peacekeeping Mission": "#1a5c9c",
    "Intergovernmental body": "#3a5c1a",
    "Member States": "#5c3a1a",
    "Regional power": "#5c1a5c",
    "State actor": "#1a3a5c",
    "Host state": "#2a5c4a",
    "Non-state armed actor (defunct)": "#6a6a6a",
}

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

    col_list, col_detail = st.columns([1, 2])

    with col_list:
        st.markdown('<div style="font-family:\'Playfair Display\',serif; font-size:1rem; font-weight:600; color:#1a3a5c; margin-bottom:0.8rem;">All Actors</div>', unsafe_allow_html=True)

        for actor in all_known:
            profile = ACTOR_PROFILES.get(actor, {})
            actor_type = profile.get("type", "Other")
            color = TYPE_COLORS.get(actor_type, "#888")
            source_count = sum(1 for s in sources if actor in s.get("actors", []))
            is_sel = st.session_state.selected_actor == actor
            bg = "#fdf7ee" if is_sel else "white"
            border = "#c8952a" if is_sel else color

            st.markdown(f"""
            <div style="background:{bg}; border:1px solid #ddd8cc; border-left:3px solid {border};
                 border-radius:3px; padding:0.6rem 0.9rem; margin-bottom:0.4rem;">
                <div style="font-weight:600; font-size:0.9rem; color:#1a3a5c;">{actor}</div>
                <div style="font-size:0.72rem; color:{color}; margin-top:0.1rem;">{actor_type}</div>
                <div style="font-size:0.72rem; color:#8a9ab0; margin-top:0.1rem;">{source_count} source{"s" if source_count!=1 else ""} in corpus</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("View →", key=f"actor_{actor}"):
                st.session_state.selected_actor = actor
                st.rerun()

    with col_detail:
        actor = st.session_state.selected_actor
        if not actor:
            st.markdown("""
            <div style="padding:4rem 2rem; text-align:center; color:#8a9ab0;">
                <div style="font-size:2rem; margin-bottom:1rem; opacity:0.4;">🏛</div>
                <div style="font-family:'Playfair Display',serif; font-size:1.1rem; color:#5a6a7a; margin-bottom:0.5rem;">Select an actor to view their profile</div>
                <div style="font-size:0.85rem;">Profiles include role in UNIFIL context and all linked sources.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            profile = ACTOR_PROFILES.get(actor, {})
            actor_type = profile.get("type", "Other")
            color = TYPE_COLORS.get(actor_type, "#888")

            if st.button("← Back", key="back_actor"):
                st.session_state.selected_actor = None
                st.rerun()

            st.markdown(f"""
            <div style="margin:0.5rem 0 1.2rem 0;">
                <div style="font-family:'Playfair Display',serif; font-size:1.6rem; font-weight:700; color:#1a3a5c; margin-bottom:0.3rem;">{actor}</div>
                <div style="font-size:0.82rem; font-weight:600; color:{color}; letter-spacing:0.04em; text-transform:uppercase;">{actor_type}</div>
            </div>
            """, unsafe_allow_html=True)

            if profile.get("full_name") and profile["full_name"] != actor:
                st.markdown(f'<div style="font-size:0.85rem; color:#5a6a7a; margin-bottom:0.8rem;"><em>{profile["full_name"]}</em></div>', unsafe_allow_html=True)

            if profile.get("description"):
                st.markdown('<div class="detail-section-title">Background</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="detail-body">{profile["description"]}</div>', unsafe_allow_html=True)

            if profile.get("role_in_unifil"):
                st.markdown('<div class="detail-section-title">Role in UNIFIL Context</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="detail-body">{profile["role_in_unifil"]}</div>', unsafe_allow_html=True)

            actor_sources = [s for s in sources if actor in s.get("actors", [])]
            st.markdown(f'<div class="detail-section-title">Sources ({len(actor_sources)})</div>', unsafe_allow_html=True)

            if not actor_sources:
                st.markdown('<div style="font-size:0.85rem; color:#8a9ab0; padding:0.5rem 0;">No sources currently reference this actor directly.</div>', unsafe_allow_html=True)
            else:
                for s in actor_sources:
                    clusters = s.get("thematic_clusters", [])[:2]
                    clusters_html = "".join([f'<span class="tag tag-cluster" style="font-size:0.68rem;">{c}</span>' for c in clusters])
                    cov = s.get("timeline_coverage", [])
                    period_str = f"{cov[0]}–{cov[1]}" if len(cov) == 2 else str(s.get("year",""))
                    st.markdown(f"""
                    <div style="background:white; border:1px solid #ddd8cc; border-left:3px solid #1a3a5c;
                         border-radius:3px; padding:0.8rem 1rem; margin-bottom:0.6rem;">
                        <div style="font-family:'Playfair Display',serif; font-size:0.9rem; font-weight:600; color:#1a3a5c; margin-bottom:0.2rem;">{s['title']}</div>
                        <div style="font-size:0.78rem; color:#8a9ab0; margin-bottom:0.4rem;">{s['author']} · {s['year']} · covers {period_str}</div>
                        <div style="font-size:0.82rem; color:#3a3a3a; line-height:1.45; margin-bottom:0.5rem;">{s.get('abstract','')[:160]}{'…' if len(s.get('abstract',''))>160 else ''}</div>
                        <div>{clusters_html}</div>
                    </div>
                    """, unsafe_allow_html=True)

            co_actors = sorted(set(a for s in actor_sources for a in s.get("actors", []) if a != actor))
            if co_actors:
                st.markdown('<div class="detail-section-title">Co-occurs with</div>', unsafe_allow_html=True)
                co_html = "".join([f'<span class="tag tag-actor">{a}</span>' for a in co_actors])
                st.markdown(f'<div style="margin-top:0.3rem;">{co_html}</div>', unsafe_allow_html=True)
