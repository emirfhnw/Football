from pathlib import Path
import pandas as pd

from src.statsbomb_explorer import build_match_goal_tables


BASE_DIR = Path(__file__).resolve().parent

SELECTED_TOURNAMENTS_FILE = BASE_DIR / "data" / "raw" / "selected_tournaments.csv"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

GOALS_OUT = PROCESSED_DIR / "goals_df.csv"
EVENTS_OUT = PROCESSED_DIR / "build_up_events_df.csv"
TEAMS_OUT = PROCESSED_DIR / "team_efficiency_df.csv"


def main():
    tournaments = pd.read_csv(SELECTED_TOURNAMENTS_FILE)

    all_goals = []
    all_events = []
    all_teams = []

    for _, row in tournaments.iterrows():
        label = str(row["label"])
        value = str(row["value"])

        print("=" * 80)
        print(f"Building: {label}")
        print(f"Value: {value}")

        try:
            goals_df, events_df, team_df = build_match_goal_tables(value, "ALL")
        except Exception as exc:
            print(f"FAILED: {label}")
            print(exc)
            continue

        if goals_df.empty:
            print(f"SKIP: {label} has no goal build-ups.")
            continue

        goals_df = goals_df.copy()
        events_df = events_df.copy()
        team_df = team_df.copy()

        goals_df["competition_label"] = label
        goals_df["competition_value"] = value

        events_df["competition_label"] = label
        events_df["competition_value"] = value

        team_df["competition_label"] = label
        team_df["competition_value"] = value

        all_goals.append(goals_df)
        all_events.append(events_df)
        all_teams.append(team_df)

        print(f"OK: {label}")
        print(f"Goals: {len(goals_df)}")
        print(f"Events: {len(events_df)}")
        print(f"Teams: {len(team_df)}")

    if not all_goals:
        raise RuntimeError("No tournament data was created.")

    final_goals = pd.concat(all_goals, ignore_index=True)
    final_events = pd.concat(all_events, ignore_index=True)
    final_teams = pd.concat(all_teams, ignore_index=True)

    final_goals.to_csv(GOALS_OUT, index=False, encoding="utf-8")
    final_events.to_csv(EVENTS_OUT, index=False, encoding="utf-8")
    final_teams.to_csv(TEAMS_OUT, index=False, encoding="utf-8")

    print("=" * 80)
    print("DONE")
    print(f"Saved: {GOALS_OUT}")
    print(f"Saved: {EVENTS_OUT}")
    print(f"Saved: {TEAMS_OUT}")
    print(f"Total goals: {len(final_goals)}")
    print(f"Total events: {len(final_events)}")
    print(f"Total teams: {len(final_teams)}")


if __name__ == "__main__":
    main()