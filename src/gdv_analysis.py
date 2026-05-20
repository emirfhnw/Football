"""
GDV analysis script for the Football visualization project.

This script creates a cleaned shot dataset and static figures for the
Fundamentals of Data Visualization (GDV) part of the project.

Run from the repository root:
    python src/gdv_analysis.py

Outputs:
    data/processed/shots_prepared.csv
    reports/figures/*.png
"""

from pathlib import Path
import ast
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "shots_single_match.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FIGURE_DIR = PROJECT_ROOT / "reports" / "figures"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", context="notebook")


def parse_location(value):
    """Parse StatsBomb location value safely."""
    if isinstance(value, list) and len(value) >= 2:
        return value
    if isinstance(value, str):
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list) and len(parsed) >= 2:
                return parsed
        except Exception:
            return None
    return None


def chance_quality(xg):
    """Create simple chance quality categories from xG."""
    if pd.isna(xg):
        return "Unknown"
    if xg < 0.05:
        return "Low"
    if xg < 0.20:
        return "Medium"
    return "High"


def prepare_shots(raw_path=RAW_FILE):
    """Load and prepare the shot data."""
    if not raw_path.exists():
        raise FileNotFoundError(f"Missing file: {raw_path}")

    shots = pd.read_csv(raw_path)

    required_cols = [
        "team", "player", "minute", "period", "location",
        "shot_outcome", "shot_statsbomb_xg", "shot_body_part",
        "shot_type", "play_pattern"
    ]
    for col in required_cols:
        if col not in shots.columns:
            shots[col] = np.nan

    shots["location_parsed"] = shots["location"].apply(parse_location)
    shots["x"] = shots["location_parsed"].apply(lambda loc: loc[0] if isinstance(loc, list) else np.nan)
    shots["y"] = shots["location_parsed"].apply(lambda loc: loc[1] if isinstance(loc, list) else np.nan)

    shots["shot_statsbomb_xg"] = pd.to_numeric(shots["shot_statsbomb_xg"], errors="coerce")
    shots["minute"] = pd.to_numeric(shots["minute"], errors="coerce")

    # StatsBomb pitch coordinates use 120x80. Goal centre is approximately (120, 40).
    shots["distance_to_goal"] = np.sqrt((120 - shots["x"]) ** 2 + (40 - shots["y"]) ** 2)
    shots["is_goal"] = shots["shot_outcome"].astype(str).str.lower().eq("goal")
    shots["chance_quality"] = shots["shot_statsbomb_xg"].apply(chance_quality)

    for col in ["team", "player", "shot_outcome", "shot_body_part", "shot_type", "play_pattern", "chance_quality"]:
        shots[col] = shots[col].fillna("Unknown").astype(str)

    shots.to_csv(PROCESSED_DIR / "shots_prepared.csv", index=False)
    return shots


def save_team_summary(shots):
    team_summary = (
        shots.groupby("team")
        .agg(
            shots=("team", "size"),
            goals=("is_goal", "sum"),
            total_xg=("shot_statsbomb_xg", "sum"),
            xg_per_shot=("shot_statsbomb_xg", "mean"),
            avg_distance=("distance_to_goal", "mean"),
        )
        .reset_index()
    )
    team_summary.to_csv(PROCESSED_DIR / "team_summary.csv", index=False)
    return team_summary


def draw_pitch(ax):
    ax.plot([0, 120], [0, 0], color="black", linewidth=1)
    ax.plot([0, 120], [80, 80], color="black", linewidth=1)
    ax.plot([0, 0], [0, 80], color="black", linewidth=1)
    ax.plot([120, 120], [0, 80], color="black", linewidth=1)
    ax.plot([60, 60], [0, 80], color="black", linewidth=1)
    ax.add_patch(plt.Circle((60, 40), 10, fill=False, color="black", linewidth=1))

    # Penalty areas
    ax.plot([0, 18], [18, 18], color="black", linewidth=1)
    ax.plot([18, 18], [18, 62], color="black", linewidth=1)
    ax.plot([18, 0], [62, 62], color="black", linewidth=1)
    ax.plot([120, 102], [18, 18], color="black", linewidth=1)
    ax.plot([102, 102], [18, 62], color="black", linewidth=1)
    ax.plot([102, 120], [62, 62], color="black", linewidth=1)

    # Six-yard boxes
    ax.plot([0, 6], [30, 30], color="black", linewidth=1)
    ax.plot([6, 6], [30, 50], color="black", linewidth=1)
    ax.plot([6, 0], [50, 50], color="black", linewidth=1)
    ax.plot([120, 114], [30, 30], color="black", linewidth=1)
    ax.plot([114, 114], [30, 50], color="black", linewidth=1)
    ax.plot([114, 120], [50, 50], color="black", linewidth=1)

    ax.set_xlim(0, 120)
    ax.set_ylim(80, 0)
    ax.set_aspect("equal")
    ax.axis("off")


