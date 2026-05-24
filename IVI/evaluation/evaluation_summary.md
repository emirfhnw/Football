# Evaluation Summary – FIFA World Cup 2022 Shot Quality Explorer

## Purpose of the evaluation

The goal of the evaluation is to check whether the interactive dashboard helps users explore shot quality, shot locations and finishing efficiency in the FIFA World Cup 2022.

The evaluation is formative. This means the goal is not to prove that the dashboard is perfect, but to find usability problems and improve the design.

## Evaluation method

The evaluation uses three simple methods:

1. **Task-based testing**  
   Participants solve concrete dashboard tasks.

2. **Think-aloud observation**  
   Participants explain what they are doing and where they are confused.

3. **System Usability Scale (SUS)**  
   Participants rate the usability of the dashboard after completing the tasks.

The evaluation material is stored in:

- `evaluation/evaluation_tasks.md`
- `evaluation/sus_questionnaire.md`
- `evaluation/evaluation_results_template.csv`

## Participants

The planned evaluation uses 3 to 5 participants. Suitable participants are:

- football fans
- students
- people with basic dashboard experience
- people without deep football analytics knowledge

The participants do not need to be professional analysts. This fits the target user group of the dashboard.

## Test tasks

The evaluation uses five tasks:

1. Find the team with the highest total xG in the tournament.
2. Select Argentina and describe its shot quality.
3. Select Serbia vs Switzerland and compare both teams.
4. Filter high-quality chances and describe where these chances usually occur on the pitch.
5. Find one player with high total xG and inspect his shots.

These tasks test whether users can use the main dashboard functions:

- filters
- KPI cards
- shot map
- timeline
- xG chart
- player chart
- hover details

## Expected results

The expected result is that users can complete the main tasks without major support. Some users may need a short explanation of xG because expected goals is not a common term for everyone.

Expected observations:

- Users should quickly understand the team and match filters.
- Users should use the KPI cards for quick comparison.
- Users should use the shot map to understand spatial patterns.
- Users may need help understanding chance quality categories.
- Users may ask what xG means.

## Design improvements based on expected feedback

The following improvements are planned or already considered:

### 1. Add a short xG explanation

A short explanation should be visible in the dashboard so users understand that xG estimates the probability that a shot becomes a goal.

### 2. Make goal markers visually clear

Goals should be easy to identify on the shot map and timeline. A different marker symbol helps users notice them quickly.

### 3. Keep filters simple

The dashboard should not contain too many advanced settings. The current filters are enough for the project scope:

- team
- match
- player
- shot outcome
- chance quality
- minute range

### 4. Use linked views

All charts should update together when filters are changed. This helps users understand that every view represents the same selected data.

### 5. Support overview and detail

The dashboard should start with the full tournament overview and allow users to move to one team, match or player. This follows the idea:

```text
overview first, filter, details on demand
```

## How the evaluation supports the IVI requirements

The evaluation checks whether the interaction design actually supports the user tasks. It also shows that the design was not only built once, but reflected and prepared for improvement.

This supports the IVI requirements because the project includes:

- a clear use case
- user tasks
- interactive filtering
- linked visualizations
- details on demand
- usability evaluation
- design improvement ideas

## Short conclusion

The evaluation plan is intentionally small and realistic. It fits the project scope and helps identify whether the dashboard is understandable for users. The results can be used in the final report to explain how the dashboard was evaluated and how the design can be improved.
