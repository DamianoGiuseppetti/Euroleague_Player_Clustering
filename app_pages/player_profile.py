"""Player Profile — one-pager scouting card: ratings, badges, radar, shot diet."""

import streamlit as st

from src.dashboard_utils import (
    PERCENTILE_PANEL,
    RADAR_FEATURES,
    RATING_HELP,
    RATINGS,
    badge_chips,
    badges_for,
    cluster_badge,
    go_to_profile,
    hero,
    hover_values,
    inject_css,
    load_data,
    percentile_bars,
    percentile_values,
    prob_segments,
    radar_chart,
    rating_tile,
    shot_profile_chart,
    similar_players,
)

inject_css()
hero("Player Profile", "One-pager scouting card — every number is a season percentile unless stated.")

df = load_data()
options = sorted(df["player_season"])

# Focus request coming from another page (search, similar-players strip, roster…)
focus = st.session_state.pop("focus_player_season", None)
default_idx = options.index(focus) if focus in options else 0

choice = st.selectbox("Player · season", options, index=default_idx)
row = df[df["player_season"] == choice].iloc[0]
row_idx = int(df[df["player_season"] == choice].index[0])

# ---- Header card ----------------------------------------------------------- #
conf = float(row["cluster_prob_max"]) * 100
badge_html = cluster_badge(str(row["cluster_name"]), f" · {conf:.0f}%")
st.markdown(
    f"""
    <div class='tk-card tk-namecard'>
      <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px'>
        <div>
          <h2>{row['display_name']}</h2>
          <div class='meta'>{row['player.team.name']} · {row['season_label']} ·
          {row['Height']:.0f} cm · {row['gamesPlayed']:.0f} games · {row['minutesPerGame']:.1f} min/g</div>
        </div>
        <div>{badge_html}</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---- Badges ----------------------------------------------------------------- #
st.markdown(badge_chips(badges_for(row)), unsafe_allow_html=True)
st.write("")

# ---- Skill ratings ----------------------------------------------------------- #
st.subheader("Skill ratings")
st.caption("0-100 composites of season percentiles — hover a title in the list below for the recipe.")
rating_cols = st.columns(len(RATINGS) + 1)
for col, name in zip(rating_cols, RATINGS):
    col.markdown(rating_tile(name, row[f"rating_{name}"]), unsafe_allow_html=True)
rating_cols[-1].markdown(rating_tile("Overall", row["rating_Overall"]), unsafe_allow_html=True)
with st.expander("How each rating is built"):
    for name, help_text in RATING_HELP.items():
        st.markdown(f"- **{name}** — {help_text}")

st.write("")

# ---- Radar + percentile bars -------------------------------------------------- #
left, right = st.columns([3, 2])
with left:
    st.subheader("Profile radar")
    fig = radar_chart(
        [(str(row["display_name"]), percentile_values(row), hover_values(row))],
        list(RADAR_FEATURES.values()),
    )
    st.plotly_chart(fig, width="stretch")
with right:
    st.subheader("League percentiles")
    st.markdown(
        "<div class='tk-card'>" + percentile_bars(row, PERCENTILE_PANEL) + "</div>",
        unsafe_allow_html=True,
    )

# ---- Shot diet + archetype membership ----------------------------------------- #
left2, right2 = st.columns([3, 2])
with left2:
    st.subheader("Shot diet")
    st.plotly_chart(shot_profile_chart(row, df), width="stretch")
with right2:
    st.subheader("Archetype membership")
    st.caption("Soft GMM probabilities — players can straddle archetypes.")
    st.markdown(
        "<div class='tk-card'>" + prob_segments(row) + "</div>",
        unsafe_allow_html=True,
    )

st.write("")

# ---- Similar players ------------------------------------------------------------ #
st.subheader("Most similar players")
sim = similar_players(row_idx, n=5)
if sim.empty:
    st.info("No similar players found with the current data.")
else:
    cols = st.columns(5)
    for col, (_, s) in zip(cols, sim.iterrows()):
        with col:
            sim_badge = cluster_badge(str(s["cluster_name"]))
            st.markdown(
                f"""
                <div class='tk-card' style='min-height:150px'>
                  <div style='font-weight:800'>{s['display_name']}</div>
                  <div style='color:#5B6B7B; font-size:.85rem; margin-bottom:6px'>
                    {s['season_label']} · {s['player.team.code']}</div>
                  {sim_badge}
                  <div style='margin-top:8px; font-size:1.2rem; font-weight:800; color:#FF6113'>
                    {s['similarity']:.0f}<span style='font-size:.8rem; color:#5B6B7B'> /100 fit</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Open profile", key=f"sim_{s['player_season']}", width="stretch"):
                go_to_profile(str(s["player_season"]))
