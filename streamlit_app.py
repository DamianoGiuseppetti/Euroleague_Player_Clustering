"""EuroLeague Player Scouting dashboard — entry point and navigation.

v4 — Teamkeys-inspired full rebuild. Light EuroLeague theme over a GMM
clustering of rotation players (seasons 2020/21–2024/25).
"""

import sys
from pathlib import Path

import streamlit as st  # type: ignore[import]

sys.path.append(str(Path(__file__).resolve().parent))

st.set_page_config(
    page_title="EuroLeague Player Scouting",
    page_icon="🏀",
    layout="wide",
)

pg = st.navigation(
    {
        "Overview": [
            st.Page("app_pages/home.py", title="League Hub", icon="🏀", default=True),
        ],
        "Players": [
            st.Page("app_pages/player_profile.py", title="Player Profile", icon="🪪"),
            st.Page("app_pages/compare.py", title="Compare", icon="⚖️"),
            st.Page("app_pages/replacement_finder.py", title="Replacement Finder", icon="🧭"),
        ],
        "League": [
            st.Page("app_pages/rankings.py", title="Rankings", icon="📊"),
            st.Page("app_pages/archetypes.py", title="Archetypes", icon="🗺️"),
            st.Page("app_pages/teams.py", title="Teams", icon="🛡️"),
        ],
    }
)
pg.run()
