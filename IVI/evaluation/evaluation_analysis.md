# Evaluation Analysis – Coach Attack Explorer

## Current status

This file documents the completed evaluation analysis for the Coach Attack Explorer. The dashboard was evaluated with three participants using a task-based test, think-aloud observation and a short SUS questionnaire.

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

The evaluation was designed as a small formative usability test. Three participants completed five dashboard tasks and gave feedback after the test.

The participants represented realistic target users:

- P1: football fan with basic dashboard experience
- P2: student with little football analytics experience
- P3: amateur coach

The test was not intended to prove statistical significance. Its purpose was to check whether the dashboard workflow is understandable and whether the visualizations support the intended analysis tasks.

## Evaluation tasks

The evaluation used five tasks:

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

## Task completion

Task completion was high:

```text
Task 1: 3/3 completed
Task 2: 3/3 completed
Task 3: 3/3 completed
Task 4: 3/3 completed
Task 5: 2/3 completed fully, 1/3 completed partly
```

The only partial result occurred in Task 5. One participant could compare the selected team with the tournament in general, but needed help to interpret the directness rank and the team style map.

## SUS score

The SUS scoring method was:

- odd-numbered questions: response minus 1
- even-numbered questions: 5 minus response
- sum adjusted scores
- multiply by 2.5

The results were:

```text
P1: 82.5
P2: 72.5
P3: 97.5
Average SUS: 84.2
```

The result indicates good usability for the tested workflow. The highest score came from the amateur coach, who found the replay useful for coaching situations. The lowest score came from the participant with little football analytics experience, mainly because the comparison view required more explanation.

## Qualitative feedback

The qualitative feedback showed three main themes.

First, the attack replay was easy to understand. Participants liked that the sequence was shown on a familiar football pitch and could be followed step by step.

Second, the build-up zones helped interpretation. Especially the transition from build-up to progression and final third made the attack easier to explain.

Third, the ranking and style map needed clearer explanation. The meaning of directness rank was not immediately obvious to every participant, and one participant noted that the team labels can overlap when many teams are shown.

## Improvements already made during development

Several improvements were made before and during the final dashboard iteration:

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

## Improvements derived from the evaluation

The evaluation led to the following final recommendations:

- keep the explanation above the directness ranking short and explicit
- explain that lower rank means fewer completed passes before goals
- keep the selected team highlighted in the style map and ranking table
- rely on hover details when team labels overlap
- add a short explanation of quick attack, medium build-up and long build-up near the overview chart

## Final report wording

The following paragraph can be used in the final report:

```text
The dashboard was evaluated with three participants using five task-based questions and a SUS questionnaire. Most participants completed the main workflow successfully. The replay was considered the most intuitive view because it directly shows the attacking sequence on the pitch. The main difficulty was understanding the directness ranking without a short explanation. Based on this feedback, the ranking description was simplified and the selected team was highlighted more clearly. The average SUS score was 84.2, which indicates good usability for the tested workflow.
```

## Conclusion

The evaluation shows that the Coach Attack Explorer supports the intended workflow. Users can select a tournament, choose a team, replay a goal attack and compare the team's style with the tournament. The main remaining limitation is that the comparison view needs clear labels and explanations, especially for users with little football analytics experience.