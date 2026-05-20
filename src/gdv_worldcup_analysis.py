"""
Create GDV figures for the FIFA World Cup 2022 Shot Quality Explorer.

This script uses the processed dataset from:
    data/processed/world_cup_2022_shots.csv
    data/processed/world_cup_2022_team_summary.csv

Run from repository root:
    python src/gdv_worldcup_analysis.py

Outputs:
    reports/figures/gdv_*.png
    reports/gdv_insights.md
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FIGURE_DIR = PROJECT_ROOT / "reports" / "figures"
REPORTS_DIR = PROJECT_ROOT / "reports"

FIGURE_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

SHOTS_FILE = PROCESSED_DIR / "world_cup_2022_shots.csv"
TEAM_SUMMARY_FILE = PROCESSED_DIR / "world_cup_2022_team_summary.csv"
INSIGHTS_FILE = REPORTS_DIR / "gdv_insights.md"

sns.set_theme(style="whitegrid", context="notebook")


def load_data():
    """Load prepared shot data and team summary."""
    if not SHOTS_FILE.exists():
        raise FileNotFoundError(
            f"Missing {SHOTS_FILE}. Run first: python src/build_worldcup_shots.py"
        )
    if not TEAM_SUMMARY_FILE.exists():
        raise FileNotFoundError(
            f"Missing {TEAM_SUMMARY_FILE}. Run first: python src/build_worldcup_shots.py"
        )

    shots = pd.read_csv(SHOTS_FILE)
    team_summary = pd.read_csv(TEAM_SUMMARY_FILE)

    # Ensure boolean column works correctly after CSV load
    if shots["is_goal"].dtype != bool:
        shots["is_goal"] = shots["is_goal"].astype(str).str.lower().eq("true")

    return shots, team_summary


def draw_pitch(ax):
    """Draw simple StatsBomb 120x80 football pitch."""
    line_color = "black"
    lw = 1

    # Outer lines
    ax.plot([0, 120], [0, 0], color=line_color, linewidth=lw)
    ax.plot([0, 120], [80, 80], color=line_color, linewidth=lw)
    ax.plot([0, 0], [0, 80], color=line_color, linewidth=lw)
    ax.plot([120, 120], [0, 80], color=line_color, linewidth=lw)

    # Halfway line and centre circle
    ax.plot([60, 60], [0, 80], color=line_color, linewidth=lw)
    ax.add_patch(plt.Circle((60, 40), 10, fill=False, color=line_color, linewidth=lw))

    # Penalty areas
    ax.plot([0, 18], [18, 18], color=line_color, linewidth=lw)
    ax.plot([18, 18], [18, 62], color=line_color, linewidth=lw)
    ax.plot([18, 0], [62, 62], color=line_color, linewidth=lw)
    ax.plot([120, 102], [18, 18], color=line_color, linewidth=lw)
    ax.plot([102, 102], [18, 62], color=line_color, linewidth=lw)
    ax.plot([102, 120], [62, 62], color=line_color, linewidth=lw)

    # Six-yard boxes
    ax.plot([0, 6], [30, 30], color=line_color, linewidth=lw)
    ax.plot([6, 6], [30, 50], color=line_color, linewidth=lw)
    ax.plot([6, 0], [50, 50], color=line_color, linewidth=lw)
    ax.plot([120, 114], [30, 30], color=line_color, linewidth=lw)
    ax.plot([114, 114], [30, 50], color=line_color, linewidth=lw)
    ax.plot([114, 120], [50, 50], color=line_color, linewidth=lw)

    ax.set_xlim(0, 120)
    ax.set_ylim(80, 0)
    ax.set_aspect("equal")
    ax.axis("off")


def fig01_top_teams_by_shots(team_summary):
    data = team_summary.sort_values("shots", ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=data, y="team", x="shots", ax=ax)
    ax.set_title("Figure 1: Top 10 teams by number of shots")
    ax.set_xlabel("Number of shots")
    ax.set_ylabel("Team")
    for container in ax.containers:
        ax.bar_label(container, fmt="%.0f", padding=3)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "gdv_fig01_top_teams_by_shots.png", dpi=300, bbox_inches="tight")
    plt.close()


def fig02_top_teams_by_xg(team_summary):
    data = team_summary.sort_values("total_xg", ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=data, y="team", x="total_xg", ax=ax)
    ax.set_title("Figure 2: Top 10 teams by total expected goals (xG)")
    ax.set_xlabel("Total xG")
    ax.set_ylabel("Team")
    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", padding=3)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "gdv_fig02_top_teams_by_xg.png", dpi=300, bbox_inches="tight")
    plt.close()


def fig03_goals_vs_xg(team_summary):
    # Show teams with highest total xG to keep the figure readable.
    data = team_summary.sort_values("total_xg", ascending=False).head(16).copy()
    data = data.sort_values("total_xg")

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(data["total_xg"], data["team"], label="xG", s=80)
    ax.scatter(data["goals"], data["team"], label="Goals", s=80, marker="X")

    for _, row in data.iterrows():
        ax.plot([row["total_xg"], row["goals"]], [row["team"], row["team"]], color="gray", alpha=0.5)

    ax.set_title("Figure 3: Goals compared with expected goals")
    ax.set_xlabel("Goals / xG")
    ax.set_ylabel("Team")
    ax.legend()
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "gdv_fig03_goals_vs_xg.png", dpi=300, bbox_inches="tight")
    plt.close()


def fig04_chance_quality_by_team(shots, team_summary):
    top_teams = team_summary.sort_values("total_xg", ascending=False).head(10)["team"]
    data = shots[shots["team"].isin(top_teams)].copy()
    order = ["Low", "Medium", "High"]

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.countplot(data=data, y="team", hue="chance_quality", hue_order=order, ax=ax)
    ax.set_title("Figure 4: Chance quality categories for top xG teams")
    ax.set_xlabel("Number of shots")
    ax.set_ylabel("Team")
    ax.legend(title="Chance quality")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "gdv_fig04_chance_quality_by_team.png", dpi=300, bbox_inches="tight")
    plt.close()


def fig05_shot_map_all(shots):
    # Keep all shots but emphasize high-quality chances and goals.
    fig, ax = plt.subplots(figsize=(11, 7))
    draw_pitch(ax)

    low_medium = shots[~shots["chance_quality"].eq("High") & ~shots["is_goal"]].copy()
    high = shots[shots["chance_quality"].eq("High") & ~shots["is_goal"]].copy()
    goals = shots[shots["is_goal"]].copy()

    ax.scatter(low_medium["x"], low_medium["y"], s=18, alpha=0.25, label="Low/Medium chance")
    ax.scatter(high["x"], high["y"], s=80, alpha=0.7, label="High-quality chance")
    ax.scatter(goals["x"], goals["y"], marker="*", s=170, edgecolor="black", linewidth=0.7, label="Goal")

    ax.set_title("Figure 5: Shot map of all World Cup 2022 shots")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.04), ncol=3)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "gdv_fig05_shot_map_all.png", dpi=300, bbox_inches="tight")
    plt.close()


def fig06_distance_vs_xg(shots):
    data = shots.dropna(subset=["distance_to_goal", "shot_statsbomb_xg"]).copy()
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.scatterplot(
        data=data,
        x="distance_to_goal",
        y="shot_statsbomb_xg",
        hue="chance_quality",
        style="is_goal",
        alpha=0.75,
        ax=ax,
    )
    ax.set_title("Figure 6: Relationship between shot distance and xG")
    ax.set_xlabel("Distance to goal")
    ax.set_ylabel("xG")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "gdv_fig06_distance_vs_xg.png", dpi=300, bbox_inches="tight")
    plt.close()


def fig07_top_players_by_xg(shots):
    player_summary = (
        shots.groupby(["player", "team"])
        .agg(
            shots=("player", "size"),
            goals=("is_goal", "sum"),
            total_xg=("shot_statsbomb_xg", "sum"),
        )
        .reset_index()
        .sort_values("total_xg", ascending=False)
        .head(12)
    )

    fig, ax = plt.subplots(figsize=(9, 6))
    sns.barplot(data=player_summary, y="player", x="total_xg", hue="team", dodge=False, ax=ax)
    ax.set_title("Figure 7: Top players by total xG")
    ax.set_xlabel("Total xG")
    ax.set_ylabel("Player")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "gdv_fig07_top_players_by_xg.png", dpi=300, bbox_inches="tight")
    plt.close()

    player_summary.to_csv(PROCESSED_DIR / "world_cup_2022_player_summary.csv", index=False)


def fig08_case_study_serbia_switzerland(shots):
    data = shots[shots["match_label"].eq("Serbia vs Switzerland")].copy()
    if data.empty:
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: shot map
    draw_pitch(axes[0])
    non_goals = data[~data["is_goal"]]
    goals = data[data["is_goal"]]
    sns.scatterplot(data=non_goals, x="x", y="y", hue="team", size="shot_statsbomb_xg", sizes=(50, 250), alpha=0.75, ax=axes[0])
    axes[0].scatter(goals["x"], goals["y"], marker="*", s=350, edgecolor="black", linewidth=1.0, label="Goal")
    axes[0].set_title("Case study: Serbia vs Switzerland shot map")

    # Right: timeline
    sns.scatterplot(data=data, x="minute", y="team", hue="team", size="shot_statsbomb_xg", sizes=(50, 300), alpha=0.75, ax=axes[1])
    axes[1].scatter(goals["minute"], goals["team"], marker="*", s=350, edgecolor="black", linewidth=1.0, label="Goal")
    axes[1].axvline(45, linestyle="--", color="gray", alpha=0.6)
    axes[1].set_title("Case study: Serbia vs Switzerland shot timeline")
    axes[1].set_xlabel("Match minute")
    axes[1].set_ylabel("Team")

    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "gdv_fig08_case_study_serbia_switzerland.png", dpi=300, bbox_inches="tight")
    plt.close()


def write_insights(shots, team_summary):
    top_xg_team = team_summary.sort_values("total_xg", ascending=False).iloc[0]
    top_shots_team = team_summary.sort_values("shots", ascending=False).iloc[0]
    most_efficient = team_summary[team_summary["shots"] >= 10].sort_values("conversion_rate", ascending=False).iloc[0]

    text = f"""# GDV Insights – FIFA World Cup 2022 Shot Quality Explorer

