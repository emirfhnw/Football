# GDV Final Submission

## Project title

Attack patterns from the FIFA World Cup 2022 for amateur coaches

## Research question

Which simple attacking patterns from the FIFA World Cup 2022 can amateur coaches use as ideas for training?

## Dataset

This project uses StatsBomb Open Data from the FIFA World Cup 2022.

The analysis is based on event data. I mainly use regular shots, goals, successful passes before shots, carries, entries into the final third, event coordinates and expected goals.

## Short project idea

The goal of this project is not to copy professional football tactics directly into amateur football. The idea is more realistic: World Cup data can show repeated attacking patterns, and these patterns can be used as inspiration for simple training exercises.

The analysis focuses on questions such as:

1. How many completed passes happen before regular shots and goals?
2. Which build up categories are common, and which ones look more efficient?
3. Which teams create shots after entering the final third?
4. Which entry methods lead to shots most often?
5. What can be learned from Spain as a concrete team example?

## Important data decisions

Penalty shootouts, penalties and direct free kick shots are excluded from the main analysis. These situations do not describe normal build up play and would distort the short pass categories.

Corners and throw ins remain in the data because they can still continue as regular attacking situations.

The analysis is descriptive. It shows patterns in the data, but it does not prove that one attacking style is always better than another.

The data does not include full player tracking. This means that off ball runs, pressing structures and exact tactical instructions cannot be analysed.

## Folder structure

```text
GDV/
├── README.md
├── data/
│   ├── gdv_final_third_entries.csv
│   ├── gdv_shot_sequences.csv
│   └── gdv_team_attack_summary.csv
├── evaluation/
│   └── GDV_Evaluation.docx
├── figures/
│   ├── 01_build_up_volume_and_goals.png
│   ├── 02_build_up_efficiency_conversion_xg.png
│   ├── 03_final_third_entry_outcomes.png
│   ├── 04_entry_method_outcome.png
│   ├── 05_goal_start_zone.png
│   ├── 06_team_directness_ranking.png
│   └── 07_spain_final_third_entries_for.png
├── notebooks/
│   └── EDA_GDV_final_abgabe.ipynb
└── report/
    ├── GDV_Report_Attack_Patterns_Final.docx
    └── GDV_Report_Attack_Patterns_Final.pdf
```

## How to run the notebook

Install the required packages:

```bash
pip install pandas numpy matplotlib statsbombpy jupyter
```

Then open the notebook:

```bash
jupyter notebook notebooks/EDA_GDV_final_abgabe.ipynb
```

Run all cells from top to bottom. The notebook creates the processed CSV files and the final figures inside the GDV folder.

If the processed CSV files already exist, the notebook can load them again to avoid downloading all StatsBomb events each time. If the data handling is changed, rebuild the tables once and then save the notebook again.

## Final report

The final written report is saved here:

```text
GDV/report/GDV_Report_Attack_Patterns_Final.pdf
```

The Word version is included for editing:

```text
GDV/report/GDV_Report_Attack_Patterns_Final.docx
```

## Evaluation material

The evaluation document is stored here:

```text
GDV/evaluation/GDV_Evaluation.docx
```

It documents the short formative evaluation with two football players and the improvements made after their feedback.

## Final notes

This GDV submission contains the notebook, processed data, final figures, report and evaluation material.

The project should be read as an exploratory visualization project. The results are useful for discussing attacking ideas, but they should not be treated as fixed tactical rules.
