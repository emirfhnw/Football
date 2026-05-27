# Evaluation Summary – Coach Attack Explorer

## Purpose of the evaluation

The evaluation checks whether the Coach Attack Explorer supports its intended use case: helping users understand how teams create goals in major tournaments.

The dashboard is designed for coaches, football fans and beginner analysts. It should make professional goal attacks easier to inspect and compare. The evaluation therefore focuses on the full workflow: tournament selection, team selection, goal replay and tournament comparison.

## Evaluation method

The evaluation uses a small formative usability test. The aim is to find design problems and improve the dashboard, not to make statistically generalizable claims.

The method combines three parts:

1. Task-based testing
   Participants complete five concrete dashboard tasks.

2. Think-aloud observation
   Participants explain what they are doing and where they are confused.

3. System Usability Scale
   Participants rate the dashboard after completing the tasks.

## Participants

The planned evaluation uses 2 to 3 participants. Suitable participants are football fans, students or users with basic dashboard experience. They do not need to be professional analysts because the dashboard should be understandable without deep data-science knowledge.

## Test tasks

The evaluation uses five tasks:

1. Select a tournament and check that goal build-ups are loaded.
2. Select one team and one goal example.
3. Replay the selected attack and describe how the goal was created.
4. Use the tournament goal pattern charts to identify the most common build-up type.
5. Use the team style map and ranking table to compare the selected team with the tournament.

These tasks test the main interactions:

- dropdown filtering
- linked dashboard updates
- step-by-step replay
- pitch interpretation
- chart interpretation
- ranking interpretation
- details on demand

## What should be recorded

For each participant, the following information should be recorded:

- task completion for each of the five tasks
- main positive feedback
- main problem or confusion
- suggested improvement
- SUS answers from 1 to 5

The results can be stored in:

```text
evaluation/evaluation_results_template.csv
```

## Expected usability observations

The expected result is that participants can understand the replay quickly because it follows a familiar football pitch layout. The most likely difficulties are the meaning of the build-up categories and the ranking table. Users may need a short explanation that lower average passes means a more direct style, while higher values indicate longer build-up.

## Design improvements already reflected in the dashboard

During development, several improvements were made based on usability problems observed during internal testing:

- The dashboard was simplified so that the attack replay became the main entry point.
- The previous team information block was removed because it made the page too wide and did not support the main task directly.
- A local processed dataset was created to avoid long loading times during normal use.
- The pitch was resized and placed inside a stable card layout.
- The pitch was divided into build-up, progression and final-third zones to support tactical interpretation.
- The team style map was changed to show all teams in the selected tournament and highlight the selected team.
- A directness ranking with tournament finish was added so users can compare attacking style with tournament outcome.

## How the evaluation supports the IVI requirements

The evaluation demonstrates that the dashboard was not only implemented technically, but also tested against user tasks. It connects the interaction design with a concrete football analysis use case.

The project includes:

- a clear target user group
- concrete user tasks
- interactive filtering
- linked views
- replay and details on demand
- overview and comparison views
- evaluation material
- documented design improvements

## Short conclusion

The evaluation setup is intentionally small and realistic. It fits the project scope and checks whether the dashboard supports the intended coaching workflow. The final report should include the completed task results and a short explanation of the improvements made after feedback.