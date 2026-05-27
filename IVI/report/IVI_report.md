# Coach Attack Explorer - IVI Report

## 1. Introduction

The Coach Attack Explorer is an interactive dashboard for analysing how teams create goals in major football tournaments. The project focuses on goal build-ups instead of general match statistics. The central idea is that a coach, football fan or beginner analyst should be able to select a tournament, choose a team, replay one goal attack and then compare this team's attacking style with the rest of the tournament.

The dashboard answers the following question:

> How do teams create goals in major tournaments, and how does their attacking style compare with their tournament outcome?

This question is useful because goals are easy to understand, but the attacking sequence before the goal is often more important for coaching. A replay of the build-up can show whether a goal came from a quick direct attack, a medium-length attack or a more patient build-up. The comparison views then help users see whether a team is an outlier or similar to other teams in the tournament.

## 2. Use case and target users

The main target user is a football coach or beginner match analyst. The dashboard is also understandable for football fans and students who are interested in tactical patterns.

The intended workflow is:

1. Select a tournament.
2. Select a team.
3. Select a goal example.
4. Replay the attack step by step on the pitch.
5. Inspect the tournament-level goal patterns.
6. Compare the selected team with other teams in the tournament.

The dashboard is not designed as a prediction model. It does not claim that one style automatically leads to success. Instead, it supports exploratory analysis. A user can observe examples, compare teams and create coaching ideas from professional match situations.

## 3. Data source and preprocessing

The project uses StatsBomb open event data. The raw event data contains ball actions such as passes, carries and shots. For the dashboard, the data was transformed into goal build-up sequences.

The final dashboard uses local preprocessed CSV files:

```text
IVI/data/processed/goals_df.csv
IVI/data/processed/build_up_events_df.csv
IVI/data/processed/team_efficiency_df.csv
```

A separate tournament list is stored in:

```text
IVI/data/raw/selected_tournaments.csv
```

This local setup was chosen because loading full StatsBomb tournaments during dashboard interaction was too slow and unstable for presentation. The data is therefore prepared once and then loaded locally by the dashboard. This improves reliability and makes the application reproducible.

The preprocessing creates two main levels of data. The first level is one row per analysed goal build-up. It contains information such as team, opponent, scorer, minute, number of completed passes before the goal, attack duration and build-up type. The second level is one row per event in the selected build-up sequence. This event table is used for the pitch replay.

The build-up style is derived from the number of completed passes before the goal:

- quick attack
- medium build-up
- long build-up

This classification is intentionally simple. It makes the dashboard easier to interpret and supports the coaching use case.

## 4. Dashboard design

The dashboard is structured around one main workflow. The user first chooses a tournament, then selects a team and a goal example. The selected goal is shown as an attack replay on a pitch.

### Attack Replay

The replay is the most important view. It shows the sequence of ball actions before the goal. Users can step through the attack with replay controls or jump to individual events. The pitch is divided into three zones:

- build-up
- progression
- final third

These zones help users understand where the attack started, how it progressed and where the final action happened. The side panel shows details about the current event, including player, action, team, scorer, completed passes, duration and build-up style.

### Tournament goal patterns

The overview charts summarize all analysed goals in the selected tournament. KPI cards show the number of analysed goals, average passes before goal, average attack duration and the most common build-up type.

The build-up type chart shows how many goals came from quick, medium or long attacks. The scatterplot shows the relationship between completed passes before the goal and attack duration. This helps users see whether longer attacks usually involve more passes and whether the selected goal is typical or unusual.

### Team style and tournament finish

The team style map compares all teams in the selected tournament. The x-axis shows the average number of completed passes before goals. Teams further left score more directly, while teams further right use more patient build-up. The y-axis shows how many analysed goals the team scored in the loaded data.

The selected team is highlighted so the user can quickly compare it with other teams. Below the map, the directness ranking orders teams by average completed passes before goals and also shows the tournament finish. This connects attacking style with tournament outcome.

## 5. Interaction design

The dashboard uses several interaction principles from information visualization.

First, the dashboard follows an overview-to-detail structure. Tournament-level charts give an overview, while the attack replay gives detail for one selected goal.

