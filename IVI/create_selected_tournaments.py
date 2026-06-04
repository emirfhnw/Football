from pathlib import Path
import pandas as pd
from statsbombpy import sb


BASE_DIR = Path(__file__).resolve().parent
OUT_FILE = BASE_DIR / "data" / "selected_tournaments.csv"
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)


TOURNAMENT_KEYWORDS = [
    "World Cup",
    "Euro",
    "European Championship",
    "Copa America",
    "Africa Cup",
]


def stage_to_text(value):
    if isinstance(value, dict):
        return str(value.get("name", ""))
    return str(value)


def main():
    competitions = sb.competitions()
    rows = []

    for _, comp in competitions.iterrows():
        competition_name = str(comp["competition_name"])
        season_name = str(comp["season_name"])

        is_tournament = any(
            keyword.lower() in competition_name.lower()
            for keyword in TOURNAMENT_KEYWORDS
        )

        if not is_tournament:
            continue

        competition_id = int(comp["competition_id"])
        season_id = int(comp["season_id"])
        label = f"{competition_name} - {season_name}"

        try:
            matches = sb.matches(
                competition_id=competition_id,
                season_id=season_id,
            )
        except Exception as exc:
            print(f"SKIP {label}: could not load matches")
            continue

        if matches.empty or "competition_stage" not in matches.columns:
            print(f"SKIP {label}: no stage information")
            continue

        stages = matches["competition_stage"].apply(stage_to_text).dropna().unique().tolist()

        has_group_stage = any("group" in stage.lower() for stage in stages)
        has_final = any(stage.lower().strip() == "final" for stage in stages)
        enough_matches = len(matches) >= 10

        if has_group_stage and has_final and enough_matches:
            print(f"KEEP {label} | matches: {len(matches)}")
            rows.append(
                {
                    "label": label,
                    "competition_id": competition_id,
                    "season_id": season_id,
                    "value": f"{competition_id}|{season_id}|ALL",
                    "match_count": len(matches),
                    "stages": " | ".join(sorted(stages)),
                }
            )
        else:
            print(f"SKIP {label} | matches: {len(matches)} | stages: {stages}")

    selected = pd.DataFrame(rows)

    if selected.empty:
        raise RuntimeError("No tournaments found with group stage and final.")

    selected.to_csv(OUT_FILE, index=False, encoding="utf-8")

    print("\nDONE")
    print(f"Saved: {OUT_FILE}")
    print(selected[["label", "competition_id", "season_id", "match_count"]])


if __name__ == "__main__":
    main()