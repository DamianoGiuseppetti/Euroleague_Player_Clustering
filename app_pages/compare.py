"""Compare — head-to-head matrix (2-4 player-seasons) with winner highlighting."""

import streamlit as st

from src.dashboard_utils import (
    CLUSTER_COLORS,
    PERGAME_STATS,
    RADAR_FEATURES,
    RATINGS,
    cluster_badge,
    comparison_matrix,
    hero,
    hover_values,
    inject_css,
    load_data,
    percentile_values,
    radar_chart,
)

inject_css()
hero("Compare", "Pick 2-4 player-seasons — best value per row is highlighted.")

df = load_data()
options = sorted(df["player_season"])

picks = st.multiselect(
    "Player-seasons",
    options,
    default=st.session_state.get("compare_picks", []),
    max_selections=4,
)
st.session_state["compare_picks"] = picks

if len(picks) < 2:
    st.info("Select at least two player-seasons to compare.")
    st.stop()

rows = [df[df["player_season"] == p].iloc[0] for p in picks]

# ---- Archetype badges ------------------------------------------------------- #
badge_cols = st.columns(len(rows))
for col, r in zip(badge_cols, rows):
    body = cluster_badge(str(r["cluster_name"]))
    col.markdown(
        f"<div class='tk-card' style='text-align:center'>"
        f"<div style='font-weight:800; margin-bottom:6px'>{r['display_name']}</div>{body}</div>",
        unsafe_allow_html=True,
    )

st.write("")

# ---- Radar overlay + matrices ------------------------------------------------ #
left, right = st.columns([2, 3])

with left:
    st.subheader("Radar overlay")
    palette = [CLUSTER_COLORS[str(r["cluster_name"])] for r in rows]
    # Avoid two players sharing a colour: fall back to a fixed palette on clash
    if len(set(palette)) < len(palette):
        palette = ["#FF6113", "#2E6FF2", "#17A674", "#8A4FE0"]
    traces = [
        (str(r["display_name"]), percentile_values(r), hover_values(r)) for r in rows
    ]
    st.plotly_chart(
        radar_chart(traces, list(RADAR_FEATURES.values()), colors=palette),
        width="stretch",
    )

with right:
    st.subheader("Skill ratings")
    ratings_stats = {f"rating_{n}": n for n in RATINGS}
    ratings_stats["rating_Overall"] = "Overall"
    st.markdown(
        "<div class='tk-card'>" + comparison_matrix(rows, ratings_stats) + "</div>",
        unsafe_allow_html=True,
    )

st.write("")
st.subheader("Per-game stats")
pergame_stats = {c: l for c, l in PERGAME_STATS.items() if c != "gamesPlayed"}
pergame_stats["gamesPlayed"] = "Games"
st.markdown(
    "<div class='tk-card'>" + comparison_matrix(rows, pergame_stats) + "</div>",
    unsafe_allow_html=True,
)
st.caption("Turnovers: the highlighted cell still marks the highest value, not the best one.")