Second, the views are linked. Selecting a tournament changes the available teams and goals. Selecting a team updates the goal examples, the replay and the comparison views.

Third, the dashboard supports details on demand. The user can inspect individual events in the replay and hover over points in the charts.

Fourth, the visual design tries to reduce unnecessary complexity. Earlier versions contained wider information sections that made the page difficult to read. These were removed so that the replay and comparison views stay central.

## 6. Evaluation method

The dashboard was evaluated with three participants using a small formative usability test. The goal was to check whether users understand the workflow and whether the visualizations support the intended coaching tasks.

The participants were:

- P1: football fan with basic dashboard experience
- P2: student with little football analytics experience
- P3: amateur coach

The evaluation tasks were:

1. Select a tournament and check that goal build-ups are loaded.
2. Select one team and one goal example.
3. Replay the selected attack and describe how the goal was created.
4. Use the tournament goal pattern charts to identify the most common build-up type.
5. Use the team style map and ranking table to compare the selected team with the rest of the tournament.

After the tasks, participants answered the System Usability Scale questionnaire. In addition, qualitative feedback was recorded.

## 7. Evaluation results

Task completion was high:

```text
Task 1: 3/3 completed
Task 2: 3/3 completed
Task 3: 3/3 completed
Task 4: 3/3 completed
Task 5: 2/3 completed fully, 1/3 completed partly
```

The only partial result occurred in Task 5. One participant understood the general comparison workflow, but needed help to interpret the directness rank and the team style map.

The SUS results were:

```text
P1: 82.5
P2: 72.5
P3: 97.5
Average SUS: 84.2
```

The average SUS score indicates good usability for the tested workflow. The strongest feedback concerned the attack replay. Participants found it easy to follow the goal sequence because it was shown on a familiar football pitch. The pitch zones also helped users explain how the attack moved from build-up to progression and final third.

The main usability issue was the interpretation of the directness ranking and build-up categories. One participant did not immediately understand that a lower directness rank means fewer completed passes before goals. Another participant mentioned that the team style map can become visually busy when many labels are shown.

## 8. Design iteration

Several design problems appeared during development and evaluation.

The first problem was loading time. Loading many StatsBomb matches directly during dashboard use made the application unreliable. The solution was to create local processed CSV files and use them during normal dashboard operation.

The second problem was layout complexity. Earlier versions had too many sections and a wide team tournament information table. This made the dashboard harder to scan. The final design removed this section and focused on the replay, overview charts and comparison ranking.

The third problem was the team comparison. A previous version only showed limited team information and did not clearly compare all tournament teams. The final version uses a team style map with all teams in the selected tournament and highlights the selected team.

The fourth problem was the interpretation of team style. A pure directness table did not show whether teams were successful in the tournament. The ranking was therefore extended with tournament finish. This makes the use case stronger because users can compare attacking style with outcome.

The evaluation also showed that the comparison view needs clear explanation. Therefore, the dashboard keeps the selected team highlighted and uses a short explanation above the ranking table. Hover details are used to support interpretation when team labels overlap.

## 9. Limitations

The dashboard has clear limitations.

It only analyses goal build-ups, not every attack in a match. This means the dashboard focuses on successful attacking examples and does not describe all offensive behaviour.

The data contains ball actions, but not all off-ball runs and tactical movements. Therefore, the replay cannot fully explain why a defence was opened.

The build-up classification is simplified. Number of completed passes and duration are useful indicators, but they do not capture every tactical detail.

The dashboard should not be used to claim that one attacking style is always better. A direct team can be successful or unsuccessful, and a patient team can also be successful or unsuccessful. The dashboard supports exploration, not causal proof.

## 10. Conclusion

The Coach Attack Explorer provides an interactive way to inspect goal attacks and compare team styles across tournaments. Its strongest part is the connection between a concrete goal replay and tournament-level comparison. This makes the dashboard useful for coaching discussions because users can move from one professional example to a broader tournament pattern.

The evaluation shows that the dashboard supports the intended workflow. Users can select a tournament, choose a team, replay a goal attack and compare the team's style with the tournament. The final result is not a prediction system, but a focused exploratory dashboard for understanding how teams create goals.