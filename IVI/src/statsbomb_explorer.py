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


def parse_match_value(match_value: str):
    competition_id, season_id, match_token = str(match_value).split("|")
    return int(competition_id), int(season_id), match_token


@lru_cache(maxsize=1)
def competitions_df() -> pd.DataFrame:
    df = sb.competitions()
    df = df.sort_values(["competition_name", "season_name"]).reset_index(drop=True)
    return df


def competition_options():
    df = competitions_df().copy()
    patterns = ["World Cup", "Euro", "European Championship", "Copa America", "Africa Cup"]
    mask = False
    for pattern in patterns:
        mask = mask | df["competition_name"].astype(str).str.contains(pattern, case=False, na=False)
    filtered = df[mask].copy()
    if filtered.empty:
        filtered = df.copy()

    options = []
    for _, row in filtered.iterrows():
        value = f"{int(row['competition_id'])}|{int(row['season_id'])}"
        label = f"{row['competition_name']} - {row['season_name']}"
        options.append({"label": label, "value": value})
    return options


@lru_cache(maxsize=64)
def matches_df(competition_id: int, season_id: int) -> pd.DataFrame:
    df = sb.matches(competition_id=int(competition_id), season_id=int(season_id))
    df = df.sort_values(["match_date", "home_team", "away_team"]).reset_index(drop=True)
    return df


def match_options(competition_season_value: str):
    if not competition_season_value:
        return []
    competition_id, season_id = [int(x) for x in str(competition_season_value).split("|")]
    df = matches_df(competition_id, season_id)

    options = [{"label": "All matches in this tournament", "value": f"{competition_id}|{season_id}|ALL"}]
    for _, row in df.iterrows():
        stage = row.get("competition_stage", "")
        date = row.get("match_date", "")
        match_id = int(row["match_id"])
        label = f"{row['home_team']} vs {row['away_team']} · {date}"
        if stage:
            label += f" · {stage}"
        value = f"{competition_id}|{season_id}|{match_id}"
        options.append({"label": label, "value": value})
    return options


def team_options(match_value: str):
    if not match_value:
        return [{"label": "All teams", "value": "ALL"}]
    try:
        competition_id, season_id, match_token = parse_match_value(match_value)
    except Exception:
        return [{"label": "All teams", "value": "ALL"}]

    matches = matches_df(competition_id, season_id)
    if str(match_token) == "ALL":
        teams = sorted(
            set(matches["home_team"].dropna().astype(str)).union(set(matches["away_team"].dropna().astype(str)))
        )
        return [{"label": "All teams", "value": "ALL"}] + [{"label": team, "value": team} for team in teams]

    found = matches[matches["match_id"].astype(int).eq(int(match_token))]
    if found.empty:
        return [{"label": "All teams", "value": "ALL"}]
    row = found.iloc[0]
    return [
        {"label": "All teams", "value": "ALL"},
        {"label": row["home_team"], "value": row["home_team"]},
        {"label": row["away_team"], "value": row["away_team"]},
    ]


@lru_cache(maxsize=128)
def events_for_match(match_id: int) -> pd.DataFrame:
    events = sb.events(match_id=int(match_id))
    events = events.sort_values("index").reset_index(drop=True)
    return events


def build_match_goal_tables(match_value: str, team_filter: str = "ALL"):
    competition_id, season_id, match_token = parse_match_value(match_value)

    if str(match_token) == "ALL":
        matches = matches_df(competition_id, season_id)
        all_goals, all_events = [], []

        for _, match in matches.iterrows():
            if team_filter and team_filter != "ALL" and team_filter not in {match["home_team"], match["away_team"]}:
                continue
            goals_df, events_df, _ = _build_single_match_goal_tables(
                match_id=int(match["match_id"]),
                team_filter=team_filter,
                home_team=match["home_team"],
                away_team=match["away_team"],
                match_date=match.get("match_date", ""),
                stage=match.get("competition_stage", ""),
            )
            if not goals_df.empty:
                all_goals.append(goals_df)
            if not events_df.empty:
                all_events.append(events_df)

        goals_df = pd.concat(all_goals, ignore_index=True) if all_goals else _empty_goals_df()
        events_df = pd.concat(all_events, ignore_index=True) if all_events else _empty_events_df()
        team_df = _team_summary(goals_df)
        return goals_df, events_df, team_df

    return _build_single_match_goal_tables(match_id=int(match_token), team_filter=team_filter)


