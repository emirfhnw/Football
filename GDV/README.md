# GDV Final Submission

## Project title

Attack patterns from the FIFA World Cup 2022 for amateur coaches

## Research question

Which simple attacking patterns from the FIFA World Cup 2022 can amateur coaches use as ideas for training?

## Dataset

This project uses StatsBomb Open Data from the FIFA World Cup 2022.

The analysis is based on event data. I mainly use shots, goals, successful passes before shots, carries, entries into the final third, event coordinates and expected goals.

## Short project idea

The goal of this project is not to copy professional football tactics directly into amateur football. The idea is more realistic: World Cup data can show repeated attacking patterns, and these patterns can be used as inspiration for simple training exercises.

The analysis focuses on questions such as:

1. Do shots and goals happen more often after few passes or after longer passing sequences?
2. Which pass categories have a higher conversion rate?
3. Which teams create shots after entering the final third?
4. Which entry methods lead to shots most often?
5. What can be learned from Spain as a concrete team example?

## Important data decisions

Penalty shootouts are excluded because they are not normal attacking possessions.

Penalties, free kicks and corners during regular match play are kept in the data because they are still attacking situations inside the game. They are treated carefully in the interpretation.

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
│   └── 08_formation_context.png
├── notebooks/
│   └── EDA_GDV_final_abgabe.ipynb
└── report/
    ├── gdv_report_final_abgabe.docx
    └── gdv_report_final_abgabe.pdf
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

If older processed CSV files already exist, the notebook can rebuild the analysis tables so that the final data handling is applied.

## Final report

The final written report is saved here:

```text
GDV/report/gdv_report_final_abgabe.pdf
```

The Word version is only included for editing:

```text
GDV/report/gdv_report_final_abgabe.docx
```

## Evaluation material

The evaluation material is stored in the evaluation folder.

It includes the final evaluation tasks, the anonymised participant results and a short summary of what was improved after the feedback.

The evaluation was used to check whether the final static figures were understandable for football interested readers.

## Final notes

This GDV submission contains the notebook, processed data, final figures, report and evaluation material.

The project should be read as an exploratory visualization project. The results are useful for discussing attacking ideas, but they should not be treated as fixed tactical rules.
