"""League Hub — landing page: KPIs, archetype landscape, league leaders, search."""

import plotly.express as px
import streamlit as st

from src.dashboard_utils import (
    BRAND,
    CLUSTER_COLORS,
    compute_pca,
    go_to_profile,
    hero,
    inject_css,
    kpi_tile,
    leader_list,
    load_data,
)

inject_css()
hero(
    "EuroLeague League Hub",
    "GMM archetypes of rotation players (≥12 min/g) · seasons 2020/21–2024/25",
)

df = load_data()

# ---- Season selector + search -------------------------------------------- #
c_season, c_search = st.columns([1, 3])
with c_season:
    seasons = sorted(df["season"].unique(), reverse=True)
    season = st.selectbox(
        "Season",
        seasons,
        format_func=lambda s: df.loc[df["season"] == s, "season_label"].iloc[0],
    )
with c_search:
    target = st.selectbox(
        "Jump to a player profile",
        [""] + sorted(df["player_season"]),
        format_func=lambda v: v or "Search a player…",
    )
    if target:
        go_to_profile(target)

pool = df[df["season"] == season]

# ---- KPI tiles ------------------------------------------------------------ #
top_scorer = pool.loc[pool["pointsPerGame"].idxmax()]
k1, k2, k3, k4 = st.columns(4)
k1.markdown(kpi_tile(f"{len(pool)}", "Rotation players"), unsafe_allow_html=True)
k2.markdown(kpi_tile(f"{pool['player.team.code'].nunique()}", "Teams"), unsafe_allow_html=True)
k3.markdown(kpi_tile(f"{pool['pirPerGame'].mean():.1f}", "Avg PIR / game"), unsafe_allow_html=True)
k4.markdown(
    kpi_tile(f"{top_scorer['display_name']}", f"Top scorer · {top_scorer['pointsPerGame']:.1f} pts/g"),
    unsafe_allow_html=True,
)

st.write("")

# ---- Archetype landscape (PCA) -------------------------------------------- #
left, right = st.columns([3, 2])

with left:
    st.subheader("Archetype landscape")
    st.caption("Each dot is a player-season, projected with PCA on the 20 model features.")
    pca = compute_pca()
    pca_pool = pca[pca["season"] == season]
    fig = px.scatter(
        pca_pool,
        x="PC1",
        y="PC2",
        color="cluster_name",
        color_discrete_map=CLUSTER_COLORS,
        hover_name="display_name",
        hover_data={
            "PC1": False,
            "PC2": False,
            "cluster_name": False,
            "player.team.name": True,
            "pointsPerGame": ":.1f",
            "pirPerGame": ":.1f",
        },
        labels={"player.team.name": "Team", "pointsPerGame": "Pts/g", "pirPerGame": "PIR/g"},
    )
    fig.update_traces(marker=dict(size=9, opacity=0.85, line=dict(width=0.5, color="white")))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=BRAND["ink"]),
        xaxis=dict(title="", showticklabels=False, gridcolor=BRAND["line"], zeroline=False),
        yaxis=dict(title="", showticklabels=False, gridcolor=BRAND["line"], zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, title=""),
        margin=dict(t=10, b=10, l=10, r=10),
        height=480,
    )
    st.plotly_chart(fig, width="stretch")

with right:
    st.subheader("Archetype share")
    counts = pool["cluster_name"].value_counts()
    fig_share = px.bar(
        counts,
        orientation="h",
        color=counts.index,
        color_discrete_map=CLUSTER_COLORS,
        labels={"value": "Players", "index": ""},
    )
    fig_share.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=BRAND["ink"]),
        showlegend=False,
        xaxis=dict(gridcolor=BRAND["line"], title="Players"),
        yaxis=dict(title="", autorange="reversed"),
        margin=dict(t=10, b=10, l=10, r=10),
        height=200,
    )
    st.plotly_chart(fig_share, width="stretch")
    st.caption(
        "Archetypes come from a Gaussian Mixture Model — every player also has a "
        "membership probability, visible on their profile."
    )

st.write("")

# ---- League leaders -------------------------------------------------------- #
st.subheader("League leaders")
categories = [
    ("pointsPerGame", "Points / game"),
    ("assistsPerGame", "Assists / game"),
    ("reboundsPerGame", "Rebounds / game"),
    ("pirPerGame", "PIR / game"),
]
cols = st.columns(4)
for col, (stat, label) in zip(cols, categories):
    body = leader_list(pool, stat)
    col.markdown(
        f"<div class='tk-card'><div class='tk-kpi'><div class='l'>{label}</div></div>{body}</div>",
        unsafe_allow_html=True,
    )
