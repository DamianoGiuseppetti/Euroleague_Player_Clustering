"""Shared utilities, design system and components for the EuroLeague scouting dashboard.

v4 — Teamkeys-inspired full rebuild. Light EuroLeague theme (white + #FF6113).
Data, clustering logic and the files under data/processed/ are unchanged —
this module only loads and presents.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"
DATA_PATH = DATA_DIR / "clustered_players.csv"
PERGAME_PATH = DATA_DIR / "player_stats_pergame.csv"

# --------------------------------------------------------------------------- #
# Design system — EuroLeague light theme
# --------------------------------------------------------------------------- #
BRAND = {
    "orange": "#FF6113",       # EuroLeague accent
    "orange_soft": "#FFE9DD",
    "ink": "#0B1626",          # near-black navy text
    "muted": "#5B6B7B",        # secondary text
    "bg": "#FFFFFF",
    "panel": "#F4F6F8",        # card / panel background
    "line": "#E4E9EE",         # borders
    "good": "#17A674",
    "warn": "#E8A93B",
}

CLUSTER_NAMES = {
    0: "Perimeter Shooter",
    1: "Ball Handler",
    2: "Two-Way Forward",
    3: "Rim Protector",
}

# Palette tuned to read on a white background
CLUSTER_COLORS = {
    "Perimeter Shooter": "#2E6FF2",
    "Ball Handler": "#FF6113",
    "Two-Way Forward": "#17A674",
    "Rim Protector": "#8A4FE0",
}

CLUSTER_BLURB = {
    "Perimeter Shooter": "Spacing specialists — high three-point volume, off-ball scoring, low usage of the dribble.",
    "Ball Handler": "Primary creators — high assist and usage rates who run the offense.",
    "Two-Way Forward": "Versatile wings/forwards — balanced scoring, rebounding and defensive activity.",
    "Rim Protector": "Interior bigs — rebounding, blocks and at-rim finishing, tallest profiles.",
}

# Features used by the GMM model (20 variables)
MODEL_FEATURES = [
    "Height",
    "offensiveReboundsPercentage",
    "defensiveReboundsPercentage",
    "assistsRatio",
    "turnoversRatio",
    "blocks",
    "steals",
    "pointsScored",
    "usageProxy",
    "pir",
    "freeThrowsRate",
    "freeThrowsPercentage",
    "fieldGoalsAttempted",
    "twoPointersPercentage",
    "threePointersPercentage",
    "3FGA_Pct",
    "Corner_3FGA_Pct",
    "0_1m_FGA_Pct",
    "1_3.5m_FGA_Pct",
    "3.5m_3pt_FGA_Pct",
]

# Radar axes: percentiles are computed on these READABLE columns (per-game stats),
# so the radius always matches the value shown in the hover popup.
RADAR_FEATURES = {
    "Height": "Height",
    "pointsPerGame": "Scoring",
    "pirPerGame": "PIR",
    "assistsPerGame": "Playmaking",
    "usageProxy": "Usage",
    "reboundsPerGame": "Rebounding",
    "blocksPerGame": "Blocks",
    "3FGA_Pct": "3PT attempt %",
    "0_1m_FGA_Pct": "At-rim attempt %",
}

RADAR_HOVER = {
    "Height": ("Height", "{:.0f} cm"),
    "pointsPerGame": ("pointsPerGame", "{:.1f} pts/game"),
    "pirPerGame": ("pirPerGame", "{:.1f} PIR/game"),
    "assistsPerGame": ("assistsPerGame", "{:.1f} ast/game"),
    "usageProxy": ("usageProxy", "{:.0%} usage"),
    "reboundsPerGame": ("reboundsPerGame", "{:.1f} reb/game"),
    "blocksPerGame": ("blocksPerGame", "{:.1f} blk/game"),
    "3FGA_Pct": ("3FGA_Pct", "{:.0f}% of shots from 3"),
    "0_1m_FGA_Pct": ("0_1m_FGA_Pct", "{:.0f}% of shots at rim"),
}

# Readable per-game stats (joined from player_stats_pergame.csv)
PERGAME_STATS = {
    "gamesPlayed": "Games",
    "minutesPerGame": "Min/g",
    "pointsPerGame": "Pts/g",
    "reboundsPerGame": "Reb/g",
    "assistsPerGame": "Ast/g",
    "stealsPerGame": "Stl/g",
    "blocksPerGame": "Blk/g",
    "turnoversPerGame": "TO/g",
    "pirPerGame": "PIR/g",
    "twoPointersPct": "2PT %",
    "threePointersPct": "3PT %",
    "freeThrowsPct": "FT %",
}

SHOT_PROFILE_STATS = {
    "0_1m_FGA_Pct": "At rim (0-1m)",
    "1_3.5m_FGA_Pct": "Short range (1-3.5m)",
    "3.5m_3pt_FGA_Pct": "Mid range",
    "3FGA_Pct": "Three-pointers",
    "Corner_3FGA_Pct": "Corner threes",
}

# Percentile-bar panel shown on the player profile
PERCENTILE_PANEL = {
    "pointsPerGame": "Scoring",
    "pirPerGame": "PIR",
    "assistsPerGame": "Playmaking",
    "reboundsPerGame": "Rebounding",
    "blocksPerGame": "Blocks",
    "stealsPerGame": "Steals",
    "usageProxy": "Usage",
    "3FGA_Pct": "3PT attempt rate",
    "0_1m_FGA_Pct": "At-rim attempt rate",
    "Height": "Height",
}

PROB_COLS = ["prob_cluster_0", "prob_cluster_1", "prob_cluster_2", "prob_cluster_3"]

# --------------------------------------------------------------------------- #
# Skill ratings (Teamkeys-style 0-100) — percentile composites within season
# --------------------------------------------------------------------------- #
RATINGS = {
    "Scoring": ["pointsPerGame"],
    "Playmaking": ["assistsPerGame", "assistsRatio"],
    "Rebounding": ["reboundsPerGame", "offensiveReboundsPercentage", "defensiveReboundsPercentage"],
    "Defense": ["stealsPerGame", "blocksPerGame"],
    "Shooting": ["twoPointersPct", "threePointersPct", "freeThrowsPct"],
    "Efficiency": ["pirPerGame"],
}

RATING_HELP = {
    "Scoring": "Points per game (season percentile)",
    "Playmaking": "Assists per game + assist ratio",
    "Rebounding": "Rebounds per game + OR% / DR%",
    "Defense": "Steals + blocks per game",
    "Shooting": "2PT / 3PT / FT accuracy",
    "Efficiency": "PIR per game (season percentile)",
}

# Auto-awarded badges: (name, emoji, description, rule on a data row)
BADGES = [
    ("Sniper", "🎯", "Top-20% 3PT accuracy on real volume",
     lambda r: r.get("pct_threePointersPct", 0) >= 80 and r.get("pct_3FGA_Pct", 0) >= 60),
    ("Floor General", "🧠", "Top-12% assists per game",
     lambda r: r.get("pct_assistsPerGame", 0) >= 88),
    ("Glass Cleaner", "🧹", "Top-12% rebounds per game",
     lambda r: r.get("pct_reboundsPerGame", 0) >= 88),
    ("Shot Blocker", "🚫", "Top-12% blocks per game",
     lambda r: r.get("pct_blocksPerGame", 0) >= 88),
    ("Pickpocket", "🖐", "Top-12% steals per game",
     lambda r: r.get("pct_stealsPerGame", 0) >= 88),
    ("Bucket Getter", "🔥", "Top-10% points per game",
     lambda r: r.get("pct_pointsPerGame", 0) >= 90),
    ("Two-Way Engine", "⚙️", "75+ rating on both Scoring and Defense",
     lambda r: r.get("rating_Scoring", 0) >= 75 and r.get("rating_Defense", 0) >= 75),
    ("MVP Caliber", "👑", "Top-5% PIR per game",
     lambda r: r.get("pct_pirPerGame", 0) >= 95),
]


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def season_label(season: int) -> str:
    """2020 -> '2020/21'."""
    return f"{season}/{str(season + 1)[-2:]}"


def _pretty_name(name: str) -> str:
    if "," in name:
        last, first = [p.strip() for p in name.split(",", 1)]
        return f"{first.title()} {last.title()}"
    return name.title()


@st.cache_data
def load_data() -> pd.DataFrame:
    """Clustered players + readable per-game stats + percentiles + ratings + badges."""
    df = pd.read_csv(DATA_PATH)
    pergame = pd.read_csv(PERGAME_PATH).rename(
        columns={
            "twoPointersPercentage": "twoPointersPct",
            "threePointersPercentage": "threePointersPct",
            "freeThrowsPercentage": "freeThrowsPct",
        }
    )
    df = df.merge(
        pergame.drop(columns=["minutesPerGame"]),
        on=["player.name", "season", "player.team.code"],
        how="left",
    )
    df["minutesPerGame"] = df["minutesPlayed"]

    df["cluster_name"] = df["cluster"].map(CLUSTER_NAMES)
    df["season_label"] = df["season"].apply(season_label)
    df["display_name"] = df["player.name"].apply(_pretty_name)
    df["player_season"] = df["display_name"] + " (" + df["season_label"] + ")"

    # League percentile (0-100) of each feature, within each season
    pct_cols = set(RADAR_FEATURES) | set(PERCENTILE_PANEL)
    for comps in RATINGS.values():
        pct_cols |= set(comps)
    for f in pct_cols:
        df[f"pct_{f}"] = df.groupby("season")[f].rank(pct=True) * 100

    # 0-100 skill ratings = mean of component percentiles (skipna)
    for name, comps in RATINGS.items():
        df[f"rating_{name}"] = (
            df[[f"pct_{c}" for c in comps]].mean(axis=1, skipna=True).round(0)
        )
    df["rating_Overall"] = (
        df[[f"rating_{n}" for n in RATINGS]].mean(axis=1, skipna=True).round(0)
    )

    df = df.reset_index(drop=True)
    return df


def badges_for(row: pd.Series) -> list[tuple[str, str, str]]:
    """Badges earned by a player-season: list of (name, emoji, description)."""
    earned = []
    for name, emoji, desc, rule in BADGES:
        try:
            if rule(row.fillna(0)):
                earned.append((name, emoji, desc))
        except (KeyError, TypeError):
            continue
    return earned


@st.cache_data
def compute_pca() -> pd.DataFrame:
    """2D PCA projection of the scaled model features, for the overview scatter."""
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler

    df = load_data()
    X = StandardScaler().fit_transform(df[MODEL_FEATURES])
    coords = PCA(n_components=2, random_state=42).fit_transform(X)
    out = df.copy()
    out["PC1"], out["PC2"] = coords[:, 0], coords[:, 1]
    return out


@st.cache_data
def _scaled_matrix() -> np.ndarray:
    """Z-scored model-feature matrix, row-aligned with load_data()."""
    from sklearn.preprocessing import StandardScaler

    df = load_data()
    return StandardScaler().fit_transform(df[MODEL_FEATURES])


def similar_players(
    target_idx: int,
    n: int = 10,
    same_season_only: bool = False,
    same_cluster_only: bool = False,
    exclude_same_team: bool = False,
    min_minutes: float = 12.0,
) -> pd.DataFrame:
    """Rank player-seasons by similarity to the target row (index into load_data()).

    Similarity = 100 * (1 - d / d_max), where d is Euclidean distance on the
    z-scored model features and d_max is the largest distance in the pool.
    Returns a dataframe with a `similarity` column (0-100), best matches first.
    """
    df = load_data()
    X = _scaled_matrix()
    dist = np.linalg.norm(X - X[target_idx], axis=1)

    pool = df.copy()
    pool["_dist"] = dist
    pool = pool[pool.index != target_idx]
    # Drop other seasons of the same player — a "match" with yourself is trivial
    pool = pool[pool["player.name"] != df.loc[target_idx, "player.name"]]
    pool = pool[pool["minutesPlayed"] >= min_minutes]
    if same_season_only:
        pool = pool[pool["season"] == df.loc[target_idx, "season"]]
    if same_cluster_only:
        pool = pool[pool["cluster"] == df.loc[target_idx, "cluster"]]
    if exclude_same_team:
        pool = pool[
            ~(
                (pool["player.team.code"] == df.loc[target_idx, "player.team.code"])
                & (pool["season"] == df.loc[target_idx, "season"])
            )
        ]

    if pool.empty:
        return pool
    d_max = pool["_dist"].max() or 1.0
    pool["similarity"] = (1 - pool["_dist"] / d_max) * 100
    return pool.sort_values("_dist").head(n)


def percentile_values(row: pd.Series) -> list[float]:
    """Pre-computed league percentiles of `row` for the radar features."""
    return [row[f"pct_{f}"] for f in RADAR_FEATURES]


def hover_values(row: pd.Series) -> list[str]:
    """Readable per-game values for the radar hover of a single player-season."""
    return [fmt.format(row[col]) for col, fmt in RADAR_HOVER.values()]


def mean_hover_values(pool: pd.DataFrame) -> list[str]:
    """Readable average per-game values for a pool of player-seasons (e.g. a cluster)."""
    return [fmt.format(pool[col].mean()) for col, fmt in RADAR_HOVER.values()]


def table_height(n_rows: int) -> int:
    """st.dataframe height that fits `n_rows` exactly (no scrollbar)."""
    return int(35 * (n_rows + 1)) + 3


def go_to_profile(player_season: str) -> None:
    """Jump to the Player Profile page focused on `player_season`."""
    st.session_state["focus_player_season"] = player_season
    st.switch_page("app_pages/player_profile.py")


# --------------------------------------------------------------------------- #
# UI components (HTML/CSS)
# --------------------------------------------------------------------------- #
def inject_css() -> None:
    """Global light styling — call once per page."""
    st.markdown(
        f"""
        <style>
        .stApp {{ background:{BRAND['bg']}; }}
        section[data-testid="stSidebar"] {{ background:{BRAND['panel']}; }}
        .block-container {{ padding-top:2.2rem; max-width:1300px; }}

        .tk-hero {{
            display:flex; align-items:center; gap:14px; margin-bottom:.2rem;
        }}
        .tk-hero .bar {{ width:6px; height:38px; background:{BRAND['orange']};
            border-radius:4px; }}
        .tk-hero h1 {{ font-size:1.9rem; font-weight:800; color:{BRAND['ink']};
            margin:0; line-height:1.1; }}
        .tk-sub {{ color:{BRAND['muted']}; font-size:.95rem; margin:.1rem 0 1rem 20px; }}

        .tk-card {{
            background:{BRAND['bg']}; border:1px solid {BRAND['line']};
            border-radius:14px; padding:18px 20px;
            box-shadow:0 1px 3px rgba(11,22,38,.06);
        }}
        .tk-kpi {{ text-align:left; }}
        .tk-kpi .v {{ font-size:1.9rem; font-weight:800; color:{BRAND['ink']};
            line-height:1; }}
        .tk-kpi .l {{ font-size:.8rem; color:{BRAND['muted']}; text-transform:uppercase;
            letter-spacing:.04em; margin-top:6px; }}

        .tk-badge {{ display:inline-block; padding:5px 14px; border-radius:20px;
            font-weight:700; font-size:.85rem; white-space:nowrap; }}

        .tk-chip {{ display:inline-block; padding:6px 13px; border-radius:20px;
            font-weight:700; font-size:.83rem; margin:3px 6px 3px 0;
            background:{BRAND['orange_soft']}; color:{BRAND['ink']};
            border:1px solid {BRAND['orange']}55; }}

        .tk-rating {{ text-align:center; padding:14px 8px; }}
        .tk-rating .num {{ font-size:2rem; font-weight:800; line-height:1; }}
        .tk-rating .lab {{ font-size:.78rem; color:{BRAND['muted']};
            text-transform:uppercase; letter-spacing:.04em; margin-top:6px; }}

        .tk-pbar-row {{ display:flex; align-items:center; gap:12px; margin:7px 0; }}
        .tk-pbar-lab {{ width:140px; font-size:.85rem; color:{BRAND['ink']};
            text-align:right; flex-shrink:0; }}
        .tk-pbar-track {{ flex:1; height:14px; background:{BRAND['panel']};
            border-radius:8px; position:relative; overflow:hidden; }}
        .tk-pbar-fill {{ height:100%; border-radius:8px; }}
        .tk-pbar-val {{ width:44px; font-size:.82rem; font-weight:700;
            color:{BRAND['ink']}; flex-shrink:0; }}

        .tk-namecard h2 {{ font-size:1.6rem; font-weight:800; color:{BRAND['ink']};
            margin:0; }}
        .tk-namecard .meta {{ color:{BRAND['muted']}; font-size:.95rem; margin-top:2px; }}

        .tk-leader {{ display:flex; justify-content:space-between; align-items:center;
            padding:5px 0; border-bottom:1px solid {BRAND['line']}; font-size:.9rem; }}
        .tk-leader:last-child {{ border-bottom:none; }}
        .tk-leader .nm {{ color:{BRAND['ink']}; font-weight:600; }}
        .tk-leader .vl {{ color:{BRAND['orange']}; font-weight:800; }}
        .tk-leader.first .nm {{ font-size:1rem; }}

        .tk-cmp {{ width:100%; border-collapse:collapse; font-size:.9rem; }}
        .tk-cmp th {{ text-align:center; padding:8px 10px; color:{BRAND['ink']};
            border-bottom:2px solid {BRAND['line']}; font-size:.92rem; }}
        .tk-cmp td {{ text-align:center; padding:7px 10px;
            border-bottom:1px solid {BRAND['line']}; color:{BRAND['ink']}; }}
        .tk-cmp td.lab {{ text-align:right; color:{BRAND['muted']}; font-size:.84rem; }}
        .tk-cmp td.win {{ background:{BRAND['orange_soft']}; font-weight:800;
            color:{BRAND['ink']}; border-radius:6px; }}

        .tk-seg {{ display:flex; height:18px; border-radius:9px; overflow:hidden; }}
        .tk-seg div {{ height:100%; }}
        .tk-seg-leg {{ font-size:.8rem; color:{BRAND['muted']}; margin-top:6px; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str = "") -> None:
    """Page title with the EuroLeague accent bar."""
    st.markdown(
        f"<div class='tk-hero'><div class='bar'></div><h1>{title}</h1></div>",
        unsafe_allow_html=True,
    )
    if subtitle:
        st.markdown(f"<div class='tk-sub'>{subtitle}</div>", unsafe_allow_html=True)


def kpi_tile(value: str, label: str) -> str:
    return (
        f"<div class='tk-card tk-kpi'><div class='v'>{value}</div>"
        f"<div class='l'>{label}</div></div>"
    )


def cluster_badge(cluster_name: str, extra: str = "") -> str:
    """Full-width colored badge for a cluster name (never truncated)."""
    color = CLUSTER_COLORS[cluster_name]
    return (
        f"<span class='tk-badge' style='background:{color}1A; border:1.5px solid {color}; "
        f"color:{color};'>{cluster_name}{extra}</span>"
    )


def rating_color(value: float) -> str:
    """Red -> grey -> green ramp for a 0-100 rating/percentile."""
    if value >= 80:
        return "#17A674"
    if value >= 60:
        return "#5FB87E"
    if value >= 40:
        return "#9AA7B3"
    if value >= 20:
        return "#E8A93B"
    return "#E0613B"


# Kept under its old name for backwards compatibility inside components
_pct_color = rating_color


def rating_tile(label: str, value: float) -> str:
    """Teamkeys-style 0-100 rating tile."""
    if pd.isna(value):
        return (
            "<div class='tk-card tk-rating'><div class='num' style='color:#9AA7B3'>–</div>"
            f"<div class='lab'>{label}</div></div>"
        )
    color = rating_color(value)
    return (
        f"<div class='tk-card tk-rating'><div class='num' style='color:{color}'>"
        f"{value:.0f}</div><div class='lab'>{label}</div></div>"
    )


def badge_chips(earned: list[tuple[str, str, str]]) -> str:
    """Row of badge chips; each chip shows its rule on hover (title attr)."""
    if not earned:
        return "<span style='color:#5B6B7B;font-size:.88rem'>No badges this season</span>"
    chips = [
        f"<span class='tk-chip' title='{desc}'>{emoji} {name}</span>"
        for name, emoji, desc in earned
    ]
    return "<div>" + "".join(chips) + "</div>"


def percentile_bars(row: pd.Series, fields: dict | None = None) -> str:
    """HTML block of horizontal percentile bars for `row`."""
    fields = fields or PERCENTILE_PANEL
    rows = []
    for col, label in fields.items():
        pct = float(row[f"pct_{col}"])
        color = rating_color(pct)
        rows.append(
            f"<div class='tk-pbar-row'>"
            f"<div class='tk-pbar-lab'>{label}</div>"
            f"<div class='tk-pbar-track'>"
            f"<div class='tk-pbar-fill' style='width:{pct:.0f}%; background:{color};'></div>"
            f"</div>"
            f"<div class='tk-pbar-val'>{pct:.0f}</div>"
            f"</div>"
        )
    return "<div>" + "".join(rows) + "</div>"


def leader_list(pool: pd.DataFrame, col: str, fmt: str = "{:.1f}", n: int = 5) -> str:
    """Top-n list for a leaders card (name + value, leader emphasized)."""
    top = pool.nlargest(n, col)
    rows = []
    for i, (_, r) in enumerate(top.iterrows()):
        cls = "tk-leader first" if i == 0 else "tk-leader"
        val = fmt.format(r[col])
        rows.append(
            f"<div class='{cls}'><span class='nm'>{r['display_name']}</span>"
            f"<span class='vl'>{val}</span></div>"
        )
    return "".join(rows)


def prob_segments(row: pd.Series) -> str:
    """Segmented archetype-probability bar (soft cluster membership)."""
    segs, legend = [], []
    for i, col in enumerate(PROB_COLS):
        p = float(row[col]) * 100
        name = CLUSTER_NAMES[i]
        color = CLUSTER_COLORS[name]
        if p >= 0.5:
            segs.append(f"<div style='width:{p:.1f}%; background:{color};' title='{name}: {p:.0f}%'></div>")
        if p >= 5:
            legend.append(
                f"<span style='color:{color}; font-weight:700'>{name} {p:.0f}%</span>"
            )
    return (
        f"<div class='tk-seg'>{''.join(segs)}</div>"
        f"<div class='tk-seg-leg'>{' &nbsp;·&nbsp; '.join(legend)}</div>"
    )


def comparison_matrix(rows: list[pd.Series], stats: dict, higher_is_better: bool = True) -> str:
    """HTML head-to-head table: one column per player, winner cell highlighted."""
    header = "<tr><th></th>" + "".join(
        f"<th>{r['display_name']}<br><span style='font-weight:400;color:#5B6B7B;font-size:.8rem'>"
        f"{r['season_label']} · {r['player.team.code']}</span></th>"
        for r in rows
    ) + "</tr>"

    body = []
    for col, label in stats.items():
        values = [float(r[col]) if pd.notna(r[col]) else np.nan for r in rows]
        valid = [v for v in values if not np.isnan(v)]
        best = (max(valid) if higher_is_better else min(valid)) if valid else np.nan
        fmt = "{:.0f}" if col.startswith("rating_") or col == "gamesPlayed" else "{:.1f}"
        cells = []
        for v in values:
            if np.isnan(v):
                cells.append("<td>–</td>")
            elif valid and v == best and len(valid) > 1:
                cells.append(f"<td class='win'>{fmt.format(v)}</td>")
            else:
                cells.append(f"<td>{fmt.format(v)}</td>")
        body.append(f"<tr><td class='lab'>{label}</td>{''.join(cells)}</tr>")

    return f"<table class='tk-cmp'>{header}{''.join(body)}</table>"


# --------------------------------------------------------------------------- #
# Charts
# --------------------------------------------------------------------------- #
def radar_chart(
    traces: list[tuple[str, list[float], list[str] | None]],
    labels: list[str],
    colors: list[str] | None = None,
    show_baseline: bool = True,
) -> go.Figure:
    """Percentile radar chart (light theme).

    Conventions: dashed flat 50th-percentile baseline; radial axis fully hidden;
    fills/lines hoverinfo=skip with marker-only traces on top so hover works
    under overlapping areas.
    """
    fig = go.Figure()
    closed_labels = labels + labels[:1]

    if show_baseline:
        fig.add_trace(
            go.Scatterpolar(
                r=[50] * len(closed_labels),
                theta=closed_labels,
                name="50th percentile",
                mode="lines",
                line=dict(color="#B7C0CA", dash="dash", width=1.5),
                hoverinfo="skip",
            )
        )

    palette = colors or [BRAND["orange"], "#2E6FF2", "#17A674", "#8A4FE0"]

    for i, (name, values, _hover) in enumerate(traces):
        fig.add_trace(
            go.Scatterpolar(
                r=list(values) + [values[0]],
                theta=closed_labels,
                fill="toself",
                mode="lines",
                name=name,
                line=dict(color=palette[i % len(palette)]),
                opacity=0.55,
                hoverinfo="skip",
            )
        )

    for i, (name, values, hover) in enumerate(traces):
        kwargs = {}
        if hover is not None:
            kwargs["customdata"] = list(hover) + [hover[0]]
            kwargs["hovertemplate"] = "%{theta}: %{customdata}<extra>" + name + "</extra>"
        else:
            kwargs["hovertemplate"] = "%{theta}: %{r:.0f}th pct<extra>" + name + "</extra>"
        fig.add_trace(
            go.Scatterpolar(
                r=list(values) + [values[0]],
                theta=closed_labels,
                mode="markers",
                name=name,
                marker=dict(color=palette[i % len(palette)], size=7),
                showlegend=False,
                **kwargs,
            )
        )

    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                range=[0, 100],
                showline=False,
                linewidth=0,
                ticks="",
                showticklabels=False,
                gridcolor=BRAND["line"],
            ),
            angularaxis=dict(gridcolor=BRAND["line"]),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=BRAND["ink"]),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        margin=dict(t=40, b=40),
        height=460,
    )
    return fig


