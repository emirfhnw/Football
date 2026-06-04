# GDV Final Submission

## Project title

Attack patterns from the FIFA World Cup 2022 for amateur coaches

## Research question

Which simple attacking patterns from the FIFA World Cup 2022 can amateur coaches use as ideas for training?

## Project idea

This project is an exploratory data visualization project for the GDV module. The goal is not to copy professional World Cup tactics directly into amateur football. Instead, the project uses event data to identify simple attacking patterns that can be discussed as practical training ideas.

The analysis focuses on regular attacking situations, completed passes before shots, entries into the final third, chance quality and a detailed Spain case study.

The project is descriptive. It shows patterns in the data, but it does not prove that one attacking style is always better than another.

## Dataset

The project uses StatsBomb Open Data from the FIFA World Cup 2022.

The analysis is based on event data. The most important data fields are:

- regular shots
- goals
- completed passes before shots
- carries
- entries into the final third
- shot and event coordinates
- expected goals, also called xG
- teams, players, matches and timestamps

The dataset does not include full player tracking. This means that off ball runs, pressing structures and exact tactical instructions cannot be analysed.

## Main analysis questions

The notebook and report focus on these questions:

1. How many completed passes happen before regular shots and goals?
2. Which pass combination categories are common?
3. Which categories look more efficient?
4. Which teams create shots after entering the final third?
5. Which entry methods lead to shots most often?
6. What can be learned from Spain as a concrete team example?

## Important data decisions

Penalty shootouts, penalties and direct free kick shots are excluded from the main analysis. These situations do not describe normal build up play and would distort the short pass categories.

Corners and throw ins remain in the data because they can still continue as regular attacking situations.

The pass combination categories used in the main tournament analysis are:

- 0 to 3 completed passes
- 4 to 6 completed passes
- 7 to 9 completed passes
- 10 or more completed passes

The Spain case study additionally uses a simplified grouping:

- 0 to 2 completed passes
- 3 to 6 completed passes
- 7 or more completed passes

This simplified grouping is used only to make the Spain specific plots easier to read.

## Final visualizations

The final figures are saved in the `figures/` folder.

The main figures are:

1. Regular shots and goals by build up category
2. Build up efficiency by pass category
3. Shot and goal rates after final third entries
4. Entry method and outcome
5. Start zone of goal attacks by pass category
6. Team directness as a style comparison
7. Original Spain final third plot before redesign
8. Spain chance quality by final third entry lane
9. Spain shots after pass combinations
10. Numbered Spain pass sequences leading to goals

After the final pitch and the evaluation feedback, the original green Spain final third plot was redesigned. The first version had too much visual noise because it combined zones, lines, points and labels in one pitch view. The final version separates the Spain analysis into clearer views: pass sequences, finishing outcome and final third entry lane quality.

## Folder structure

The current GDV folder contains the following main files and folders:

```text
GDV/
├── README.md
├── data/
│   ├── final_third_entries.csv
│   ├── formation_context.csv
│   ├── formations.csv
│   ├── gdv_final_third_entries.csv
│   ├── gdv_shot_sequences.csv
│   ├── gdv_team_attack_summary.csv
│   ├── goal_buildup_passes.csv
│   ├── goal_buildups.csv
│   ├── team_entry_summary.csv
│   ├── team_match_formations.csv
│   └── team_tournament_context.csv
├── evaluation/
│   ├── Aufgaben_Ivan_batista.docx
│   ├── Aufgaben_Yannick_Geiger.docx
│   └── GDV_Evaluation.docx
├── figures/
│   ├── 01_build_up_volume_and_goals.png
│   ├── 02_build_up_efficiency_conversion_xg.png
│   ├── 03_final_third_entry_outcomes.png
│   ├── 04_entry_method_outcome.png
│   ├── 05_goal_start_zone.png
│   ├── 06_team_directness_ranking.png
│   ├── 07_spain_final_third_entries_for.png
│   ├── 08_spain_lane_ranking_clean_final.png
│   ├── 09_spain_pass_combinations_goals_clean_final.png
│   └── 10_spain_numbered_pass_stafetten_small_multiples.png
├── notebooks/
│   └── Analyse.ipynb
├── report/
│   ├── GDV_PP.pptx
│   └── Report.docx
└── Idea/
    └── idee.png
```



## How to run the notebook

Install the required packages:

```bash
pip install pandas numpy matplotlib statsbombpy jupyter
```

Then open the notebook:

```bash
jupyter notebook notebooks/Analyse.ipynb
```

Run all cells from top to bottom.

The notebook creates or loads the processed CSV files and saves the final figures inside the GDV folder. If the processed CSV files already exist, the notebook can reuse them to avoid downloading and processing all StatsBomb events again.

## Final report and presentation

The final written report is stored in the `report/` folder:

```text
GDV/report/Report.docx
```

The final presentation is also stored in the `report/` folder:

```text
GDV/report/GDV_PP.pptx
```

## Evaluation material

The evaluation material is stored in the `evaluation/` folder:

```text
GDV/evaluation/Aufgaben_Ivan_batista.docx
GDV/evaluation/Aufgaben_Yannick_Geiger.docx
GDV/evaluation/GDV_Evaluation.docx
```

The evaluation was done as a small formative check with two football players. The goal was to see whether the visualizations were understandable and whether any plots created confusion.

The most important feedback concerned the original Spain final third plot. It was considered too overloaded, so the Spain analysis was split into clearer plots.

## Limitations

This project has several limitations:

- The analysis uses event data, not tracking data.
- Off ball movement and pressing structures cannot be analysed.
- The results are descriptive and do not prove causality.
- The Spain case study is one team example and should not be generalized to all teams.
- The results are useful as training discussion points, not as fixed tactical rules.

## Final notes

This GDV submission contains the notebook, processed data, final figures, report, presentation and evaluation material.

The project should be read as an exploratory visualization project. The results can help amateur coaches discuss attacking ideas such as pass combinations, final third entries and chance creation, but they should not be treated as universal football rules.
