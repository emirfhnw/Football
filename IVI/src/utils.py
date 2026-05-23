from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

PITCH_LENGTH = 120
PITCH_WIDTH = 80

BUILD_UP_ORDER = ["Quick attack", "Medium build-up", "Long build-up"]
BUILD_UP_COLORS = {
    "Quick attack": "#94a3b8",
    "Medium build-up": "#38bdf8",
    "Long build-up": "#f59e0b",
}

STAGE_SCORE = {
    "Group Stage": 1,
    "Round of 16": 2,
    "Quarter Final": 3,
    "Quarter-Finals": 3,
    "Semi Final": 4,
    "Semi-Finals": 4,
    "Third Place Play-off": 5,
    "Final": 6,
    "Winner": 7,
}

TEAM_STAGE_MAPPING_2022 = {
    "Qatar": "Group Stage",
    "Ecuador": "Group Stage",
    "Iran": "Group Stage",
    "Wales": "Group Stage",
    "Mexico": "Group Stage",
    "Saudi Arabia": "Group Stage",
    "Denmark": "Group Stage",
    "Tunisia": "Group Stage",
    "Canada": "Group Stage",
    "Belgium": "Group Stage",
    "Germany": "Group Stage",
    "Costa Rica": "Group Stage",
    "Serbia": "Group Stage",
    "Cameroon": "Group Stage",
    "Ghana": "Group Stage",
    "Uruguay": "Group Stage",
    "United States": "Round of 16",
    "Senegal": "Round of 16",
    "Australia": "Round of 16",
    "Poland": "Round of 16",
    "Spain": "Round of 16",
    "Japan": "Round of 16",
    "Switzerland": "Round of 16",
    "South Korea": "Round of 16",
    "Netherlands": "Quarter Final",
    "Brazil": "Quarter Final",
    "Portugal": "Quarter Final",
    "England": "Quarter Final",
    "Croatia": "Semi Final",
    "Morocco": "Semi Final",
    "France": "Final",
    "Argentina": "Winner",
}


def ensure_dirs() -> None:
    for path in [RAW_DIR, PROCESSED_DIR, ROOT_DIR / "assets", ROOT_DIR / "evaluation", ROOT_DIR / "src"]:
        path.mkdir(parents=True, exist_ok=True)


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def classify_build_up(passes_before_goal: object) -> str:
    passes = 0 if pd.isna(passes_before_goal) else int(passes_before_goal)
    if passes <= 2:
        return "Quick attack"
    if passes <= 6:
        return "Medium build-up"
    return "Long build-up"


def stage_score(stage: object) -> int:
    return STAGE_SCORE.get(clean_text(stage), 0)


def safe_numeric(series: pd.Series, default: float = 0.0) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(default)


def first_existing(columns: Iterable[str], candidates: Iterable[str]) -> str | None:
    available = set(columns)
    for candidate in candidates:
        if candidate in available:
            return candidate
    return None


def normalize_attack_direction(df: pd.DataFrame, coordinate_cols: list[str]) -> pd.DataFrame:
    """Flip coordinates only when the selected sequence visibly attacks right-to-left."""
    if df.empty:
        return df
    out = df.copy()
    x_cols = [col for col in coordinate_cols if col.endswith("_x") or col == "x"]
    x_values = []
    for col in x_cols:
        if col in out:
            x_values.extend(pd.to_numeric(out[col], errors="coerce").dropna().tolist())
    if len(x_values) < 2 or x_values[-1] >= x_values[0]:
        return out

    for col in coordinate_cols:
        if col in out:
            if col.endswith("_x") or col == "x":
                out[col] = PITCH_LENGTH - pd.to_numeric(out[col], errors="coerce")
            elif col.endswith("_y") or col == "y":
                out[col] = PITCH_WIDTH - pd.to_numeric(out[col], errors="coerce")
    return out
