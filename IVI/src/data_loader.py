from __future__ import annotations

from functools import lru_cache

import pandas as pd

from .preprocessing import preprocess_all
from .utils import BUILD_UP_ORDER, PROCESSED_DIR, safe_numeric


@lru_cache(maxsize=1)
def load_dashboard_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    goals_df, events_df, team_df = preprocess_all()
    return _prepare_goals(goals_df), _prepare_events(events_df), _prepare_team(team_df)


def _prepare_goals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    numeric_cols = [
        "match_id",
        "minute",
        "second",
        "passes_before_goal",
        "attack_duration_seconds",
        "shot_xg",
        "tournament_progress_score",
        "finishing_efficiency",
    ]
    for col in numeric_cols:
        if col in df:
            df[col] = safe_numeric(df[col])
    df["build_up_type"] = pd.Categorical(df["build_up_type"], categories=BUILD_UP_ORDER, ordered=True)
    df["goal_label"] = (
        df["team"].astype(str)
        + " - "
        + df["scorer"].astype(str)
        + " ("
        + df["minute"].astype(int).astype(str)
        + "') vs "
        + df["opponent"].fillna("").astype(str)
    )
    return df.sort_values(["match_id", "minute", "second"]).reset_index(drop=True)


def _prepare_events(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["event_order", "minute", "second", "x", "y", "end_x", "end_y"]:
        if col in df:
            df[col] = safe_numeric(df[col])
    return df.sort_values(["build_up_id", "event_order"]).reset_index(drop=True)


def _prepare_team(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in [
        "shots",
        "goals",
        "goals_analysed",
        "finishing_efficiency",
        "tournament_progress_score",
        "avg_passes_before_goal",
        "avg_attack_duration",
    ]:
        if col in df:
            df[col] = safe_numeric(df[col])
    return df


def clear_data_cache() -> None:
    load_dashboard_data.cache_clear()


def processed_paths() -> dict[str, str]:
    return {
        "goals": str(PROCESSED_DIR / "goals_df.csv"),
        "events": str(PROCESSED_DIR / "build_up_events_df.csv"),
        "team": str(PROCESSED_DIR / "team_efficiency_df.csv"),
    }
