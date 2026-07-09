"""Replacement Finder — ranked statistical matches for any player-season."""

import streamlit as st

from src.dashboard_utils import (
    RADAR_FEATURES,
    cluster_badge,
    go_to_profile,
    hero,
    hover_values,
    inject_css,
    load_data,
    percentile_values,
    radar_chart,
    similar_players,
    table_height,
)

inject_css()
hero(
    "Replacement Finder",
    "Similarity = distance on the 20 z-scored model features, rescaled to 0-100.",
)

df = load_data()
options = sorted(df["player_season"])

c1, c2 = st.columns([2, 3])
with c1:
    choice = st.selectbox("Find a replacement for…", options)
with c2:
    f1, f2, f3 = st.columns(3)
    same_season = f1.toggle("Same season only", value=False)
    same_cluster = f2.toggle("Same archetype only", value=False)
    other_teams = f3.toggle("Exclude own team", value=True)
    n_results = st.slider("Results", 5, 25, 10)

row = df[df["player_season"] == choice].iloc[0]
row_idx = int(df[df["player_season"] == choice].index[0])

target_badge = cluster_badge(str(row["cluster_name"]))
st.markdown(
    f"<div class='tk-card tk-namecard'><h2>{row['display_name']}</h2>"
    f"<div class='meta'>{row['player.team.name']} · {row['season_label']} · "
    f"{row['pointsPerGame']:.1f} pts/g · {row['pirPerGame']:.1f} PIR/g</div>"
    f"<div style='margin-top:8px'>{target_badge}</div></div>",
    unsafe_allow_html=True,
)
st.write("")

matches = similar_players(
    row_idx,
    n=n_results,
    same_season_only=same_season,
    same_cluster_only=same_cluster,
    exclude_same_team=other_teams,
)

if matches is None or matches.empty:
    st.warning("No matches with these filters — try relaxing them.")
    st.stop()

# ---- Results table ----------------------------------------------------------- #
st.subheader(f"Top {len(matches)} matches")
view = matches[
    [
        "display_name", "season_label", "player.team.name", "cluster_name",
        "similarity", "pointsPerGame", "reboundsPerGame", "assistsPerGame", "pirPerGame",
    ]
].rename(
    columns={
        "display_name": "Player",
        "season_label": "Season",
        "player.team.name": "Team",
        "cluster_name": "Archetype",
        "similarity": "Fit",
        "pointsPerGame": "Pts/g",
        "reboundsPerGame": "Reb/g",
        "assistsPerGame": "Ast/g",
        "pirPerGame": "PIR/g",
    }
)
st.dataframe(
    view,
    hide_index=True,
    width="stretch",
    height=table_height(len(view)),
    column_config={
        "Fit": st.column_config.ProgressColumn("Fit /100", format="%.0f", min_value=0, max_value=100),
        "Pts/g": st.column_config.NumberColumn(format="%.1f"),
        "Reb/g": st.column_config.NumberColumn(format="%.1f"),
        "Ast/g": st.column_config.NumberColumn(format="%.1f"),
        "PIR/g": st.column_config.NumberColumn(format="%.1f"),
    },
)

# ---- Side-by-side radar -------------------------------------------------------- #
st.subheader("Overlay against a match")
pick = st.selectbox("Match to overlay", list(matches["player_season"]))
match_row = df[df["player_season"] == pick].iloc[0]

traces = [
    (str(row["display_name"]), percentile_values(row), hover_values(row)),
    (str(match_row["display_name"]), percentile_values(match_row), hover_values(match_row)),
]
c_radar, c_side = st.columns([3, 2])
with c_radar:
    st.plotly_chart(
        radar_chart(traces, list(RADAR_FEATURES.values())), width="stretch"
    )
with c_side:
    fit = float(matches.loc[matches["player_season"] == pick, "similarity"].iloc[0])
    match_badge = cluster_badge(str(match_row["cluster_name"]))
    st.markdown(
        f"<div class='tk-card'><div style='font-weight:800'>{match_row['display_name']}</div>"
        f"<div style='color:#5B6B7B; font-size:.9rem; margin-bottom:6px'>"
        f"{match_row['player.team.name']} · {match_row['season_label']}</div>{match_badge}"
        f"<div style='margin-top:10px; font-size:1.6rem; font-weight:800; color:#FF6113'>{fit:.0f}"
        f"<span style='font-size:.85rem; color:#5B6B7B'> /100 fit</span></div></div>",
        unsafe_allow_html=True,
    )
    st.write("")
    if st.button("Open this profile", width="stretch"):
        go_to_profile(str(match_row["player_season"]))
