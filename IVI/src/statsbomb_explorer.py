from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd
from statsbombpy import sb

from .utils import classify_build_up


def _xy(value):
    if isinstance(value, (list, tuple)) and len(value) >= 2:
        return value[0], value[1]
    return np.nan, np.nan


def _end_xy(row):
    event_type = row.get("type", "")

    if event_type == "Pass":
        return _xy(row.get("pass_end_location"))
    if event_type == "Carry":
        return _xy(row.get("carry_end_location"))
    if event_type == "Shot":
        return 120, 40

    return np.nan, np.nan


@lru_cache(maxsize=1)
def competitions_df() -> pd.DataFrame:
    df = sb.competitions()
    df = df.sort_values(["competition_name", "season_name"]).reset_index(drop=True)
    return df


def competition_options():
    df = competitions_df()

    options = []
    for _, row in df.iterrows():
        value = f"{int(row['competition_id'])}|{int(row['season_id'])}"
        label = f"{row['competition_name']} - {row['season_name']}"
        options.append({"label": label, "value": value})

    return options


@lru_cache(maxsize=64)
def matches_df(competition_id: int, season_id: int) -> pd.DataFrame:
    df = sb.matches(competition_id=competition_id, season_id=season_id)
    df = df.sort_values(["match_date", "home_team", "away_team"]).reset_index(drop=True)
    return df


def match_options(competition_season_value: str):
    if not competition_season_value:
        return []

    competition_id, season_id = [int(x) for x in competition_season_value.split("|")]
    df = matches_df(competition_id, season_id)

    options = []
    for _, row in df.iterrows():
        stage = row.get("competition_stage", "")
        date = row.get("match_date", "")
        label = f"{row['home_team']} vs {row['away_team']} · {date}"
        if stage:
            label += f" · {stage}"

        options.append({"label": label, "value": int(row["match_id"])})

    return options


def team_options(match_id: int):
    if not match_id:
        return [{"label": "All teams", "value": "ALL"}]

    match_row = None

    for _, comp in competitions_df().iterrows():
        try:
            m = matches_df(int(comp["competition_id"]), int(comp["season_id"]))
            found = m[m["match_id"].astype(int).eq(int(match_id))]
            if not found.empty:
                match_row = found.iloc[0]
                break
        except Exception:
            continue

    if match_row is None:
        return [{"label": "All teams", "value": "ALL"}]

    return [
        {"label": "All teams", "value": "ALL"},
        {"label": match_row["home_team"], "value": match_row["home_team"]},
        {"label": match_row["away_team"], "value": match_row["away_team"]},
    ]


@lru_cache(maxsize=32)
def events_for_match(match_id: int) -> pd.DataFrame:
    events = sb.events(match_id=int(match_id))
    events = events.sort_values("index").reset_index(drop=True)
    return events