## Research question

How do shot quality, shot locations and finishing efficiency differ between teams and matches in the FIFA World Cup 2022?

## Dataset overview

- Matches: {shots['match_id'].nunique()}
- Teams: {shots['team'].nunique()}
- Shots: {len(shots)}
- Goals: {int(shots['is_goal'].sum())}

## Key insights

1. **Shot volume and chance quality are not the same.**  
   {top_shots_team['team']} had the highest shot volume with {int(top_shots_team['shots'])} shots, while {top_xg_team['team']} had the highest total xG with {top_xg_team['total_xg']:.2f}.

2. **xG helps interpret chance quality.**  
   Instead of only counting shots, xG shows whether shots were likely to become goals.

3. **Shot location matters.**  
   The shot map shows that high-quality chances are usually closer to goal and more central.

4. **Finishing efficiency differs between teams.**  
   Among teams with at least 10 shots, {most_efficient['team']} had the highest conversion rate at {most_efficient['conversion_rate']:.2%}.

5. **The Serbia vs Switzerland case study connects the tournament overview to one concrete match.**  
   This makes the analysis easier to understand and prepares the same dataset for the later IVI dashboard.

## Figures created

- Figure 1: Top 10 teams by number of shots
- Figure 2: Top 10 teams by total xG
- Figure 3: Goals compared with xG
- Figure 4: Chance quality categories by team
- Figure 5: Shot map of all World Cup shots
- Figure 6: Distance to goal vs xG
- Figure 7: Top players by total xG
- Figure 8: Serbia vs Switzerland case study
"""
    INSIGHTS_FILE.write_text(text, encoding="utf-8")


def main():
    shots, team_summary = load_data()

    fig01_top_teams_by_shots(team_summary)
    fig02_top_teams_by_xg(team_summary)
    fig03_goals_vs_xg(team_summary)
    fig04_chance_quality_by_team(shots, team_summary)
    fig05_shot_map_all(shots)
    fig06_distance_vs_xg(shots)
    fig07_top_players_by_xg(shots)
    fig08_case_study_serbia_switzerland(shots)
    write_insights(shots, team_summary)

    print("GDV figures completed.")
    print(f"Figures saved to: {FIGURE_DIR}")
    print(f"Insights saved to: {INSIGHTS_FILE}")


if __name__ == "__main__":
    main()
