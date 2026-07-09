# EuroLeague Players Cluster Analysis
### Redefining Positions Through Unsupervised Learning

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://euroleagueplayerclustering-lpruwy66gmgpethhjqqy4r.streamlit.app/)

Basketball positions — point guard, center, forward — were designed for a different era. This project asks a simpler question: **what do EuroLeague players actually look like in the data?** Using model-based clustering on five seasons of player stats, we let the numbers define the positions.

Inspired by Kalman & Bosch (2019), *"NBA Lineup Analysis on Clustered Player Tendencies"*.

---

## The Data

The dataset covers **EuroLeague player-seasons from 2020/2021 to 2024/2025** and was assembled from three sources:

- **Player stats** (basic, advanced, per-100 possessions) — collected via the [`euroleague_api`](https://github.com/giasemidis/euroleague_api) Python package
- **Shot zone profiles** — shot-by-shot data aggregated into five spatial zones (corner 3, above-the-break 3, mid-range, short, at-rim) from the same API
- **Player heights** — scraped from Proballers and merged using fuzzy name matching to handle spelling variations across seasons

The three sources were joined on a player-season key, producing **956 player-seasons** across 20 statistical features. After filtering to players averaging ≥ 12 minutes per game (the standard "rotation player" threshold), **856 player-seasons** enter the model.

> Raw data, ingestion scripts, and preprocessing pipelines are intentionally excluded from this repository. Only the cleaned, analysis-ready dataset is included.

---

## Methodology

1. **Filter** — drop players below 12 min/game to avoid unreliable rate stats
2. **Scale** — StandardScaler (z-score) so all 20 variables are on equal footing
3. **K-Means** — run as a baseline; silhouette analysis as expected favours few clusters
4. **GMM** — Gaussian Mixture Model with BIC-based model selection across 4 covariance types and up to 12 components; best model: **4 components, full covariance**
5. **Profile** — box plots of scaled variables per cluster, cluster means table, example players
6. **Soft assignment** — each player gets a probability vector, not just a hard label

---

## Results

The model identifies **four play-style positions**:

| Cluster | Name | N | Defining traits | Example players |
|---------|------|---|-----------------|-----------------|
| 0 | **Perimeter Shooter** | 291 | High 3FGA%, Corner 3FGA%, FGA volume; low paint activity | Will Clyburn (22/23), Nigel Hayes-Davis (23/24), Sasha Vezenkov (21/22), Shavon Shields (21/22), Mario Hezonja (21/22) |
| 1 | **Ball Handler** | 301 | High usage, assist ratio; shortest players, fewest rebounds | Alexey Shved (20/21), Shane Larkin (21/22), Mike James (23/24), Lorenzo Brown (22/23), Vasilije Micic (22/23) |
| 2 | **Two-Way Forward** | 184 | High OReb%, DReb%, block rate, paint FGA%; low 3-point rate | Vladimir Lucic (20/21), John Brown III (21/22), Jaylen Hoard (24/25), Zach Leday (23/24), Jordan Mickey (20/21) |
| 3 | **Rim Protector** | 80 | Dominant at-rim FGA%, elite block rate, zero 3FG attempts | Mathias Lessort (22/23), Georgios Papagiannis (21/22), Jan Vesely (20/21), Walter Tavares (20/21), Kyle Hines (20/21) |

Cluster separation is sharp: **92.9%** of player-seasons have a max cluster probability above 0.9. Only 7 players sit meaningfully between two clusters.

---

## How to Run

```bash
# 1. Clone the repo
git clone https://github.com/DamianoGiuseppetti/Euroleague_Player_Clustering.git
cd Euroleague_Player_Clustering

# 2. Install dependencies
pip install -r requirements.txt

# 3a. Open the notebook
jupyter notebook notebooks/Cluster_Analysis_code.ipynb

# 3b. ...or launch the interactive dashboard
streamlit run streamlit_app.py
```

The notebook is self-contained — just run all cells top to bottom.

---

## Interactive Dashboard

A multipage **Streamlit dashboard** lets you explore the clustering results without touching code:

| Page | What it shows |
|------|---------------|
| 🏀 **League Hub** | Season KPIs, the PCA archetype landscape, league leaders, and quick player search |
| 🪪 **Player Profile** | One-pager scouting card: 0-100 skill ratings, auto-awarded badges, percentile radar, shot diet vs league, GMM soft-assignment, most similar players |
| ⚖️ **Compare** | 2–4 player-seasons head-to-head: winner-highlighted stat matrix + radar overlay |
| 🧭 **Replacement Finder** | Statistical doppelgängers of any player (distance on the 20 z-scored model features), with archetype/season/team filters |
| 📊 **Rankings** | Filterable leaderboards on per-game production or skill ratings |
| 🗺️ **Archetypes** | The four cluster fingerprints: overlaid radars, blurbs, purest examples |
| 🛡️ **Teams** | Roster construction by archetype: minute mix vs league average + full roster table |

Run locally with `streamlit run streamlit_app.py`, or **[try the live app on Streamlit Community Cloud](https://euroleagueplayerclustering-lpruwy66gmgpethhjqqy4r.streamlit.app/)**.

---

## Repository Structure

```
├── streamlit_app.py                  # Dashboard entry point (navigation)
├── .streamlit/
│   └── config.toml                   # Light EuroLeague theme
├── app_pages/                        # Dashboard pages
│   ├── home.py                       # League Hub
│   ├── player_profile.py
│   ├── compare.py
│   ├── replacement_finder.py
│   ├── rankings.py
│   ├── archetypes.py
│   └── teams.py
├── src/
│   └── dashboard_utils.py            # Design system, ratings, badges, charts, similarity
├── notebooks/
│   └── Cluster_Analysis_code.ipynb   # Main analysis
├── data/
│   └── processed/
│       ├── final_dataset_2020_2024.csv   # Model input (856 player-seasons, 20 features)
│       ├── clustered_players.csv         # Model output with cluster assignments
│       └── player_stats_pergame.csv      # Readable per-game stats for the dashboard
├── requirements.txt
└── README.md
```
