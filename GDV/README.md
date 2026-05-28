
# GDV Final Submission - Angriffsmuster aus WM-Daten

## Project title

Angriffsmuster aus der FIFA WM 2022 fuer Amateurtrainer

## Research question

Welche einfachen Angriffsmuster aus der FIFA WM 2022 koennen Amateurtrainer fuer das Training ableiten?

## Dataset

StatsBomb Open Data, FIFA World Cup 2022.

The analysis uses event data: shots, goals, successful passes before shots, carries, entries into the final third, event coordinates and expected goals (xG).

## Important data handling decisions

- Penalty shootouts are excluded because they are not normal attacking possessions.
- In-game penalties, free kicks and corners remain included because they are relevant attacking situations, but they are marked as set-piece context.
- The analysis is descriptive and does not claim causal effects.
- Event data does not include full off-ball movement or tactical instructions.

## Files for submission

```text
GDV/
├── README.md
├── data/
│   ├── gdv_final_third_entries.csv
│   ├── gdv_shot_sequences.csv
│   └── gdv_team_attack_summary.csv
├── evaluation/
│   ├── gdv_evaluation_tasks_final.md
│   ├── gdv_evaluation_results_final.csv
│   └── gdv_evaluation_summary_final.md
├── figures/
│   ├── 01_passes_before_shots_goals.png
│   ├── 02_conversion_by_pass_category.png
│   ├── 03_final_third_entry_outcomes.png
│   ├── 04_entry_method_outcome.png
│   ├── 05_goal_start_zone.png
│   ├── 06_team_directness_ranking.png
│   ├── 07_spain_final_third_entries_for.png
│   └── 08_formation_context_optional.png
├── notebooks/
│   └── EDA_GDV_final_abgabe.ipynb
└── report/
    ├── gdv_report_final_abgabe.docx
    └── gdv_report_final_abgabe.pdf
```

## How to run the notebook

Install the required packages in the project environment. The notebook uses:

```bash
pip install pandas numpy matplotlib statsbombpy
```

Then run:

```bash
jupyter notebook notebooks/EDA_GDV_final_abgabe.ipynb
```

The notebook creates processed tables and final figures in the GDV folder. If cached CSV files use an older schema, the notebook rebuilds the analysis tables so the set-piece and penalty-shootout handling is applied.

## Final report

Submit `GDV/report/gdv_report_final_abgabe.pdf` as the written report. The DOCX version is provided only for editing.

## Evaluation material

The evaluation material is aligned with the final figures in the report. The tasks cover pass categories, conversion rate, entries into the final third, entry method, start zones, team directness and the Spain use case.

## Notes

No separate pitch-slide file is required in this repository version. The final GDV submission consists of the notebook, report, figures, processed data, evaluation material and this README.
=======
# GDV – Goal Build-up Analysis

This folder contains the GDV part of the football visualization project.

## Project topic

The project analyses how goals were created at the FIFA World Cup 2022. The main focus is on goal build-ups: whether goals were created through quick attacks with few completed passes or through longer passing sequences.

## Research question

How were goals created at the FIFA World Cup 2022: through quick attacks with few passes or through longer passing sequences?

## Dataset

The project uses StatsBomb Open Data for the FIFA World Cup 2022. The analysis is based on event data, especially goals, passes, shots, teams, players, timestamps, match information and event coordinates.

Important limitation: this is event data only. The project does not use tracking data and does not show off-ball movement.

## GDV focus

The GDV part focuses on static visualizations and their design rationale. The goal is to communicate the main patterns clearly before moving to the interactive IVI dashboard.

Main visual questions:

1. Which build-up type is most common before goals?
2. Do longer passing sequences also take more time?
3. Which teams scored after more direct or more patient build-ups?
4. Can selected goal sequences be explained visually?
5. How clear are the static figures for users?

## Folder structure

```text
GDV/
|-- README.md
|-- report/
|   |-- gdv_report_draft.md
|-- evaluation/
|   |-- gdv_evaluation_tasks.md
|   |-- gdv_evaluation_summary.md
|   |-- gdv_evaluation_analysis.md
|   |-- gdv_evaluation_results_template.csv
```

## Evaluation

The evaluation uses a small formative think-aloud test. Participants inspect the static figures and answer short interpretation tasks. The goal is not to prove a hypothesis statistically, but to check whether the figures are understandable and whether the design needs improvement.

## Final submission checklist for GDV

Before submission, the following items should be present:

- final GDV report as PDF
- final static figures included or referenced in the report
- evaluation tasks
- anonymised evaluation results or notes
- evaluation summary with design improvements
- clear references in APA style
- reproducible code or clear link to the preprocessing/analysis code

## Honest status

The GDV documentation and evaluation structure are prepared. The remaining critical task is to make sure the final figures are exported and referenced consistently in the final report PDF.
