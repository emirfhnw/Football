# Evaluation Analysis – Current Status and Next Step

## Important note

This file documents the evaluation setup and the analysis structure. The actual user evaluation must still be completed with real participants before the final submission if the module explicitly requires measured results.

The repository already contains all required evaluation material:

- `evaluation/evaluation_tasks.md`
- `evaluation/sus_questionnaire.md`
- `evaluation/evaluation_results_template.csv`
- `evaluation/evaluation_summary.md`

## Planned evaluation setup

The evaluation is designed as a small formative usability test with 3 to 5 participants.

The participants should represent the intended target users:

- football fans
- students
- beginner analysts
- users with basic dashboard experience

The goal is to check whether users can use the dashboard to explore shot quality, shot locations and finishing efficiency in the FIFA World Cup 2022.

## Evaluation tasks

The evaluation uses five tasks:

1. Find the team with the highest total xG.
2. Select Argentina and describe its shot quality.
3. Select Serbia vs Switzerland and compare both teams.
4. Filter high-quality chances and describe where these chances usually occur on the pitch.
5. Find one player with high total xG and inspect his shots.

These tasks test the core IVI interactions:

- filtering
- linked views
- KPI interpretation
- shot map interpretation
- timeline interpretation
- hover details

## What to record

For each participant, record:

- whether each task was completed
- SUS answers from 1 to 5
- main positive feedback
- main usability problem
- suggested improvement

Use:

```text
evaluation/evaluation_results_template.csv
```

## Analysis method

### Task completion

For each task, calculate how many participants completed it.

Example format:

```text
Task 1: 3/3 completed
Task 2: 3/3 completed
Task 3: 2/3 completed
Task 4: 2/3 completed
Task 5: 3/3 completed
```

### SUS score

For each participant:

- odd questions: response minus 1
- even questions: 5 minus response
- sum adjusted scores
- multiply by 2.5

Then calculate the average SUS score.

### Qualitative feedback

Group observations into themes, for example:

- xG explanation unclear
- filters easy to understand
- shot map useful
- goal markers should be clearer
- too many points when no filter is selected

## Expected design improvements

Based on the planned evaluation, the most realistic improvements are:

1. Add a short explanation of xG directly in the dashboard.
2. Add a short user instruction explaining how to use the filters.
3. Make goal markers and chance quality easier to understand.
4. Keep the dashboard focused on shot quality instead of adding too many extra football metrics.

## Current implementation status

Some improvements are already implemented in the dashboard:

- prepared local CSV data for faster loading
- linked views through shared filters
- KPI cards for immediate overview
- filters for team, match, player, outcome, chance quality and minute range
- hover details for individual shots

## Final report wording after the real evaluation

After completing the evaluation with real participants, the final report should include a short paragraph like this:

```text
The dashboard was evaluated with X participants using five task-based questions and a SUS questionnaire. Most participants completed the tasks successfully. The main difficulty was understanding xG and chance quality without an explanation. Based on this feedback, an xG explanation was added to the dashboard and the user instructions were made clearer.
```

Replace `X` with the real number of participants and add the real SUS score.

## Conclusion

The evaluation structure is ready. The only missing step is to run the short test with real participants and insert the results into `evaluation/evaluation_results_template.csv` or a filled copy of that file.