def build_match_goal_tables(match_id: int, team_filter: str = "ALL"):
    events = events_for_match(int(match_id)).copy()
    events = events.sort_values("index").reset_index(drop=True)

    if "location" in events.columns:
        events[["x", "y"]] = events["location"].apply(lambda v: pd.Series(_xy(v)))

    end_locations = events.apply(_end_xy, axis=1)
    events["end_x"] = [xy[0] for xy in end_locations]
    events["end_y"] = [xy[1] for xy in end_locations]

    goal_shots = events[
        (events["type"] == "Shot")
        & (events["shot_outcome"] == "Goal")
    ].copy()

    if team_filter and team_filter != "ALL":
        goal_shots = goal_shots[goal_shots["team"].eq(team_filter)]

    goal_rows = []
    event_rows = []

    for goal_number, (_, goal) in enumerate(goal_shots.iterrows(), start=1):
        team = goal["team"]
        possession = goal["possession"]
        build_up_id = f"{int(match_id)}_{goal_number}"

        possession_events = events[
            (events["team"] == team)
            & (events["possession"] == possession)
            & (events["index"] <= goal["index"])
        ].copy().sort_values("index")

        completed_passes = possession_events[
            (possession_events["type"] == "Pass")
            & (
                possession_events["pass_outcome"].isna()
                if "pass_outcome" in possession_events.columns
                else True
            )
        ].copy()

        action_events = possession_events[
            (
                (possession_events["type"] == "Pass")
                & (
                    possession_events["pass_outcome"].isna()
                    if "pass_outcome" in possession_events.columns
                    else True
                )
            )
            | (possession_events["type"] == "Carry")
            | (possession_events["type"] == "Shot")
        ].copy()

        action_events = action_events[action_events["index"] <= goal["index"]].copy()
        action_events = action_events.sort_values("index").reset_index(drop=True)

        passes_before_goal = int(len(completed_passes))

        first_timestamp = action_events.iloc[0]["timestamp"] if not action_events.empty else "00:00:00.000"
        goal_timestamp = goal["timestamp"]

        duration_seconds = _timestamp_to_seconds(goal_timestamp) - _timestamp_to_seconds(first_timestamp)
        duration_seconds = max(0, duration_seconds)

        scorer = goal.get("player", "")
        shot_xg = float(goal.get("shot_statsbomb_xg", 0) or 0)

        goal_rows.append(
            {
                "build_up_id": build_up_id,
                "goal_id": build_up_id,
                "goal_event_id": goal.get("id", build_up_id),
                "match_id": int(match_id),
                "match_name": str(match_id),
                "team": team,
                "opponent": "",
                "scorer": scorer,
                "minute": int(goal.get("minute", 0)),
                "second": int(goal.get("second", 0)),
                "period": int(goal.get("period", 0)),
                "possession": possession,
                "passes_before_goal": passes_before_goal,
                "attack_duration_seconds": duration_seconds,
                "build_up_type": classify_build_up(passes_before_goal),
                "shot_xg": shot_xg,
                "tournament_stage": "",
                "tournament_progress_score": 0,
                "finishing_efficiency": np.nan,
                "match_stage": "",
                "play_pattern": goal.get("play_pattern", ""),
                "start_x": action_events.iloc[0]["x"] if not action_events.empty else np.nan,
                "start_y": action_events.iloc[0]["y"] if not action_events.empty else np.nan,
                "goal_x": goal.get("x", np.nan),
                "goal_y": goal.get("y", np.nan),
                "shot_x": goal.get("x", np.nan),
                "shot_y": goal.get("y", np.nan),
            }
        )

        for order, (_, event) in enumerate(action_events.iterrows(), start=1):
            event_type = event.get("type", "")
            player = event.get("player", "")

            if event_type == "Pass":
                recipient = event.get("pass_recipient", "")
                pass_outcome = "Complete"
                is_completed = True
            else:
                recipient = ""
                pass_outcome = ""
                is_completed = False

            event_rows.append(
                {
                    "build_up_id": build_up_id,
                    "goal_id": build_up_id,
                    "match_id": int(match_id),
                    "match_name": str(match_id),
                    "team": team,
                    "event_order": int(order),
                    "event_index": int(event.get("index", order)),
                    "event_id": event.get("id", f"{build_up_id}_{order}"),
                    "event_type": event_type,
                    "player": player,
                    "recipient": recipient,
                    "pass_recipient": recipient,
                    "minute": int(event.get("minute", 0)),
                    "second": int(event.get("second", 0)),
                    "timestamp_label": f"{int(event.get('minute', 0)):02d}:{int(event.get('second', 0)):02d}",
                    "x": event.get("x", np.nan),
                    "y": event.get("y", np.nan),
                    "end_x": event.get("end_x", np.nan),
                    "end_y": event.get("end_y", np.nan),
                    "pass_outcome": pass_outcome,
                    "outcome": "Goal" if event_type == "Shot" else pass_outcome,
                    "is_completed_pass": is_completed,
                    "is_shot": event_type == "Shot",
                    "is_assist": False,
                    "is_goal": event_type == "Shot",
                }
            )

    goals_df = pd.DataFrame(goal_rows)
    events_df = pd.DataFrame(event_rows)

    if goals_df.empty:
        team_df = pd.DataFrame(columns=["team", "goals", "goals_analysed", "avg_passes_before_goal", "avg_attack_duration"])
    else:
        team_df = (
            goals_df.groupby("team", as_index=False)
            .agg(
                goals=("build_up_id", "nunique"),
                goals_analysed=("build_up_id", "nunique"),
                avg_passes_before_goal=("passes_before_goal", "mean"),
                avg_attack_duration=("attack_duration_seconds", "mean"),
            )
        )
        team_df["shots"] = np.nan
        team_df["finishing_efficiency"] = np.nan
        team_df["tournament_stage"] = ""
        team_df["tournament_progress_score"] = 0

    return goals_df, events_df, team_df


def _timestamp_to_seconds(value):
    try:
        h, m, s = str(value).split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)
    except Exception:
        return 0.0