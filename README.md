# FIFA World Cup 2022 Goal Build-up Analysis

This project analyses how goals were created during the FIFA World Cup 2022 using StatsBomb Open Data.

The focus is on goal build-ups: successful passes in the same possession before a goal, attack duration, finishing efficiency and tournament progress.

## Module focus

This repository currently contains the GDV part of the project.

- **GDV – Fundamentals of Data Visualization:** static visual analysis, design reasoning and communication
- **IVI – Interactive Visualization:** planned next step based on the same goal build-up data

## Research question

**How are goals created at the FIFA World Cup 2022: through quick attacks with few passes or through longer passing sequences?**

Additional question:

**Does a team’s goal build-up style relate to finishing efficiency and tournament progress?**

## Use case

A coach, analyst or football fan wants to understand how goals are created. The goal is not only to know who scored, but how the ball moved before the goal.

The analysis answers:

- How many successful passes happen before a goal?
- Are goals more often created through quick, medium or long build-ups?
- Which teams score after more direct attacks?
- Which teams score after longer passing sequences?
- Are more passes before a goal also linked to longer attack duration?
- Is there a visible relationship between finishing efficiency and tournament progress?
- What does a concrete Spain goal build-up look like as a case study?

## Data source

The project uses StatsBomb Open Data through the `statsbombpy` Python package.

The analysed competition is:

```text
FIFA World Cup 2022
competition_id = 43
season_id = 106
```

Relevant event data:

- passes
- shots
- goals
- possessions
- pitch coordinates
- match information
- tournament stages

## Method

For each goal, the notebook identifies the same possession phase that directly led to the goal. Within this possession, it counts all successful passes by the scoring team before the shot.

Build-ups are grouped into three categories:

- **Quick:** 0 to 3 successful passes before the goal
- **Medium:** 4 to 7 successful passes before the goal
- **Long:** 8 or more successful passes before the goal

The analysis also adds team-level shot data and tournament-stage information to compare build-up style with finishing efficiency and tournament progress.

## Repository structure

```text
Football/
├── data/
│   └── processed/
│       ├── goal_buildups.csv
│       ├── goal_buildup_passes.csv
│       └── team_tournament_context.csv
├── notebooks/
│   └── 01_goal_buildup_gdv.ipynb
├── reports/
│   └── figures/
│       ├── goal_fig01_passes_before_goals.png
│       ├── goal_fig02_buildup_types.png
│       ├── goal_fig04_passes_vs_duration.png
│       ├── goal_final_01_team_buildup_style.png
│       ├── goal_final_02_efficiency_stage.png
│       ├── goal_final_03_direct_vs_patient.png
│       ├── goal_final_04_buildup_type_share.png
│       └── goal_fig13_spain_case_study.png
├── requirements.txt
└── README.md
```

## Setup

Install the required Python packages from the repository root:

```bash
pip install -r requirements.txt
```

## Run the GDV notebook

Open the notebook:

```text
notebooks/01_goal_buildup_gdv.ipynb
```

Then run all cells from top to bottom.

The notebook creates the processed data files and saves the final figures in:

```text
reports/figures/
```

## Final GDV figures

The final report should focus on these figures:

```text
goal_fig01_passes_before_goals.png
goal_fig02_buildup_types.png
goal_fig04_passes_vs_duration.png
goal_final_01_team_buildup_style.png
goal_final_02_efficiency_stage.png
goal_final_03_direct_vs_patient.png
goal_final_04_buildup_type_share.png
goal_fig13_spain_case_study.png
```

The heatmaps were used during exploration, but they are not central to the final argument because they were less directly interpretable for the research question.

## Main interpretation

The analysis separates goal creation into pass count, build-up duration, finishing efficiency and tournament progress.

The goal is not to claim that one playing style is always better. Instead, the visualizations show that different teams created goals in different ways. Some goals were created through quick direct attacks, while others came after longer passing sequences.

Finishing efficiency and tournament progress are added as context. They help check whether more efficient teams tended to progress further, but this is interpreted as an association, not as causation.

## Limitations

The analysis is based on event data, not tracking data. Therefore, it shows ball actions such as passes and shots, but not the full movement of all players.

The possession field is used to identify the goal build-up phase. This is a reasonable approximation, but it is still a simplification of real match dynamics.

Team-level comparisons should be interpreted carefully because some teams scored fewer goals than others, which creates smaller samples.
