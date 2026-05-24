# Goal Build-up Analysis

Interactive IVI dashboard for analysing how goals were created at the FIFA World Cup 2022.

## Research Question

How are goals created at the FIFA World Cup 2022: through quick attacks with few passes or through longer passing sequences?

Additional question: does a team's goal build-up style relate to finishing efficiency and tournament progress?

## Dataset

The dashboard uses StatsBomb Open Data for the FIFA World Cup 2022. It works with event data: passes, shots, goals, possessions, teams, players, timestamps, match information and pitch coordinates.

This is event data only. The app does not use tracking data and does not invent off-ball player movement.

## Intended Users

- Coach
- Football analyst
- Football fan

## What The Dashboard Shows

- Completed passes before goals.
- Quick, medium and long build-up distribution.
- Team profiles by average passes before goal.
- Relationship between passes and attack duration.
- Step-by-step pitch simulation for selected goal build-ups.

Build-up types:

- Quick: 0-2 completed passes
- Medium: 3-6 completed passes
- Long: 7+ completed passes

## Supported Tasks

- Find the most common build-up type.
- Compare quick, medium and long goal build-ups.
- Identify teams with longer or shorter goal build-ups.
- Inspect a concrete goal sequence on the pitch.
- Compare passes before goal with attack duration.
- Compare team build-up profiles.

## Main Interactions

- Filter by team, build-up type, match and scorer.
- Select a goal from the dropdown.
- Click a scatterplot point to load that goal in the pitch view.
- Click a build-up type bar to filter the dashboard.
- Use Previous, Next, Play, Pause, Show all and Reset for the sequence.
- Click timeline rows to jump to a specific event.

## How The Simulation Works

The pitch uses StatsBomb's 120 x 80 coordinate system. Each pass or shot is drawn from its event start coordinate to its event end coordinate. Event circles are numbered in sequence order. The active event and current ball position are highlighted.

Attacks are normalised left-to-right when the recorded sequence clearly moves right-to-left. No tracking paths are shown.

## How To Run

```bash
pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:8050/
```

If port 8050 is already occupied, the app falls back to:

```text
http://127.0.0.1:8051/
```

## Project Structure

```text
IVI/
|-- app.py
|-- requirements.txt
|-- README.md
|-- assets/
|   |-- style.css
|-- data/
|   |-- raw/
|   |-- processed/
|       |-- goals_df.csv
|       |-- build_up_events_df.csv
|       |-- team_efficiency_df.csv
|-- src/
|   |-- data_loader.py
|   |-- preprocessing.py
|   |-- metrics.py
|   |-- pitch_plots.py
|   |-- figures.py
|   |-- layout.py
|   |-- utils.py
|-- evaluation/
    |-- tasks.md
    |-- sus_questionnaire.md
    |-- evaluation_notes.md
```

## Preprocessing Summary

For each goal, the preprocessing identifies the goal shot, its possession, the completed passes in the same possession before the shot, and the attack duration. The processed goal table stores team, scorer, match, minute, possession, passes before goal, attack duration, build-up type, xG when available and tournament stage.

The event table stores the event sequence used by the pitch simulation.

## IVI Design Rationale

- Overview first: KPI cards and aggregate charts summarize the dataset.
- Details on demand: selecting a goal opens its event sequence, summary and timeline.
- Linked views: scatterplot clicks update the pitch simulation.
- Filtering: filters update the goal list, KPIs and charts.
- Drill-down: users move from tournament/team patterns to a concrete goal.
- Tooltips: charts and pitch nodes expose event-level details.
- Feedback cues: selected steps are highlighted in the pitch and timeline.
- Brushing: clicking a build-up type bar applies that category as a filter.

## Iterative Improvement

- The initial version was visually overloaded.
- The layout was reduced to three views: Overview, Goal Replay and Team Comparison.
- The pitch simulation was changed from show-all default to step-by-step default.
- Timeline and selected-event feedback were improved.
- Debug tools and callback issues were removed.
- The show-all view was toned down for long sequences.
- Finishing efficiency was removed from the dashboard to keep the analysis focused.

## Performance Considerations

Processed CSVs are loaded once at startup. Heavy preprocessing is not run inside callbacks. Step controls update only the pitch, summary and timeline instead of rebuilding all charts.

## Evaluation Plan

Evaluation material is stored in `evaluation/`. Participants complete task-based exploration, then fill out a SUS questionnaire. Notes capture task success, observed problems and improvement ideas.

## Limitations

- No tracking data is available.
- Off-ball movement cannot be shown.
- Legacy processed event data may not contain every original StatsBomb field.
- The dashboard is descriptive and does not make causal claims.

## Reproducibility

The app runs locally from the processed CSVs in this repository. To regenerate processed files:

```bash
python -c "from src.preprocessing import preprocess_all; preprocess_all(force=True)"
```
