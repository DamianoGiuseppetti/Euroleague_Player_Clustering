"""Teams — roster by team/season: archetype mix, team profile, roster table."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.dashboard_utils import (
    BRAND,
    CLUSTER_COLORS,
    PERGAME_STATS,
    go_to_profile,
    hero,
    inject_css,
    kpi_tile,
    load_data,
    pergame_table_config,
    table_height,
)

inject_css()
hero("Teams", "Roster construction through the archetype lens, one team-season at a time.")

df = load_data()

c1, c2 = st.columns(2)
with c1:
    seasons = sorted(df["season"].unique(), reverse=True)
    season = st.selectbox(
        "Season",
        seasons,
        format_func=lambda s: df.loc[df["season"] == s, "season_label"].iloc[0],
    )
league = df[df["season"] == season]
with c2:
    teams = sorted(league["player.team.name"].unique())
    team = st.selectbox("Team", teams)

roster = league[league["player.team.name"] == team].sort_values(
    "minutesPerGame", ascending=False
)

# ---- Team KPI tiles ------------------------------------------------------------- #
team_rank = (
    league.groupby("player.team.name")["pirPerGame"].mean().rank(ascending=False)
)
k1, k2, k3, k4 = st.columns(4)
k1.markdown(kpi_tile(f"{len(roster)}", "Rotation players"), unsafe_allow_html=True)
k2.markdown(
    kpi_tile(f"{roster['pointsPerGame'].sum():.0f}", "Rotation pts/game"),
    unsafe_allow_html=True,
)
k3.markdown(
    kpi_tile(f"{roster['rating_Overall'].mean():.0f}", "Avg overall rating"),
    unsafe_allow_html=True,
)
k4.markdown(
    kpi_tile(
        f"#{team_rank[team]:.0f}",
        f"Avg-PIR rank of {league['player.team.name'].nunique()} teams",
    ),
    unsafe_allow_html=True,
)

st.write("")

# ---- Archetype mix --------------------------------------------------------------- #
left, right = st.columns([2, 3])

with left:
    st.subheader("Archetype mix")
    st.caption("Share of rotation minutes by archetype — vs league average.")
    mix = (
        roster.groupby("cluster_name")["minutesPerGame"].sum()
        / roster["minutesPerGame"].sum()
        * 100
    )
    league_mix = (
        league.groupby("cluster_name")["minutesPerGame"].sum()
        / league["minutesPerGame"].sum()
        * 100
    )
    order = list(CLUSTER_COLORS)
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=order,
            x=[league_mix.get(a, 0) for a in order],
            orientation="h",
            name="League avg",
            marker_color=BRAND["line"],
            hovertemplate="%{y}: %{x:.0f}% of minutes<extra>League avg</extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            y=order,
            x=[mix.get(a, 0) for a in order],
            orientation="h",
            name=team,
            marker_color=[CLUSTER_COLORS[a] for a in order],
            hovertemplate="%{y}: %{x:.0f}% of minutes<extra></extra>",
        )
    )
    fig.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=BRAND["ink"]),
        xaxis=dict(title="% of rotation minutes", gridcolor=BRAND["line"]),
        yaxis=dict(autorange="reversed"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=30, b=10, l=10, r=10),
        height=340,
    )
    st.plotly_chart(fig, width="stretch")

with right:
    st.subheader("Roster")
    view = roster[
        ["display_name", "cluster_name", "Height", "rating_Overall"]
        + list(PERGAME_STATS)
    ].rename(
        columns={
            "display_name": "Player",
            "cluster_name": "Archetype",
            "Height": "cm",
            "rating_Overall": "OVR",
            **PERGAME_STATS,
        }
    )
    cfg = pergame_table_config()
    cfg["cm"] = st.column_config.NumberColumn(format="%.0f")
    cfg["OVR"] = st.column_config.ProgressColumn(
        "OVR", format="%.0f", min_value=0, max_value=100
    )
    st.dataframe(
        view,
        hide_index=True,
        width="stretch",
        height=table_height(len(view)),
        column_config=cfg,
    )

# ---- Jump to profile ---------------------------------------------------------------- #
player = st.selectbox(
    "Open a player profile",
    [""] + list(roster["player_season"]),
    format_func=lambda v: v or "Pick a player…",
)
if player:
    go_to_profile(player)

st.caption(
    "Only rotation players (≥12 min/g) are in the dataset — team totals cover the "
    "rotation, not the full roster."
)
