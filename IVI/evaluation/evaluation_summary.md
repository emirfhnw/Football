# Evaluation Summary – Coach Attack Explorer

## Purpose of the evaluation

The evaluation checks whether the Coach Attack Explorer supports its intended use case: helping users understand how teams create goals in major tournaments.

The dashboard is designed for coaches, football fans and beginner analysts. It should make professional goal attacks easier to inspect and compare. The evaluation therefore focuses on the full workflow: tournament selection, team selection, goal replay and tournament comparison.

## Evaluation method

The evaluation used a small formative usability test. The aim was to find design problems and improve the dashboard, not to make statistically generalizable claims.

The method combined three parts:

1. Task-based testing
   Participants completed five concrete dashboard tasks.

2. Think-aloud observation
   Participants explained what they were doing and where they were confused.

3. System Usability Scale
   Participants rated the dashboard after completing the tasks.

## Participants

The evaluation was completed with three participants:

- P1: football fan with basic dashboard experience
- P2: student with little football analytics experience
- P3: amateur coach

This participant mix fits the target group because the dashboard should be understandable for users with football interest, but without expert data-analysis knowledge.

## Test tasks

The evaluation used five tasks:

1. Select a tournament and check that goal build-ups are loaded.
2. Select one team and one goal example.
3. Replay the selected attack and describe how the goal was created.
4. Use the tournament goal pattern charts to identify the most common build-up type.
5. Use the team style map and ranking table to compare the selected team with the tournament.

These tasks tested the main interactions:

- dropdown filtering
- linked dashboard updates
- step-by-step replay
- pitch interpretation
- chart interpretation
- ranking interpretation
- details on demand

## Task completion results

The task completion results were strong:

```text
Task 1: 3/3 completed
Task 2: 3/3 completed
Task 3: 3/3 completed
Task 4: 3/3 completed
Task 5: 2/3 completed fully, 1/3 completed partly
```

The only partly completed task was Task 5. One participant understood the general comparison workflow, but did not fully interpret the team style map and directness ranking without additional explanation.

## SUS results

The System Usability Scale results were:

```text
P1: 82.5
P2: 72.5
P3: 97.5
Average SUS: 84.2
```

The average SUS score indicates good usability for the tested workflow. The score also fits the qualitative feedback: the replay and main filters were easy to use, while the comparison view needed clearer explanation.

## Qualitative feedback

The most positive feedback concerned the attack replay. Participants liked that the attack could be followed step by step on a football pitch. The pitch zones helped users understand how the attack moved from build-up to final third.

The main usability issue was the interpretation of the directness ranking and build-up categories. One participant did not immediately understand that a lower directness rank means fewer completed passes before goals. Another participant noted that the team style map can become visually busy when many team labels are shown.

## Design improvements based on evaluation

Based on the evaluation, the most relevant improvements are:

- add or keep a short explanation above the ranking table
- keep the selected team clearly highlighted in the style map and ranking
- rely on hover details when many labels overlap in the team style map
- add a short explanation of quick attack, medium build-up and long build-up near the overview chart

Several of these points were already addressed during development. The final dashboard keeps the selected team highlighted and uses a simplified ranking explanation.

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

The evaluation shows that the Coach Attack Explorer supports the intended coaching workflow. Users were able to select a tournament, choose a team, replay a goal and interpret the main goal patterns. The main remaining challenge is explaining the directness ranking and reducing visual clutter in the team style map when many teams are displayed.