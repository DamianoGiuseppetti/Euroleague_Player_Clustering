"""Archetypes — the four GMM clusters: overlaid radar, cards, representatives."""

import streamlit as st

from src.dashboard_utils import (
    CLUSTER_BLURB,
    CLUSTER_COLORS,
    RADAR_FEATURES,
    cluster_badge,
    go_to_profile,
    hero,
    inject_css,
    load_data,
    mean_hover_values,
    radar_chart,
)

inject_css()
hero(
    "Archetypes",
    "Four player types from a Gaussian Mixture Model on 20 features (BIC-selected).",
)

df = load_data()

# ---- Overlaid radar of archetype averages ------------------------------------ #
st.subheader("Archetype fingerprints")
st.caption("League-percentile averages of each archetype, all seasons pooled.")

selected = st.multiselect(
    "Archetypes to overlay",
    list(CLUSTER_COLORS),
    default=list(CLUSTER_COLORS),
)

traces, palette = [], []
for name in selected:
    pool = df[df["cluster_name"] == name]
    values = [pool[f"pct_{f}"].mean() for f in RADAR_FEATURES]
    traces.append((name, values, mean_hover_values(pool)))
    palette.append(CLUSTER_COLORS[name])

if traces:
    st.plotly_chart(
        radar_chart(traces, list(RADAR_FEATURES.values()), colors=palette),
        width="stretch",
    )
else:
    st.info("Select at least one archetype.")

st.write("")

# ---- Archetype cards ------------------------------------------------------------ #
st.subheader("The four archetypes")
cols = st.columns(4)
for col, name in zip(cols, CLUSTER_COLORS):
    pool = df[df["cluster_name"] == name]
    reps = pool.nlargest(3, "cluster_prob_max")
    color = CLUSTER_COLORS[name]
    badge = cluster_badge(name)
    rep_rows = "".join(
        f"<div class='tk-leader'><span class='nm'>{r['display_name']}</span>"
        f"<span class='vl' style='color:{color}'>{r['season_label']}</span></div>"
        for _, r in reps.iterrows()
    )
    col.markdown(
        f"""
        <div class='tk-card' style='min-height:300px'>
          {badge}
          <div style='color:#5B6B7B; font-size:.86rem; margin:10px 0 12px; min-height:88px'>
            {CLUSTER_BLURB[name]}</div>
          <div class='tk-kpi'><div class='v' style='color:{color}'>{len(pool)}</div>
            <div class='l'>player-seasons</div></div>
          <div style='margin-top:10px; font-size:.8rem; color:#5B6B7B;
            text-transform:uppercase; letter-spacing:.04em'>Purest examples</div>
          {rep_rows}
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# ---- Explore one archetype ------------------------------------------------------- #
st.subheader("Explore an archetype")
pick = st.selectbox("Archetype", list(CLUSTER_COLORS))
pool = df[df["cluster_name"] == pick].sort_values("cluster_prob_max", ascending=False)
c1, c2 = st.columns([2, 1])
with c1:
    player = st.selectbox(
        "Jump to a member profile",
        [""] + list(pool["player_season"]),
        format_func=lambda v: v or "Pick a player…",
    )
    if player:
        go_to_profile(player)
with c2:
    st.metric("Average membership confidence", f"{pool['cluster_prob_max'].mean() * 100:.0f}%")
