from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .utils import (
    PROCESSED_DIR,
    RAW_DIR,
    TEAM_STAGE_MAPPING_2022,
    classify_build_up,
    ensure_dirs,
    safe_numeric,
    stage_score,
)


def preprocess_all(
    raw_dir: Path = RAW_DIR,
    processed_dir: Path = PROCESSED_DIR,
    force: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create dashboard-ready CSVs.

    The preferred input is full StatsBomb event data. In this repository the available
    source for goal build-ups is the existing GDV processed output, so this function
    normalizes that data into the IVI schema and documents the missing event details.
    """
    ensure_dirs()
    goals_path = processed_dir / "goals_df.csv"
    events_path = processed_dir / "build_up_events_df.csv"
    team_path = processed_dir / "team_efficiency_df.csv"

    if not force and goals_path.exists() and events_path.exists() and team_path.exists():
        goals_df, events_df, team_df = pd.read_csv(goals_path), pd.read_csv(events_path), pd.read_csv(team_path)
        return ensure_dashboard_schema(goals_df, events_df, team_df)

    legacy_goals = processed_dir / "goal_buildups.csv"
    legacy_passes = processed_dir / "goal_buildup_passes.csv"
    if legacy_goals.exists() and legacy_passes.exists():
        goals_df, events_df, team_df = normalize_legacy_processed(processed_dir)
    elif goals_path.exists() and events_path.exists() and team_path.exists():
        goals_df, events_df, team_df = ensure_dashboard_schema(
            pd.read_csv(goals_path),
            pd.read_csv(events_path),
            pd.read_csv(team_path),
        )
    else:
        goals_df, events_df, team_df = build_from_statsbomb_files(raw_dir, processed_dir)

    goals_df.to_csv(goals_path, index=False, encoding="utf-8")
    events_df.to_csv(events_path, index=False, encoding="utf-8")
    team_df.to_csv(team_path, index=False, encoding="utf-8")
    return goals_df, events_df, team_df


def ensure_dashboard_schema(
    goals_df: pd.DataFrame,
    events_df: pd.DataFrame,
    team_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    goals_df = goals_df.copy()
    events_df = events_df.copy()
    if "goal_id" not in goals_df and "build_up_id" in goals_df:
        goals_df["goal_id"] = goals_df["build_up_id"]
    if "goal_event_id" not in goals_df and "build_up_id" in goals_df:
        goals_df["goal_event_id"] = goals_df["build_up_id"]

    if "goal_id" not in events_df and "build_up_id" in events_df:
        events_df["goal_id"] = events_df["build_up_id"]
    if "event_index" not in events_df and "event_order" in events_df:
        events_df["event_index"] = events_df["event_order"]
    if "event_id" not in events_df:
        events_df["event_id"] = events_df.apply(
            lambda row: f"{row.get('build_up_id', 'goal')}_{row.get('event_type', 'event').lower()}_{int(row.get('event_order', 0))}",
            axis=1,
        )
    if "pass_recipient" not in events_df and "recipient" in events_df:
        events_df["pass_recipient"] = events_df["recipient"]
    if "outcome" not in events_df:
        events_df["outcome"] = events_df.get("pass_outcome", "")
        goal_mask = events_df["is_goal"].astype(bool) if "is_goal" in events_df else pd.Series(False, index=events_df.index)
        events_df.loc[goal_mask, "outcome"] = "Goal"
    if "is_completed_pass" not in events_df:
        pass_outcome = events_df["pass_outcome"] if "pass_outcome" in events_df else pd.Series("", index=events_df.index)
        events_df["is_completed_pass"] = events_df["event_type"].eq("Pass") & pass_outcome.eq("Complete")
    if "is_shot" not in events_df:
        events_df["is_shot"] = events_df["event_type"].eq("Shot")
    return goals_df, events_df, team_df


def normalize_legacy_processed(processed_dir: Path = PROCESSED_DIR) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    goals = pd.read_csv(processed_dir / "goal_buildups.csv")
    passes = pd.read_csv(processed_dir / "goal_buildup_passes.csv")
    matches = _read_optional(processed_dir.parent / "raw" / "world_cup_2022_matches.csv")
    shots = _read_optional(processed_dir / "world_cup_2022_shots.csv")
    team_context = _read_optional(processed_dir / "team_tournament_context.csv")
    team_summary = _read_optional(processed_dir / "world_cup_2022_team_summary.csv")

    goals = goals.copy()
    goals["goal_id"] = goals["build_up_id"]
    goals["goal_event_id"] = goals["build_up_id"]
    goals["match_name"] = goals["match_label"]
    goals["scorer"] = goals["goal_player"]
    goals["minute"] = safe_numeric(goals["goal_minute"]).astype(int)
    goals["second"] = safe_numeric(goals["goal_second"]).astype(int)
    goals["attack_duration_seconds"] = safe_numeric(goals["duration_seconds"])
    goals["build_up_type"] = goals["passes_before_goal"].apply(classify_build_up)

    if not matches.empty:
        match_cols = ["match_id", "home_team", "away_team", "competition_stage"]
        goals = goals.merge(matches[match_cols], how="left", on="match_id")
        goals["opponent"] = np.where(goals["team"].eq(goals["home_team"]), goals["away_team"], goals["home_team"])
        goals["match_stage"] = goals["competition_stage"]
    else:
        goals["opponent"] = ""
        goals["match_stage"] = ""

    goals["tournament_stage"] = goals["team"].map(TEAM_STAGE_MAPPING_2022).fillna(goals["match_stage"])
    goals["tournament_progress_score"] = goals["tournament_stage"].apply(stage_score)

    if not shots.empty:
        goal_shots = shots[shots["is_goal"].astype(str).str.lower().eq("true")].copy()
        goal_shots["minute"] = safe_numeric(goal_shots["minute"]).astype(int)
        goal_shots["second"] = safe_numeric(goal_shots["second"]).astype(int)
        shot_cols = ["match_id", "team", "player", "minute", "second", "shot_statsbomb_xg", "x", "y"]
        goals = goals.merge(
            goal_shots[shot_cols],
            how="left",
            left_on=["match_id", "team", "scorer", "minute", "second"],
            right_on=["match_id", "team", "player", "minute", "second"],
            suffixes=("", "_shot"),
        )
        goals["shot_xg"] = safe_numeric(goals.get("shot_statsbomb_xg", pd.Series(dtype=float)))
        goals["shot_x"] = goals.get("x", goals["goal_x"])
        goals["shot_y"] = goals.get("y", goals["goal_y"])
    else:
        goals["shot_xg"] = 0.0
        goals["shot_x"] = goals["goal_x"]
        goals["shot_y"] = goals["goal_y"]

    team_df = build_team_efficiency(goals, shots, team_context, team_summary)
    goals = goals.merge(team_df[["team", "finishing_efficiency"]], how="left", on="team")

    output_cols = [
        "build_up_id",
        "goal_id",
        "match_id",
        "match_name",
        "match_date",
        "team",
        "opponent",
        "scorer",
        "minute",
        "second",
        "period",
        "possession",
        "passes_before_goal",
        "attack_duration_seconds",
        "build_up_type",
        "shot_xg",
        "tournament_stage",
        "tournament_progress_score",
        "finishing_efficiency",
        "goal_event_id",
        "match_stage",
        "play_pattern",
        "start_x",
        "start_y",
        "goal_x",
        "goal_y",
        "shot_x",
        "shot_y",
    ]
    goals = goals[[col for col in output_cols if col in goals.columns]].copy()

    events_df = normalize_legacy_passes(passes, goals)
    return goals, events_df, team_df


def normalize_legacy_passes(passes: pd.DataFrame, goals_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    goals_lookup = goals_df.set_index("build_up_id").to_dict("index")
    for build_up_id, group in passes.sort_values(["build_up_id", "pass_order"]).groupby("build_up_id"):
        goal = goals_lookup.get(build_up_id, {})
        group_records = group.to_dict("records")
        for idx, row in enumerate(group_records):
            next_player = group_records[idx + 1]["player"] if idx + 1 < len(group_records) else goal.get("scorer", "")
            rows.append(
                {
                    "build_up_id": build_up_id,
                    "goal_id": build_up_id,
                    "match_id": row.get("match_id"),
                    "match_name": row.get("match_label", goal.get("match_name", "")),
                    "team": row.get("team", goal.get("team", "")),
                    "event_order": int(row.get("pass_order", idx + 1)),
                    "event_index": int(row.get("pass_order", idx + 1)),
                    "event_id": f"{build_up_id}_pass_{int(row.get('pass_order', idx + 1))}",
                    "event_type": "Pass",
                    "player": row.get("player", ""),
                    "recipient": next_player,
                    "pass_recipient": next_player,
                    "minute": int(row.get("minute", 0)),
                    "second": int(row.get("second", 0)),
                    "timestamp_label": f"{int(row.get('minute', 0)):02d}:{int(row.get('second', 0)):02d}",
                    "x": row.get("x"),
                    "y": row.get("y"),
                    "end_x": row.get("end_x"),
                    "end_y": row.get("end_y"),
                    "pass_outcome": "Complete",
                    "outcome": "Complete",
                    "is_completed_pass": True,
                    "is_shot": False,
                    "is_assist": idx == len(group_records) - 1,
                    "is_goal": False,
                }
            )
        rows.append(
            {
                "build_up_id": build_up_id,
                "goal_id": build_up_id,
                "match_id": goal.get("match_id"),
                "match_name": goal.get("match_name", ""),
                "team": goal.get("team", ""),
                "event_order": len(group_records) + 1,
                "event_index": len(group_records) + 1,
                "event_id": f"{build_up_id}_shot",
                "event_type": "Shot",
                "player": goal.get("scorer", ""),
                "recipient": "",
                "pass_recipient": "",
                "minute": int(goal.get("minute", 0)),
                "second": int(goal.get("second", 0)),
                "timestamp_label": f"{int(goal.get('minute', 0)):02d}:{int(goal.get('second', 0)):02d}",
                "x": goal.get("shot_x", goal.get("goal_x")),
                "y": goal.get("shot_y", goal.get("goal_y")),
                "end_x": 120,
                "end_y": 40,
                "pass_outcome": "",
                "outcome": "Goal",
                "is_completed_pass": False,
                "is_shot": True,
                "is_assist": False,
                "is_goal": True,
            }
        )
    return pd.DataFrame(rows)


def build_team_efficiency(
    goals_df: pd.DataFrame,
    shots: pd.DataFrame,
    team_context: pd.DataFrame,
    team_summary: pd.DataFrame,
) -> pd.DataFrame:
    if not team_context.empty:
        team_df = team_context.copy()
        team_df["tournament_stage"] = team_df["team"].map(TEAM_STAGE_MAPPING_2022).fillna(team_df["stage"])
        team_df["tournament_progress_score"] = team_df["tournament_stage"].apply(stage_score)
        team_df["finishing_efficiency"] = safe_numeric(team_df["conversion_rate"])
    elif not team_summary.empty:
        team_df = team_summary.copy()
        team_df["tournament_stage"] = team_df["team"].map(TEAM_STAGE_MAPPING_2022)
        team_df["tournament_progress_score"] = team_df["tournament_stage"].apply(stage_score)
        team_df["finishing_efficiency"] = safe_numeric(team_df["conversion_rate"])
    elif not shots.empty:
        team_df = (
            shots.groupby("team")
            .agg(shots=("team", "size"), goals=("is_goal", "sum"))
            .reset_index()
        )
        team_df["tournament_stage"] = team_df["team"].map(TEAM_STAGE_MAPPING_2022)
        team_df["tournament_progress_score"] = team_df["tournament_stage"].apply(stage_score)
        team_df["finishing_efficiency"] = team_df["goals"] / team_df["shots"].replace(0, np.nan)
    else:
        team_df = goals_df.groupby("team").agg(goals=("team", "size")).reset_index()
        team_df["shots"] = np.nan
        team_df["tournament_stage"] = team_df["team"].map(TEAM_STAGE_MAPPING_2022)
        team_df["tournament_progress_score"] = team_df["tournament_stage"].apply(stage_score)
        team_df["finishing_efficiency"] = np.nan

    buildup = (
        goals_df.groupby("team")
        .agg(
            goals_analysed=("team", "size"),
            avg_passes_before_goal=("passes_before_goal", "mean"),
            avg_attack_duration=("attack_duration_seconds", "mean"),
        )
        .reset_index()
    )
    team_df = team_df.merge(buildup, how="left", on="team")
    for col in ["shots", "goals", "goals_analysed", "avg_passes_before_goal", "avg_attack_duration"]:
        if col not in team_df.columns:
            team_df[col] = np.nan
    return team_df[
        [
            "team",
            "shots",
            "goals",
            "goals_analysed",
            "finishing_efficiency",
            "tournament_stage",
            "tournament_progress_score",
            "avg_passes_before_goal",
            "avg_attack_duration",
        ]
    ].copy()


def build_from_statsbomb_files(raw_dir: Path, processed_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Minimal StatsBomb JSON fallback for repositories with full event exports."""
    event_files = list(raw_dir.glob("events/**/*.json")) + list(raw_dir.glob("*.json"))
    if not event_files:
        raise FileNotFoundError(
            "No full StatsBomb event files found and legacy processed goal build-up CSVs are missing."
        )

    events = []
    for file in event_files:
        match_id = int(file.stem) if file.stem.isdigit() else None
        with file.open("r", encoding="utf-8") as handle:
            for event in json.load(handle):
                event["match_id"] = event.get("match_id", match_id)
                events.append(event)
    events_df = pd.json_normalize(events)
    return build_goal_tables_from_events(events_df, processed_dir)


def build_goal_tables_from_events(events_df: pd.DataFrame, processed_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    goals = events_df[
        events_df.get("type.name", "").eq("Shot") & events_df.get("shot.outcome.name", "").eq("Goal")
    ].copy()
    if goals.empty:
        raise ValueError("No goal shot events found in StatsBomb event data.")

    rows = []
    event_rows = []
    for idx, goal in goals.iterrows():
        match_id = goal.get("match_id")
        team = goal.get("team.name", "")
        possession = goal.get("possession")
        possession_events = events_df[
            (events_df["match_id"].eq(match_id))
            & (events_df["possession"].eq(possession))
            & (events_df.index <= idx)
        ].copy()
        possession_events = possession_events[possession_events.get("team.name", "").eq(team)]
        passes = possession_events[
            possession_events.get("type.name", "").eq("Pass")
            & possession_events.get("pass.outcome.name").isna()
        ]
        build_up_id = f"{match_id}_{len(rows) + 1}"
        goal_time = _seconds_from_timestamp(goal.get("timestamp", "00:00:00.000"))
        first_time = _seconds_from_timestamp(possession_events.iloc[0].get("timestamp", "00:00:00.000"))
        rows.append(
            {
                "build_up_id": build_up_id,
                "match_id": match_id,
                "match_name": str(match_id),
                "team": team,
                "opponent": "",
                "scorer": goal.get("player.name", ""),
                "minute": goal.get("minute", 0),
                "second": goal.get("second", 0),
                "period": goal.get("period", 0),
                "possession": possession,
                "passes_before_goal": len(passes),
                "attack_duration_seconds": max(0, goal_time - first_time),
                "build_up_type": classify_build_up(len(passes)),
                "shot_xg": goal.get("shot.statsbomb_xg", 0),
                "tournament_stage": TEAM_STAGE_MAPPING_2022.get(team, ""),
                "tournament_progress_score": stage_score(TEAM_STAGE_MAPPING_2022.get(team, "")),
                "goal_event_id": goal.get("id", build_up_id),
            }
        )
        for order, (_, event) in enumerate(pd.concat([passes, goal.to_frame().T]).iterrows(), start=1):
            location = _as_list(event.get("location", []))
            end_location = _as_list(event.get("pass.end_location", [])) if event.get("type.name") == "Pass" else [120, 40]
            event_rows.append(
                {
                    "build_up_id": build_up_id,
                    "match_id": match_id,
                    "team": team,
                    "event_order": order,
                    "event_type": event.get("type.name", ""),
                    "player": event.get("player.name", ""),
                    "recipient": event.get("pass.recipient.name", ""),
                    "minute": event.get("minute", 0),
                    "second": event.get("second", 0),
                    "timestamp_label": f"{int(event.get('minute', 0)):02d}:{int(event.get('second', 0)):02d}",
                    "x": location[0] if len(location) > 0 else np.nan,
                    "y": location[1] if len(location) > 1 else np.nan,
                    "end_x": end_location[0] if len(end_location) > 0 else np.nan,
                    "end_y": end_location[1] if len(end_location) > 1 else np.nan,
                    "pass_outcome": event.get("pass.outcome.name", "Complete") if event.get("type.name") == "Pass" else "",
                    "is_assist": False,
                    "is_goal": event.get("type.name") == "Shot",
                }
            )
    goals_df = pd.DataFrame(rows)
    events_out = pd.DataFrame(event_rows)
    team_df = build_team_efficiency(goals_df, pd.DataFrame(), pd.DataFrame(), pd.DataFrame())
    return goals_df, events_out, team_df


def _seconds_from_timestamp(value: object) -> float:
    parts = str(value).split(":")
    if len(parts) != 3:
        return 0.0
    return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])


def _as_list(value: object) -> list:
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return []
    return []


def _read_optional(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()
