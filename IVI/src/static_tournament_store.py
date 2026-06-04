from __future__ import annotations

from pathlib import Path
import pickle
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_DIR / "data" / "processed" / "statsbomb_tournament_goal_buildups.pkl"


def _empty_data():
    return {
        "competitions": pd.DataFrame(columns=["label", "value"]),
        "goals": pd.DataFrame(),
        "events": pd.DataFrame(),
        "teams": pd.DataFrame(),
        "matches": pd.DataFrame(),
    }


def load_static_data():
    if not DATA_FILE.exists():
        return _empty_data()

    with open(DATA_FILE, "rb") as f:
        return pickle.load(f)


def competition_options_from_static(data=None):
    data = data or load_static_data()
    comps = data.get("competitions", pd.DataFrame())

    if comps.empty:
        return []

    return [
        {"label": row["label"], "value": row["value"]}
        for _, row in comps.sort_values("label").iterrows()
    ]


def match_options_from_static(competition_value):
    if not competition_value:
        return []

    return [
        {
            "label": "All matches in this tournament",
            "value": competition_value,
        }
    ]


def tournament_slice(competition_value, data=None):
    data = data or load_static_data()

    goals = data.get("goals", pd.DataFrame())
    events = data.get("events", pd.DataFrame())
    teams = data.get("teams", pd.DataFrame())
    matches = data.get("matches", pd.DataFrame())

    if not competition_value:
        return (
            goals.iloc[0:0].copy() if not goals.empty else pd.DataFrame(),
            events.iloc[0:0].copy() if not events.empty else pd.DataFrame(),
            teams.iloc[0:0].copy() if not teams.empty else pd.DataFrame(),
            matches.iloc[0:0].copy() if not matches.empty else pd.DataFrame(),
        )

    if not goals.empty and "competition_value" in goals.columns:
        goals = goals[goals["competition_value"].astype(str).eq(str(competition_value))].copy()
    if not events.empty and "competition_value" in events.columns:
        events = events[events["competition_value"].astype(str).eq(str(competition_value))].copy()
    if not teams.empty and "competition_value" in teams.columns:
        teams = teams[teams["competition_value"].astype(str).eq(str(competition_value))].copy()
    if not matches.empty and "competition_value" in matches.columns:
        matches = matches[matches["competition_value"].astype(str).eq(str(competition_value))].copy()

    return goals, events, teams, matches


def team_tournament_summary_static(competition_value, team_name, data=None):
    data = data or load_static_data()
    goals, _events, _teams, matches = tournament_slice(competition_value, data)

    if not team_name:
        return {
            "team": "All teams",
            "matches": [],
            "formation": "Select a team",
            "summary": "Select one team to see tournament information.",
        }

    match_rows = []
    formations = []

    if not matches.empty:
        team_matches = matches[
            (matches["home_team"].astype(str).eq(str(team_name)))
            | (matches["away_team"].astype(str).eq(str(team_name)))
        ].copy()

        for _, match in team_matches.sort_values("match_date").iterrows():
            home = str(match.get("home_team", ""))
            away = str(match.get("away_team", ""))
            home_score = match.get("home_score", "")
            away_score = match.get("away_score", "")

            match_rows.append(
                {
                    "date": match.get("match_date", ""),
                    "stage": match.get("competition_stage", ""),
                    "match": f"{home} vs {away}",
                    "result": f"{home_score}:{away_score}",
                }
            )

    # Formation is often not available in the simplified event cache.
    formation = "Not available in cached event data"

    return {
        "team": team_name,
        "matches": match_rows,
        "formation": formation,
        "summary": f"{team_name} played {len(match_rows)} matches in this selected tournament.",
    }
