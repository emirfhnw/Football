# IVI Report Draft – FIFA World Cup 2022 Shot Quality Explorer

## Title page information

**Project title:** FIFA World Cup 2022 Shot Quality Explorer  
**Module:** Interactive Visualization (IVI)  
**Student:** Emir Can  
**Dataset:** StatsBomb Open Data, FIFA World Cup 2022  
**Dashboard file:** `dashboard/app_worldcup.py`  
**Research question:** How can an interactive dashboard help users explore shot quality, shot locations and finishing efficiency across teams, matches and players in the FIFA World Cup 2022?

---

## 1. Introduction and goal

The IVI part builds directly on the GDV analysis. In GDV, the shot data was explored with static visualizations. In IVI, the same prepared dataset is turned into an interactive dashboard.

The goal of the dashboard is to help users explore attacking quality in the FIFA World Cup 2022. Instead of showing only one fixed chart, the dashboard allows users to filter the data and compare teams, matches and players interactively.

The main IVI research question is:

**How can an interactive dashboard help users explore shot quality, shot locations and finishing efficiency across teams, matches and players in the FIFA World Cup 2022?**

This question is suitable for an interactive visualization because the dataset contains many teams, matches, players and shots. A static figure can only show one selected perspective, while an interactive dashboard allows the user to choose the perspective that is relevant for the current task.

---

## 2. Use case and target users

The target users are football fans, students and beginner analysts who want to understand offensive performance during the World Cup 2022.

The dashboard is designed for users who want to answer questions such as:

- Which team created the most shots?
- Which team had the highest total xG?
- Which teams were efficient in converting chances into goals?
- Where on the pitch did high-quality chances occur?
- Which players created the most dangerous shots?
- How did a specific match, such as Serbia vs Switzerland, look in terms of shot quality?

The dashboard supports both overview and detail. A user can start with all tournament shots and then filter down to one team, one match or one player.

---

## 3. Data basis

The IVI dashboard uses the same processed dataset as the GDV analysis:

- `data/processed/world_cup_2022_shots.csv`

The dataset was created by `src/build_worldcup_shots.py`. It contains all shot events from the FIFA World Cup 2022 that were available through StatsBomb Open Data.

Important columns used in the dashboard are:

- `team`
- `player`
- `match_label`
- `minute`
- `x` and `y`
- `shot_statsbomb_xg`
- `shot_outcome`
- `is_goal`
- `chance_quality`
- `distance_to_goal`

Using a prepared CSV file instead of loading directly from the API makes the dashboard faster, more stable and easier to reproduce.

---

## 4. Interaction design

The dashboard is built around the idea of **overview first, filter, then details on demand**.

### Overview

When the dashboard opens, all shots from the tournament are shown. The user immediately sees high-level KPI cards and the overall shot map.

### Filtering

The left side contains filters for:

- team
- match
- player
- shot outcome
- chance quality
- minute range

These filters update all charts at the same time. This creates linked views because every visualization is connected to the same filtered dataset.

### Details on demand

The user can hover over shots in the shot map and timeline. The hover tooltip shows detailed information such as player, team, match, minute, xG, outcome and chance quality.

This means the user does not need to read a large table. Details appear only when they are needed.

---

## 5. Dashboard components

The dashboard contains the following main components.

### KPI cards

The KPI cards show:

- Shots
- Goals
- Total xG
- xG per Shot
- Conversion Rate

These cards give a quick numerical overview of the current filtered selection.

### Interactive shot map

The shot map is the central visualization. It shows all shot locations on a football pitch. Position represents the real shot location, color represents teams, marker size represents xG and symbol distinguishes goals from non-goals.

This visualization is important because shot quality is strongly connected to spatial position.

### xG by team

This bar chart compares the total xG of the currently filtered data. It is useful for comparing attacking quality between teams.

### Shot timeline

The timeline shows when shots occurred during matches. It helps users understand whether dangerous moments were concentrated in certain phases.

### Top players by xG

This chart ranks players by total xG in the filtered data. It connects team-level performance to individual contributions.

### Shot outcomes

The outcome chart shows how many shots were goals, saved, blocked or off target. This helps explain finishing efficiency.

---

## 6. Design rationale

The dashboard uses simple and understandable visual encodings.

- **Position** is used for shot locations on the pitch.
- **Length** is used in bar charts to compare xG and player contributions.
- **Color** is used to separate teams.
- **Marker size** is used to represent xG.
- **Symbol shape** is used to distinguish goals from non-goals.

These design decisions make the dashboard easy to understand. The dashboard avoids unnecessary decoration and focuses on the user tasks.

The filters are placed on the left because users usually start by selecting what they want to explore. The KPI cards are placed at the top because they summarize the current selection. The shot map is large because spatial analysis is the most important part of this project.

---

## 7. Performance and reproducibility

The dashboard uses a preprocessed CSV file instead of loading StatsBomb data live. This has several advantages:

- the dashboard starts faster
- filters react quickly
- the dashboard works without repeated API calls
- results are reproducible
- the same data basis is shared between GDV and IVI

The processed dataset is created once with:

```bash
python src/build_worldcup_shots.py
```

The dashboard can then be started with:

```bash
python dashboard/app_worldcup.py
```

---

## 8. Evaluation plan

The evaluation is designed as a lightweight formative usability test. The goal is to check whether users can solve typical analysis tasks with the dashboard.

The evaluation material is stored in:

- `evaluation/evaluation_tasks.md`
- `evaluation/sus_questionnaire.md`
- `evaluation/evaluation_results_template.csv`

The planned test tasks are:

1. Find the team with the highest total xG.
2. Select Argentina and describe its shot quality.
3. Select Serbia vs Switzerland and compare both teams.
4. Filter high-quality chances and describe their pitch locations.
5. Find one player with high total xG and inspect his shots.

After completing the tasks, participants answer the SUS questionnaire. The results are then used to identify possible improvements.

---

## 9. Expected improvements after evaluation

Possible improvements after user feedback are:

- add a short xG explanation directly in the dashboard
- make goal markers larger
- improve default filter choices
- reduce visual clutter in the shot map
- add clearer labels for chance quality
- improve text instructions for first-time users

These improvements are realistic and directly connected to possible usability problems.

---

## 10. Limitations

The dashboard focuses only on shot events. This keeps the project understandable and focused, but it does not include other important football events such as passes, defensive actions or possession chains.

The dashboard uses xG values provided by StatsBomb. It does not create a new xG model. This is appropriate for the project scope but means that the interpretation depends on the existing xG values.

The dashboard is intended as an exploratory tool, not as a complete professional scouting platform.

---

## 11. Conclusion

The IVI dashboard turns the static GDV analysis into an interactive exploration tool. Users can filter the FIFA World Cup 2022 shot data by team, match, player, outcome, chance quality and time. The linked visualizations update together and help users understand shot quality, shot locations and finishing efficiency.

This makes the project suitable for both GDV and IVI. GDV explains the static analysis and visual design choices. IVI allows users to interactively explore the same data and answer their own questions.
