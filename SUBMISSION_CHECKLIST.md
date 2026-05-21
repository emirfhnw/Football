# Submission Checklist – GDV & IVI

## Current project

**Project title:** FIFA World Cup 2022 Shot Quality Explorer

**Research question:** How do shot quality, shot locations and finishing efficiency differ between teams and matches in the FIFA World Cup 2022?

**Main data source:** StatsBomb Open Data, FIFA World Cup 2022

## What is implemented

### Data preparation

- [x] All FIFA World Cup 2022 matches are loaded from StatsBomb Open Data
- [x] Shot events are extracted
- [x] Match metadata is added
- [x] x/y shot coordinates are extracted
- [x] distance to goal is calculated
- [x] `is_goal` is created
- [x] `chance_quality` is created from xG
- [x] processed CSV files are saved

Relevant files:

```text
src/build_worldcup_shots.py
data/processed/world_cup_2022_shots.csv
data/processed/world_cup_2022_team_summary.csv
data/processed/world_cup_2022_player_summary.csv
```

### GDV

- [x] Static analysis figures are generated
- [x] Shot volume is analysed
- [x] Total xG is analysed
- [x] Goals vs xG is analysed
- [x] Chance quality categories are analysed
- [x] Shot map is generated
- [x] Distance vs xG is analysed
- [x] Top players by xG are analysed
- [x] Serbia vs Switzerland case study is included
- [x] GDV report draft exists

Relevant files:

```text
src/gdv_worldcup_analysis.py
reports/figures/
reports/gdv_insights.md
reports/gdv_report_draft.md
reports/final_report_draft.md
```

### IVI

- [x] Interactive Dash dashboard exists
- [x] Dashboard uses local processed CSV file
- [x] KPI cards are implemented
- [x] Team filter is implemented
- [x] Match filter is implemented
- [x] Player filter is implemented
- [x] Shot outcome filter is implemented
- [x] Chance quality filter is implemented
- [x] Minute range filter is implemented
- [x] Dependent match/player filters are implemented
- [x] Linked views are implemented
- [x] Hover details are implemented
- [x] Dashboard explains xG and chance quality
- [x] Visual story is structured around volume, quality, location, timing, efficiency and key players

Relevant files:

```text
dashboard/app_worldcup.py
reports/ivi_report_draft.md
```

### Evaluation

- [x] Evaluation tasks are prepared
- [x] SUS questionnaire is prepared
- [x] Evaluation results template is prepared
- [x] Evaluation summary is prepared
- [x] Evaluation analysis structure is prepared
- [ ] Real evaluation results still need to be filled in if required by the instructor

Relevant files:

```text
evaluation/evaluation_tasks.md
evaluation/sus_questionnaire.md
evaluation/evaluation_results_template.csv
evaluation/evaluation_summary.md
evaluation/evaluation_analysis.md
```

## Commands for final local test

Run these commands from the repository root:

```bash
pip install -r requirements.txt
python src/build_worldcup_shots.py
python src/gdv_worldcup_analysis.py
python dashboard/app_worldcup.py
```

Then open:

```text
http://127.0.0.1:8050
```

## What to say in the presentation

1. The project does not only compare goals or shot counts.
2. It separates shot volume, chance quality, shot location and finishing efficiency.
3. xG is used to measure chance quality.
4. Shot maps explain where dangerous chances happen.
5. Goals minus xG explains finishing efficiency.
6. The interactive dashboard lets users filter by team, match, player, outcome, chance quality and time.
7. The same dataset is used for both GDV and IVI, so the project is reproducible and coherent.

## Critical remaining actions before submission

1. Pull the newest repo version locally:

```bash
git pull origin main
```

2. Run the dashboard once:

```bash
python dashboard/app_worldcup.py
```

3. Check that the dashboard opens at:

```text
http://127.0.0.1:8050
```

4. If required, export `reports/final_report_draft.md` as PDF.

5. If required, export the presentation as PDF.

6. Check whether the module requires GitLab instead of GitHub.

## Honest status

The technical GDV and IVI implementation is complete. The report drafts, evaluation material and README are prepared. The only potentially missing item is a real user evaluation with filled results if the instructor explicitly requires measured evaluation results.