def _build_single_match_goal_tables(match_id: int, team_filter: str = "ALL", home_team: str = "", away_team: str = "", match_date: str = "", stage: str = ""):
    events = events_for_match(int(match_id)).copy()
    events = events.sort_values("index").reset_index(drop=True)

    if "location" in events.columns:
        events[["x", "y"]] = events["location"].apply(lambda v: pd.Series(_xy(v)))
    else:
        events["x"] = np.nan
        events["y"] = np.nan

    end_locations = events.apply(_end_xy, axis=1)
    events["end_x"] = [xy[0] for xy in end_locations]
    events["end_y"] = [xy[1] for xy in end_locations]

    if "shot_outcome" not in events.columns:
        goal_shots = events.iloc[0:0].copy()
    else:
        goal_shots = events[
            (events["type"].astype(str).str.lower() == "shot")
            & (events["shot_outcome"].astype(str).str.lower() == "goal")
        ].copy()

    if team_filter and team_filter != "ALL":
        goal_shots = goal_shots[goal_shots["team"].eq(team_filter)]

    goal_rows, event_rows = [], []

    for goal_number, (_, goal) in enumerate(goal_shots.iterrows(), start=1):
        team = goal["team"]
        opponent = away_team if team == home_team else home_team
        possession = goal["possession"]
        build_up_id = f"{int(match_id)}_{goal_number}"

        possession_events = events[
            (events["team"] == team)
            & (events["possession"] == possession)
            & (events["index"] <= goal["index"])
        ].copy().sort_values("index")

        if "pass_outcome" in possession_events.columns:
            completed_pass_mask = possession_events["pass_outcome"].isna()
        else:
            completed_pass_mask = pd.Series(True, index=possession_events.index)

        completed_passes = possession_events[(possession_events["type"] == "Pass") & completed_pass_mask].copy()

        action_events = possession_events[
            ((possession_events["type"] == "Pass") & completed_pass_mask)
            | (possession_events["type"] == "Carry")
            | (possession_events["type"] == "Shot")
        ].copy()
        action_events = action_events[action_events["index"] <= goal["index"]].copy()
        action_events = action_events.sort_values("index").reset_index(drop=True)

        passes_before_goal = int(len(completed_passes))
        first_timestamp = action_events.iloc[0]["timestamp"] if not action_events.empty else "00:00:00.000"
        duration_seconds = max(0, _timestamp_to_seconds(goal["timestamp"]) - _timestamp_to_seconds(first_timestamp))

        scorer = goal.get("player", "")
        shot_xg = float(goal.get("shot_statsbomb_xg", 0) or 0)
        minute = int(goal.get("minute", 0))
        second = int(goal.get("second", 0))
        goal_label = f"{team} - {scorer} ({minute}')"
        if opponent:
            goal_label += f" vs {opponent}"

        goal_rows.append(
            {
                "build_up_id": build_up_id,
                "goal_id": build_up_id,
                "goal_event_id": goal.get("id", build_up_id),
                "goal_label": goal_label,
                "match_id": int(match_id),
                "match_name": f"{home_team} vs {away_team}" if home_team and away_team else str(match_id),
                "team": team,
                "opponent": opponent,
                "scorer": scorer,
                "minute": minute,
                "second": second,
                "period": int(goal.get("period", 0)),
                "possession": possession,
                "passes_before_goal": passes_before_goal,
                "attack_duration_seconds": duration_seconds,
                "build_up_type": classify_build_up(passes_before_goal),
                "shot_xg": shot_xg,
                "tournament_stage": stage,
                "tournament_progress_score": 0,
                "finishing_efficiency": np.nan,
                "match_stage": stage,
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
                    "match_name": f"{home_team} vs {away_team}" if home_team and away_team else str(match_id),
                    "team": team,
                    "event_order": int(order),
                    "event_index": int(event.get("index", order)),
                    "event_id": event.get("id", f"{build_up_id}_{order}"),
                    "event_type": event_type,
                    "player": event.get("player", ""),
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

    goals_df = pd.DataFrame(goal_rows) if goal_rows else _empty_goals_df()
    events_df = pd.DataFrame(event_rows) if event_rows else _empty_events_df()
    team_df = _team_summary(goals_df)
    return goals_df, events_df, team_df


def _team_summary(goals_df):
    if goals_df.empty:
        return _empty_team_df()
    out = (
        goals_df.groupby("team", as_index=False)
        .agg(
            goals=("build_up_id", "nunique"),
            goals_analysed=("build_up_id", "nunique"),
            avg_passes_before_goal=("passes_before_goal", "mean"),
            avg_attack_duration=("attack_duration_seconds", "mean"),
            total_xg=("shot_xg", "sum"),
        )
    )
    out["shots"] = np.nan
    out["finishing_efficiency"] = np.nan
    out["tournament_stage"] = ""
    out["tournament_progress_score"] = 0
    return out


def _empty_goals_df():
    return pd.DataFrame(columns=["build_up_id", "goal_id", "goal_event_id", "goal_label", "match_id", "match_name", "team", "opponent", "scorer", "minute", "second", "period", "possession", "passes_before_goal", "attack_duration_seconds", "build_up_type", "shot_xg", "tournament_stage", "tournament_progress_score", "finishing_efficiency", "match_stage", "play_pattern", "start_x", "start_y", "goal_x", "goal_y", "shot_x", "shot_y"])


def _empty_events_df():
    return pd.DataFrame(columns=["build_up_id", "goal_id", "match_id", "match_name", "team", "event_order", "event_index", "event_id", "event_type", "player", "recipient", "pass_recipient", "minute", "second", "timestamp_label", "x", "y", "end_x", "end_y", "pass_outcome", "outcome", "is_completed_pass", "is_shot", "is_assist", "is_goal"])


def _empty_team_df():
    return pd.DataFrame(columns=["team", "goals", "goals_analysed", "avg_passes_before_goal", "avg_attack_duration", "shots", "finishing_efficiency", "tournament_stage", "tournament_progress_score", "total_xg"])


def _timestamp_to_seconds(value):
    try:
        h, m, s = str(value).split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)
    except Exception:
        return 0.0
