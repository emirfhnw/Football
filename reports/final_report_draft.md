# Final Report Draft – FIFA World Cup 2022 Shot Quality Explorer

## Title page information

**Project title:** FIFA World Cup 2022 Shot Quality Explorer  
**Modules:** Fundamentals of Data Visualization (GDV) and Interactive Visualization (IVI)  
**Student:** Emir Can  
**Dataset:** StatsBomb Open Data, FIFA World Cup 2022  
**Repository:** Football  
**Dashboard:** `dashboard/app_worldcup.py`

---

## 1. Introduction

This project analyses shot quality, shot locations and finishing efficiency in the FIFA World Cup 2022. The aim is not only to count goals or shots, but to understand how dangerous the created chances were and how attacking performance differs between teams, matches and players.

The central research question is:

**How do shot quality, shot locations and finishing efficiency differ between teams and matches in the FIFA World Cup 2022?**

The project is divided into two connected parts. The GDV part uses static visualizations to explore and explain the dataset. The IVI part turns the same data into an interactive dashboard that allows users to filter and explore the tournament themselves.

---

## 2. Use case and target users

The target users are football fans, students and beginner analysts who want to understand offensive performance during the FIFA World Cup 2022. The dashboard and visual analysis support questions such as:

- Which teams produced the most shots?
- Which teams had the highest total expected goals?
- Which teams were most efficient in converting chances into goals?
- Where on the pitch did high-quality chances occur?
- Which players contributed most to attacking danger?
- How does one specific match compare to the tournament overview?

The interactive dashboard supports these questions by allowing the user to move from an overview of the whole tournament to a specific team, match or player.

---

## 3. Dataset

The project uses StatsBomb Open Data for the FIFA World Cup 2022. The analysis focuses only on shot events. This keeps the scope clear and makes the project easier to explain and reproduce.

The processed dataset contains:

- 64 matches
- 32 teams
- 1494 shots
- 195 goals

The most relevant variables are:

- `team`
- `player`
- `match_id`
- `match_label`
- `minute`
- `x` and `y` shot coordinates
- `shot_statsbomb_xg`
- `shot_outcome`
- `shot_body_part`
- `shot_type`
- `play_pattern`

Expected goals, abbreviated as xG, estimates how likely a shot is to become a goal. It is used as the main variable for shot quality.

---

## 4. Data preprocessing

The preprocessing is implemented in `src/build_worldcup_shots.py`. The script loads all FIFA World Cup 2022 matches from StatsBomb Open Data, extracts only shot events and creates a clean CSV file for both GDV and IVI.

The preprocessing steps are:

1. Load all FIFA World Cup 2022 matches.
2. Load event data for every match.
3. Filter the event data to keep only shots.
4. Add match information such as home team, away team, score and match label.
5. Extract x and y coordinates from the shot location field.
6. Convert xG and minute values to numeric data types.
7. Calculate distance from the shot location to the goal centre.
8. Create `is_goal` from the shot outcome.
9. Create `chance_quality` from xG.

The chance quality categories are:

- **Low:** xG below 0.05
- **Medium:** xG from 0.05 to below 0.20
- **High:** xG of 0.20 or higher

The final processed files are:

- `data/processed/world_cup_2022_shots.csv`
- `data/processed/world_cup_2022_team_summary.csv`
- `data/processed/world_cup_2022_player_summary.csv`

---

## 5. GDV: Static visual analysis

The GDV part focuses on static visualizations and design reasoning. The figures are generated with `src/gdv_worldcup_analysis.py` and saved in `reports/figures/`.

### Figure 1: Top 10 teams by shots

This bar chart shows which teams produced the highest shot volume. Bar charts are suitable here because the task is a direct comparison between teams. The value is encoded by length, which is easy to compare.

Argentina had the highest shot volume with 110 shots.

### Figure 2: Top 10 teams by total xG

This bar chart compares teams by total expected goals. Total xG gives more context than shot count because it includes the estimated quality of each shot.

Argentina also had the highest total xG with 20.99.

### Figure 3: Goals compared with xG

This figure compares actual goals and expected goals for the highest-xG teams. It helps identify which teams scored more or fewer goals than expected based on chance quality.

This supports the analysis of finishing efficiency.

### Figure 4: Chance quality categories by team

This chart groups shots into low, medium and high-quality chances. The categories make xG easier to interpret for users who are not familiar with football analytics.

### Figure 5: Shot map of all World Cup 2022 shots

