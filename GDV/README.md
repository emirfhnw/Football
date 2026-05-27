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