def shot_profile_chart(row: pd.Series, league: pd.DataFrame) -> go.Figure:
    """Horizontal shot-diet bars: player vs league average of the same season."""
    pool = league[league["season"] == row["season"]]
    labels = list(SHOT_PROFILE_STATS.values())
    player_vals = [float(row[c]) for c in SHOT_PROFILE_STATS]
    league_vals = [float(pool[c].mean()) for c in SHOT_PROFILE_STATS]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=labels, x=league_vals, orientation="h", name="League avg",
            marker_color=BRAND["line"],
            hovertemplate="%{y}: %{x:.0f}% of shots<extra>League avg</extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            y=labels, x=player_vals, orientation="h", name=str(row["display_name"]),
            marker_color=BRAND["orange"],
            hovertemplate="%{y}: %{x:.0f}% of shots<extra></extra>",
        )
    )
    fig.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=BRAND["ink"]),
        xaxis=dict(title="% of field-goal attempts", gridcolor=BRAND["line"]),
        yaxis=dict(autorange="reversed"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=30, b=10, l=10, r=10),
        height=320,
    )
    return fig


def pergame_table_config() -> dict:
    """st.dataframe column_config for the per-game stat columns."""
    cfg = {}
    for col, label in PERGAME_STATS.items():
        fmt = "%.0f" if col == "gamesPlayed" else "%.1f"
        cfg[label] = st.column_config.NumberColumn(format=fmt)
    return cfg