The shot map shows where shots occurred on the pitch. This is important because football shots are spatial events. High-quality chances are usually closer to goal and more central.

### Figure 6: Distance to goal vs xG

This scatterplot shows the relationship between shot distance and xG. It confirms that shots closer to goal usually have a higher chance of becoming a goal, while also showing that distance is not the only factor.

### Figure 7: Top players by total xG

This bar chart ranks players by total xG. It connects team-level attacking performance to individual players.

### Figure 8: Serbia vs Switzerland case study

This figure connects the tournament overview to one concrete match. It combines a shot map and a timeline for Serbia vs Switzerland, making the project easier to explain and preparing the logic for the interactive dashboard.

---

## 6. GDV design rationale

The static visualizations were selected based on the type of question being answered.

- Bar charts are used for team and player comparisons.
- Scatterplots are used for relationships between quantitative variables.
- The shot map is used because pitch position is meaningful for football data.
- Marker size represents xG when approximate magnitude is useful.
- Different symbols are used to highlight goals.
- The analysis moves from overview to detail.

The goal is to keep the visualizations understandable, avoid unnecessary decoration and make the main message of each figure clear.

---

## 7. IVI: Interactive dashboard

The IVI part is implemented in `dashboard/app_worldcup.py`. The dashboard uses the same prepared dataset as the GDV analysis. This makes the project reproducible and avoids repeated API calls.

The dashboard includes:

- KPI cards for shots, goals, total xG, xG per shot and conversion rate
- team filter
- match filter
- player filter
- shot outcome filter
- chance quality filter
- minute range slider
- interactive shot map
- shot timeline
- xG by team chart
- top players by xG chart
- shot outcome chart
- hover details for individual shots

The dashboard is based on the principle:

```text
overview first, filter, then details on demand
```

When the dashboard opens, the user sees the full tournament overview. Then the user can filter down to a team, match or player. Hover tooltips provide details only when needed.

---

## 8. IVI interaction design rationale

The dashboard supports interaction because the dataset contains many teams, matches, players and shots. A single static chart cannot show all relevant perspectives at once.

The filters allow users to define their own view. All charts update together, which creates linked views. This helps users understand that the KPI cards, shot map, timeline and bar charts are based on the same filtered data.

The shot map is the central view because spatial location is the most important part of shot quality. The KPI cards provide a fast numerical summary. The timeline adds temporal context. The player chart helps identify individual contributions.

The dashboard also contains a short xG explanation and user instructions. This was added because xG and chance quality may not be clear for all users.

---

## 9. Performance and reproducibility

The dashboard uses a preprocessed CSV file instead of loading live data from the StatsBomb API. This improves performance and stability.

The full project can be reproduced with:

```bash
pip install -r requirements.txt
python src/build_worldcup_shots.py
python src/gdv_worldcup_analysis.py
python dashboard/app_worldcup.py
```

This creates the processed data, generates the GDV figures and starts the IVI dashboard.

---

## 10. Evaluation

The evaluation material is stored in the `evaluation/` folder. The planned evaluation uses:

- task-based user testing
- think-aloud observation
- SUS questionnaire
- qualitative feedback

The evaluation tasks are:

1. Find the team with the highest total xG.
2. Select Argentina and describe its shot quality.
3. Select Serbia vs Switzerland and compare both teams.
4. Filter high-quality chances and describe their locations.
5. Find one player with high total xG and inspect his shots.

The evaluation setup is ready, but the final measured results still need to be added after testing with real participants. The current dashboard already includes improvements that address expected usability issues: an xG explanation, clearer user instructions and a linked-views explanation.

---

## 11. Limitations

The project focuses only on shots. This keeps the analysis focused and understandable, but it excludes other important football events such as passes, defensive actions, pressing and possession sequences.

The xG values are taken from StatsBomb and are not calculated by a custom model. This is appropriate for the module scope, but the analysis depends on the existing xG values.

The dashboard is designed as an exploratory visualization tool, not as a full professional scouting platform.

---

## 12. Conclusion

This project shows how shot data from the FIFA World Cup 2022 can be used to compare attacking quality between teams, matches and players. The GDV part provides static visualizations and design reasoning. The IVI part turns the same analysis into an interactive dashboard.

By combining shot volume, xG, spatial shot locations and finishing efficiency, the project provides a more informative view than goals or shots alone. The final dashboard allows users to explore the data themselves through filters, linked views and hover details.
