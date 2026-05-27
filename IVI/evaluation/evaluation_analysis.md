# Evaluation Analysis – Coach Attack Explorer

## Current status

This file documents the planned evaluation analysis for the Coach Attack Explorer. The dashboard is finished enough for a small formative evaluation. The next step is to run the task-based test with 2 to 3 real participants and enter the results into the results template.

The evaluation material is stored in:

- `evaluation/evaluation_tasks.md`
- `evaluation/sus_questionnaire.md`
- `evaluation/evaluation_results_template.csv`
- `evaluation/evaluation_summary.md`

## Dashboard goal

The dashboard helps users inspect how teams create goals in major football tournaments. It combines one detailed goal replay with overview and comparison views.

The main analysis question is:

> How do teams create goals, and how does their attacking style compare with other teams in the same tournament?

## Evaluation setup

The evaluation is designed as a small formative usability test with 2 to 3 participants. Participants should represent realistic users such as football fans, coaches, students or beginner analysts.

The test is not intended to prove statistical significance. Its purpose is to check whether the dashboard workflow is understandable and whether the visualizations support the intended analysis tasks.

## Evaluation tasks

The evaluation uses five tasks:

1. Select a tournament and confirm that goal build-ups are loaded.
2. Select one team and one goal example.
3. Replay the selected goal attack and describe how the goal was created.
4. Use the tournament goal pattern charts to identify the most common build-up type.
5. Use the team style map and ranking table to compare the selected team with the tournament.

These tasks test the core IVI interaction concepts:

- overview first
- filtering
- linked views
- details on demand
- visual comparison
- interpretation of encoded data

## What to record

For each participant, record:

- completion of each task
- where the participant hesitated
- whether the replay was understandable
- whether the directness ranking was understandable
- which view was most useful
- main positive feedback
- main usability problem
- suggested improvement
- SUS questionnaire answers

## Analysis method

### Task completion

For each task, count how many participants completed it.

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

- odd-numbered questions: response minus 1
- even-numbered questions: 5 minus response
- sum adjusted scores
- multiply by 2.5

Then calculate the average SUS score.

### Qualitative feedback

Group observations into themes, for example:

- tournament selection is easy to understand
- replay controls are intuitive
- build-up categories need a short explanation
- ranking table supports comparison
- labels in the team style map can overlap when many teams are shown

## Improvements already made during development

Several improvements were made before the final evaluation:

1. Static local dataset

The first dashboard versions loaded too slowly when full tournament data was loaded directly. The data was therefore preprocessed into local CSV files. This improved reliability and made the dashboard usable during presentation.

2. Simplified layout

Earlier versions contained too many sections and a wide team information table. This made the page harder to read. The layout was simplified so that the replay is the main entry point.

3. Clearer pitch visualization

The pitch was adjusted to stay inside its card and was divided into three tactical zones: build-up, progression and final third. This helps users interpret where the attack develops.

4. Tournament comparison

The team style map was changed to show all teams in the selected tournament and highlight the selected team. This supports comparison instead of showing only one isolated team.

5. Ranking with tournament finish

The ranking table was extended with tournament finish. This makes the use case stronger because users can compare directness with how far teams reached in the tournament.

## Expected final report wording after real evaluation

After completing the evaluation, the final report should include a paragraph like this with real numbers:

```text
The dashboard was evaluated with X participants using five task-based questions and a SUS questionnaire. Most participants completed the main workflow successfully. The replay was considered the most intuitive view because it directly shows the attacking sequence on the pitch. The main difficulty was understanding the directness ranking without a short explanation. Based on this feedback, the ranking description was simplified and the selected team was highlighted more clearly.
```

Replace `X` and the findings with the real evaluation results.

## Conclusion

The evaluation structure is ready. The missing step is to perform the short user test, fill in the results template and insert the real findings into the report.