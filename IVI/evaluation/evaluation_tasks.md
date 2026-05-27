# Evaluation Tasks – Coach Attack Explorer

## Purpose

These tasks evaluate whether the dashboard helps users understand how teams create goals in major tournaments. The evaluation focuses on the complete workflow: selecting a tournament, choosing a team, replaying a goal attack and comparing the team's attacking style with other teams in the tournament.

The evaluation is formative. The goal is not to prove that the dashboard is perfect, but to identify usability problems and improve the design before submission.

## Target users

The intended users are:

- football coaches
- football fans with tactical interest
- beginner analysts
- students with basic dashboard experience

The participants do not need expert football analytics knowledge. The dashboard should be understandable for users who know football, but are not professional data analysts.

## Procedure

1. Give the participant a short introduction:
   "This dashboard shows how teams create goals. Please choose a tournament, select a team, replay one goal attack and compare the team with the rest of the tournament."
2. Ask the participant to solve the tasks below while thinking aloud.
3. Observe where the participant hesitates, misunderstands labels or needs help.
4. After the tasks, ask the SUS questionnaire.
5. Record positive feedback, main problems and improvement ideas.

## Tasks

### Task 1 – Select a tournament

Choose one tournament from the tournament dropdown and check that the dashboard loads goal build-ups.

Expected interaction:

- open the tournament dropdown
- select one tournament
- wait until the dashboard updates
- read the number of available goal build-ups

What this tests:

- whether the entry point is understandable
- whether the user notices that the dashboard is tournament-based

### Task 2 – Select a team and goal example

Select one team and then choose one goal example from this team.

Expected interaction:

- use the team dropdown
- select one team
- use the goal example dropdown
- select one goal

What this tests:

- whether the filter workflow is clear
- whether the user understands that the replay is team-specific

### Task 3 – Replay the attack

Use the replay controls to inspect how the selected goal was created.

Expected interaction:

- use Play, Next or Jump to event
- identify at least one important action before the goal
- describe whether the attack was quick, medium or longer build-up

What this tests:

- whether the pitch replay is understandable
- whether users can follow the sequence step by step
- whether the build-up zones support interpretation

### Task 4 – Interpret tournament goal patterns

Use the tournament goal pattern charts to identify the most common build-up type in the selected tournament.

Expected interaction:

- inspect the build-up type chart
- compare quick, medium and long build-ups
- optionally inspect the passes vs duration scatterplot

What this tests:

- whether users understand the overview charts
- whether the KPI cards and chart labels are useful

### Task 5 – Compare team style with tournament outcome

Use the team style map and ranking table to compare the selected team with the rest of the tournament.

Expected interaction:

- find the selected team in the style map
- read whether it is more direct or more patient
- use the ranking table to see directness rank and tournament finish

What this tests:

- whether the comparison view supports the coaching use case
- whether users understand the link between attacking style and tournament finish

## Observation notes template

For each participant, record:

- Were all tasks completed?
- Which task caused hesitation?
- Was the replay understandable?
- Was the ranking understandable?
- Did the participant understand direct, balanced and patient build-up?
- Which view was most useful?
- Which label or interaction was confusing?
- What should be improved?

## Success criteria

The dashboard is considered understandable enough if most participants can:

- select a tournament without support
- select a team and goal example
- play through a goal sequence
- explain the selected team's build-up style
- use the ranking table to compare teams

## Planned design improvements after evaluation

Possible improvements based on expected feedback:

- simplify labels if users do not understand build-up categories
- make the selected team more visible in the style map and ranking
- reduce visual clutter in the team style map if labels overlap
- improve short instructions in the header
- keep the dashboard focused on goal build-ups instead of adding unrelated football metrics