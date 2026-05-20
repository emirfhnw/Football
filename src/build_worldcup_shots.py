"""
Build the processed FIFA World Cup 2022 shot dataset.

This is the shared data preparation step for GDV and IVI.

Run from repository root:
    python src/build_worldcup_shots.py

Outputs:
    data/processed/world_cup_2022_shots.csv
    data/processed/world_cup_2022_team_summary.csv
"""

from pathlib import Path
import ast
import time
import warnings

import numpy as np
import pandas as pd
from statsbombpy import sb

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_SHOTS = PROCESSED_DIR / "world_cup_2022_shots.csv"
OUTPUT_TEAM_SUMMARY = PROCESSED_DIR / "world_cup_2022_team_summary.csv"

# StatsBomb IDs for FIFA World Cup 2022
COMPETITION_ID = 43
SEASON_ID = 106


def parse_location(value):
    """Parse StatsBomb location values safely."""
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


def prepare_shots(shots: pd.DataFrame) -> pd.DataFrame:
    """Clean shot data and derive useful analysis variables."""
    required_cols = [
        "team", "player", "minute", "second", "period", "location",
        "shot_outcome", "shot_statsbomb_xg", "shot_body_part",
        "shot_type", "play_pattern", "match_id", "timestamp"
    ]
    for col in required_cols:
        if col not in shots.columns:
            shots[col] = np.nan

    shots = shots.copy()

    shots["location_parsed"] = shots["location"].apply(parse_location)
    shots["x"] = shots["location_parsed"].apply(lambda loc: loc[0] if isinstance(loc, list) else np.nan)
    shots["y"] = shots["location_parsed"].apply(lambda loc: loc[1] if isinstance(loc, list) else np.nan)

    shots["shot_statsbomb_xg"] = pd.to_numeric(shots["shot_statsbomb_xg"], errors="coerce")
    shots["minute"] = pd.to_numeric(shots["minute"], errors="coerce")
    shots["second"] = pd.to_numeric(shots["second"], errors="coerce")

    # StatsBomb pitch dimensions are 120x80. Goal centre is approximately (120, 40).
    shots["distance_to_goal"] = np.sqrt((120 - shots["x"]) ** 2 + (40 - shots["y"]) ** 2)
    shots["is_goal"] = shots["shot_outcome"].astype(str).str.lower().eq("goal")
    shots["chance_quality"] = shots["shot_statsbomb_xg"].apply(chance_quality)

    # These fields are used in plots and later in the IVI dashboard.
    keep_cols = [
        "match_id", "match_date", "match_label", "home_team", "away_team",
        "home_score", "away_score", "competition_stage", "match_week",
        "team", "player", "minute", "second", "period", "timestamp",
        "x", "y", "distance_to_goal", "shot_statsbomb_xg", "chance_quality",
        "shot_outcome", "is_goal", "shot_body_part", "shot_type", "play_pattern"
    ]

    for col in keep_cols:
        if col not in shots.columns:
            shots[col] = np.nan

    cleaned = shots[keep_cols].copy()

    for col in [
        "team", "player", "shot_outcome", "shot_body_part", "shot_type",
        "play_pattern", "chance_quality", "match_label", "competition_stage"
    ]:
        cleaned[col] = cleaned[col].fillna("Unknown").astype(str)

    return cleaned


def build_world_cup_shots() -> pd.DataFrame:
    """Download all FIFA World Cup 2022 matches and collect all shot events."""
    print("Loading FIFA World Cup 2022 matches from StatsBomb Open Data...")
    matches = sb.matches(competition_id=COMPETITION_ID, season_id=SEASON_ID).copy()

    all_shots = []
    total_matches = len(matches)

    for idx, match in matches.reset_index(drop=True).iterrows():
        match_id = int(match["match_id"])
        home_team = match["home_team"]
        away_team = match["away_team"]
        match_label = f"{home_team} vs {away_team}"

        print(f"[{idx + 1}/{total_matches}] {match_label} ({match_id})")

        try:
            events = sb.events(match_id=match_id)
            shots = events[events["type"] == "Shot"].copy()

            if shots.empty:
                continue

            shots["match_date"] = match.get("match_date")
            shots["home_team"] = home_team
            shots["away_team"] = away_team
            shots["home_score"] = match.get("home_score")
            shots["away_score"] = match.get("away_score")
            shots["match_label"] = match_label
            shots["competition_stage"] = match.get("competition_stage")
            shots["match_week"] = match.get("match_week")

            all_shots.append(shots)
            time.sleep(0.1)

        except Exception as exc:
            print(f"Could not load match {match_id}: {exc}")

    if not all_shots:
        raise RuntimeError("No shot data could be loaded.")

    all_shots_df = pd.concat(all_shots, ignore_index=True)
    return prepare_shots(all_shots_df)


def create_team_summary(shots: pd.DataFrame) -> pd.DataFrame:
    """Create team-level summary metrics."""
    summary = (
        shots.groupby("team")
        .agg(
            matches=("match_id", "nunique"),
            shots=("team", "size"),
            goals=("is_goal", "sum"),
            total_xg=("shot_statsbomb_xg", "sum"),
            xg_per_shot=("shot_statsbomb_xg", "mean"),
            avg_distance=("distance_to_goal", "mean"),
        )
        .reset_index()
    )

    summary["conversion_rate"] = summary["goals"] / summary["shots"]
    summary["goals_minus_xg"] = summary["goals"] - summary["total_xg"]

    numeric_cols = ["total_xg", "xg_per_shot", "avg_distance", "conversion_rate", "goals_minus_xg"]
    for col in numeric_cols:
        summary[col] = summary[col].round(3)

    return summary.sort_values("total_xg", ascending=False)


def main():
    shots = build_world_cup_shots()
    team_summary = create_team_summary(shots)

    shots.to_csv(OUTPUT_SHOTS, index=False)
    team_summary.to_csv(OUTPUT_TEAM_SUMMARY, index=False)

    print("\nDone.")
    print(f"Saved shot dataset to: {OUTPUT_SHOTS}")
    print(f"Saved team summary to: {OUTPUT_TEAM_SUMMARY}")
    print("\nDataset overview:")
    print(f"Matches: {shots['match_id'].nunique()}")
    print(f"Teams: {shots['team'].nunique()}")
    print(f"Shots: {len(shots)}")
    print(f"Goals: {int(shots['is_goal'].sum())}")
    print("\nTop 10 teams by total xG:")
    print(team_summary.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