def create_figures(shots, team_summary):
    # Figure 1: shots by team
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.barplot(data=team_summary.sort_values("shots", ascending=False), x="team", y="shots", ax=ax)
    ax.set_title("Figure 1: Number of shots by team")
    ax.set_xlabel("Team")
    ax.set_ylabel("Number of shots")
    for container in ax.containers:
        ax.bar_label(container, fmt="%.0f", padding=3)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "fig01_shots_by_team.png", dpi=300, bbox_inches="tight")
    plt.close()

    # Figure 2: xG by team
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.barplot(data=team_summary.sort_values("total_xg", ascending=False), x="team", y="total_xg", ax=ax)
    ax.set_title("Figure 2: Total expected goals (xG) by team")
    ax.set_xlabel("Team")
    ax.set_ylabel("Total xG")
    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", padding=3)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "fig02_total_xg_by_team.png", dpi=300, bbox_inches="tight")
    plt.close()

    # Figure 3: chance quality by team
    fig, ax = plt.subplots(figsize=(8, 5))
    order = ["Low", "Medium", "High"]
    sns.countplot(data=shots, x="chance_quality", hue="team", order=order, ax=ax)
    ax.set_title("Figure 3: Chance quality categories by team")
    ax.set_xlabel("Chance quality based on xG")
    ax.set_ylabel("Number of shots")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "fig03_chance_quality_by_team.png", dpi=300, bbox_inches="tight")
    plt.close()

    # Figure 4: shot map
    fig, ax = plt.subplots(figsize=(10, 6))
    draw_pitch(ax)
    non_goals = shots[~shots["is_goal"]]
    sns.scatterplot(
        data=non_goals,
        x="x", y="y", hue="team", size="shot_statsbomb_xg",
        sizes=(45, 260), alpha=0.75, ax=ax
    )
    goals = shots[shots["is_goal"]]
    ax.scatter(goals["x"], goals["y"], marker="*", s=420, edgecolor="black", linewidth=1.2, label="Goal")
    ax.set_title("Figure 4: Shot map with goals and xG size")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.05), ncol=4)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "fig04_shot_map.png", dpi=300, bbox_inches="tight")
    plt.close()

    # Figure 5: distance vs xG
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(
        data=shots,
        x="distance_to_goal", y="shot_statsbomb_xg",
        hue="team", style="is_goal", size="shot_statsbomb_xg",
        sizes=(50, 300), alpha=0.8, ax=ax
    )
    ax.set_title("Figure 5: Shot distance vs xG")
    ax.set_xlabel("Distance to goal")
    ax.set_ylabel("xG")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "fig05_distance_vs_xg.png", dpi=300, bbox_inches="tight")
    plt.close()

    # Figure 6: shot timeline
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.scatterplot(
        data=shots,
        x="minute", y="team", hue="team", size="shot_statsbomb_xg",
        sizes=(50, 350), alpha=0.75, ax=ax
    )
    goals = shots[shots["is_goal"]]
    ax.scatter(goals["minute"], goals["team"], marker="*", s=400, edgecolor="black", linewidth=1.2, label="Goal")
    ax.axvline(45, linestyle="--", color="gray", alpha=0.6)
    ax.set_title("Figure 6: Shot timeline")
    ax.set_xlabel("Match minute")
    ax.set_ylabel("Team")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "fig06_shot_timeline.png", dpi=300, bbox_inches="tight")
    plt.close()

    # Figure 7: top players by xG
    player_summary = (
        shots.groupby(["player", "team"])
        .agg(shots=("player", "size"), goals=("is_goal", "sum"), total_xg=("shot_statsbomb_xg", "sum"))
        .reset_index()
        .sort_values("total_xg", ascending=False)
        .head(10)
    )
    player_summary.to_csv(PROCESSED_DIR / "player_summary.csv", index=False)
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=player_summary, x="total_xg", y="player", hue="team", dodge=False, ax=ax)
    ax.set_title("Figure 7: Top shooting players by total xG")
    ax.set_xlabel("Total xG")
    ax.set_ylabel("Player")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "fig07_top_players_by_xg.png", dpi=300, bbox_inches="tight")
    plt.close()

    # Figure 8: play pattern
    fig, ax = plt.subplots(figsize=(9, 5))
    play_order = shots["play_pattern"].value_counts().index.tolist()
    sns.countplot(data=shots, y="play_pattern", hue="team", order=play_order, ax=ax)
    ax.set_title("Figure 8: Shot creation by play pattern")
    ax.set_xlabel("Number of shots")
    ax.set_ylabel("Play pattern")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "fig08_play_pattern.png", dpi=300, bbox_inches="tight")
    plt.close()


def main():
    shots = prepare_shots()
    team_summary = save_team_summary(shots)
    create_figures(shots, team_summary)

    print("GDV analysis completed.")
    print(f"Prepared data saved to: {PROCESSED_DIR / 'shots_prepared.csv'}")
    print(f"Figures saved to: {FIGURE_DIR}")
    print("\nTeam summary:")
    print(team_summary)


if __name__ == "__main__":
    main()
