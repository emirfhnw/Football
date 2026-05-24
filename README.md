# Goal Build-up Analysis

Interactive Dash/Plotly dashboard for analysing goal build-ups at the FIFA World Cup 2022.

## Research Question

How are goals created at the FIFA World Cup 2022: through quick attacks with few passes or through longer passing sequences?

The dashboard focuses on completed passes before goals, attack duration, team build-up style and concrete goal sequences.

## Dataset

The project uses StatsBomb Open Data for the FIFA World Cup 2022.

Used data fields include passes, shots, goals, teams, players, possessions, timestamps, match metadata and event coordinates.

This is event data only. The pitch view shows recorded event coordinates and does not show tracking data or invented player runs.

## What The Dashboard Shows

- Goals analysed and core build-up metrics.
- Distribution of quick, medium and long build-ups.
- Team ranking by average completed passes before goal.
- Relationship between completed passes and attack duration.
- A selected goal build-up on a football pitch with event timeline.

Build-up categories:

- Quick attack: 0-2 completed passes
- Medium build-up: 3-6 completed passes
- Long build-up: 7+ completed passes

## Main Interactions

- Filter by team, build-up type and match.
- Select a goal from the goal dropdown.
- Click a scatterplot point to inspect that goal on the pitch.
- Click a build-up type bar to filter the dashboard.
- Step through the selected event sequence with Previous, Next event and Show all.

## How To Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the app:

```bash
python app.py
```

Open the local URL shown in the terminal, usually:

```text
http://127.0.0.1:8050/
```

## Project Structure

```text
Football/
├── app.py
├── requirements.txt
├── README.md
├── assets/
│   └── style.css
├── data/
│   ├── raw/
│   └── processed/
│       ├── goals_df.csv
│       ├── build_up_events_df.csv
│       └── team_efficiency_df.csv
├── src/
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── metrics.py
│   ├── figures.py
│   ├── pitch_plots.py
│   └── utils.py
└── evaluation/
    ├── tasks.md
    ├── sus_questionnaire.md
    └── evaluation_notes.md
```

## Limitations

- No tracking data is used, so off-ball movement and player runs are not shown.
- The pitch sequence is a step-by-step event view, not a physical animation.
- Legacy processed build-up files do not contain every original StatsBomb event field; pass recipients are inferred where necessary.
- The dashboard is descriptive and does not claim causal relationships.

## IVI Design Rationale

- Overview first: KPI cards and aggregate charts appear before detailed inspection.
- Details on demand: hover tooltips and the selected goal view reveal event-level information.
- Linked views: scatterplot clicks update the pitch, summary and timeline.
- Filtering: team, build-up type and match filters update the goal list and charts.
- Drill-down: users move from team-level patterns to a concrete goal build-up.
- Performance: processed CSVs are loaded at startup, not recomputed inside callbacks.

## Evaluation Plan

The evaluation material is in `evaluation/`.

Participants complete five short tasks, then answer the SUS questionnaire. Qualitative notes capture task success, confusion points, positive feedback and possible design changes.
