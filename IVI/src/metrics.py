from __future__ import annotations

import pandas as pd


def dashboard_kpis(goals_df: pd.DataFrame) -> dict[str, object]:
    if goals_df.empty:
        return {
            "total_goals": 0,
            "avg_passes": 0,
            "median_passes": 0,
            "avg_duration": 0,
            "most_common_type": "-",
        }
    type_counts = goals_df["build_up_type"].astype(str).value_counts()

    return {
        "total_goals": int(goals_df["build_up_id"].nunique()),
        "avg_passes": round(float(goals_df["passes_before_goal"].mean()), 1),
        "median_passes": round(float(goals_df["passes_before_goal"].median()), 1),
        "avg_duration": round(float(goals_df["attack_duration_seconds"].mean()), 1),
        "most_common_type": type_counts.index[0] if not type_counts.empty else "-",
    }


def filter_goals(
    goals_df: pd.DataFrame,
    teams: list[str] | None = None,
    matches: list[str] | None = None,
    build_types: list[str] | None = None,
    players: list[str] | None = None,
    minute_range: list[int] | None = None,
) -> pd.DataFrame:
    filtered = goals_df.copy()
    if teams:
        filtered = filtered[filtered["team"].isin(teams)]
    if matches:
        filtered = filtered[filtered["match_name"].isin(matches)]
    if build_types:
        filtered = filtered[filtered["build_up_type"].astype(str).isin(build_types)]
    if players:
        filtered = filtered[filtered["scorer"].isin(players)]
    if minute_range and len(minute_range) == 2:
        filtered = filtered[
            (filtered["minute"] >= minute_range[0])
            & (filtered["minute"] <= minute_range[1])
        ]
    return filtered


def team_ranking(goals_df: pd.DataFrame) -> pd.DataFrame:
    if goals_df.empty:
        return pd.DataFrame(columns=["team", "goals", "avg_passes", "avg_duration"])
    return (
        goals_df.groupby("team", as_index=False)
        .agg(
            goals=("build_up_id", "nunique"),
            avg_passes=("passes_before_goal", "mean"),
            avg_duration=("attack_duration_seconds", "mean"),
        )
        .sort_values("avg_passes", ascending=False)
    )
