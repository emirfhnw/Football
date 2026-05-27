# Coach Attack Explorer

Interactive IVI dashboard for exploring how teams create goals in major football tournaments.

The dashboard is built for a simple coaching use case: a user selects a tournament, chooses a team, replays one goal attack step by step, and compares the team's attacking style with the rest of the tournament.

## Use case

A coach or beginner football analyst wants to answer:

> How do teams create goals in major tournaments, and how does a team's attacking style relate to tournament outcome?

The dashboard focuses on goal build-ups, not on full match prediction. It helps users turn professional match examples into practical training ideas.

## Main features

- Tournament selection from a prepared local tournament list
- Team and goal selection
- Step-by-step attack replay on a football pitch
- Build-up zones on the pitch: build-up, progression and final third
- Tournament goal pattern charts
- Passes vs duration scatterplot
- Team goal style map
- Directness ranking with tournament finish

## Data source

The project uses StatsBomb open event data. The data is preprocessed into local CSV files so that the dashboard can run without downloading event data during normal use.

Included processed files:

```text
IVI/data/processed/goals_df.csv
IVI/data/processed/build_up_events_df.csv
IVI/data/processed/team_efficiency_df.csv
```

Included tournament selection file:

```text
IVI/data/raw/selected_tournaments.csv
```

## Folder structure

```text
IVI/
  app.py
  build_static_tournament_data.py
  create_selected_tournaments.py
  requirements.txt
  README.md

  assets/
    style.css

  data/
    raw/
      selected_tournaments.csv
    processed/
      goals_df.csv
      build_up_events_df.csv
      team_efficiency_df.csv

  src/
    data_loader.py
    figures.py
    layout.py
    metrics.py
    pitch_plots.py
    preprocessing.py
    static_tournament_store.py
    statsbomb_explorer.py
    utils.py

  evaluation/
    evaluation_tasks.md
    evaluation_results_template.csv
    evaluation_summary.md
    evaluation_analysis.md
    sus_questionnaire.md

  report/
    IVI_report.md
```

## How to run the dashboard

Open PowerShell in the repository root and run:

```powershell
cd IVI
pip install -r requirements.txt
python app.py
```

Then open the local Dash URL shown in the terminal, usually:

```text
http://127.0.0.1:8050/
```

## How to rebuild the local dataset

The processed CSV files are already included. Rebuilding is only needed if the data should be regenerated from StatsBomb.

```powershell
cd IVI
python build_static_tournament_data.py
```

This can take some time because several tournaments are processed.

## Dashboard workflow

1. Choose a tournament.
2. Select one team.
3. Select one goal example.
4. Replay the attack step by step.
5. Inspect the tournament goal pattern charts.
6. Compare the selected team in the team style map and directness ranking.

## Limitations

- The dashboard analyses goal build-ups only, not all attacks.
- Off-ball runs and tactical positioning away from the ball are not visible in event data.
- The ranking describes attacking style in goals, not overall team strength.
- The dashboard should not be interpreted as a prediction model for tournament success.
- The data quality depends on the available StatsBomb event data and the preprocessing rules.

## Project status

The dashboard is prepared for IVI submission together with evaluation material and a written report draft.