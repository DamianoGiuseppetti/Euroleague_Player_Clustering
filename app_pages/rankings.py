"""Rankings — filterable leaderboards on per-game stats and skill ratings."""

import streamlit as st

from src.dashboard_utils import (
    RATINGS,
    hero,
    inject_css,
    load_data,
    table_height,
)

inject_css()
hero("Rankings", "Leaderboards on per-game production or Teamkeys-style skill ratings.")

df = load_data()

# ---- Filters ----------------------------------------------------------------- #
f1, f2, f3, f4 = st.columns([1, 1.4, 1.4, 1.2])
with f1:
    seasons = ["All"] + sorted(df["season"].unique(), reverse=True)
    season = st.selectbox(
        "Season",
        seasons,
        format_func=lambda s: "All seasons" if s == "All"
        else df.loc[df["season"] == s, "season_label"].iloc[0],
    )
with f2:
    teams = ["All"] + sorted(df["player.team.name"].unique())
    team = st.selectbox("Team", teams)
with f3:
    archetypes = ["All"] + sorted(df["cluster_name"].unique())
    archetype = st.selectbox("Archetype", archetypes)
with f4:
    min_min = st.slider("Min minutes/g", 12, 30, 12)

METRICS = {
    "Points / game": "pointsPerGame",
    "Rebounds / game": "reboundsPerGame",
    "Assists / game": "assistsPerGame",
    "Steals / game": "stealsPerGame",
    "Blocks / game": "blocksPerGame",
    "PIR / game": "pirPerGame",
    "3PT %": "threePointersPct",
    "FT %": "freeThrowsPct",
}
for name in RATINGS:
    METRICS[f"Rating · {name}"] = f"rating_{name}"
METRICS["Rating · Overall"] = "rating_Overall"

metric_label = st.selectbox("Rank by", list(METRICS))
metric = METRICS[metric_label]

# ---- Apply filters -------------------------------------------------------------- #
pool = df.copy()
if season != "All":
    pool = pool[pool["season"] == season]
if team != "All":
    pool = pool[pool["player.team.name"] == team]
if archetype != "All":
    pool = pool[pool["cluster_name"] == archetype]
pool = pool[pool["minutesPerGame"] >= min_min]
pool = pool.dropna(subset=[metric])

if pool.empty:
    st.warning("No players match these filters.")
    st.stop()

# Percentile of the ranking metric within the FILTERED view
pool = pool.copy()
pool["view_pct"] = pool[metric].rank(pct=True) * 100
pool = pool.sort_values(metric, ascending=False)

n_show = st.slider("Show top", 10, min(100, len(pool)), min(25, len(pool)))
top = pool.head(n_show)

view = top[
    [
        "display_name", "season_label", "player.team.name", "cluster_name",
        metric, "view_pct", "minutesPerGame", "gamesPlayed",
    ]
].rename(
    columns={
        "display_name": "Player",
        "season_label": "Season",
        "player.team.name": "Team",
        "cluster_name": "Archetype",
        metric: metric_label,
        "view_pct": "Percentile (view)",
        "minutesPerGame": "Min/g",
        "gamesPlayed": "Games",
    }
)
view.insert(0, "#", range(1, len(view) + 1))

is_rating = metric.startswith("rating_")
st.dataframe(
    view,
    hide_index=True,
    width="stretch",
    height=table_height(len(view)),
    column_config={
        "#": st.column_config.NumberColumn(width="small"),
        metric_label: st.column_config.NumberColumn(format="%.0f" if is_rating else "%.1f"),
        "Percentile (view)": st.column_config.ProgressColumn(
            "Percentile in this view", format="%.0f", min_value=0, max_value=100
        ),
        "Min/g": st.column_config.NumberColumn(format="%.1f"),
        "Games": st.column_config.NumberColumn(format="%.0f"),
    },
)
st.caption(
    "The percentile bar is computed within the filtered view above, not the whole league."
)
