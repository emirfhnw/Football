# GDV Report Draft – FIFA World Cup 2022 Shot Quality Explorer

## Title page information

**Project title:** FIFA World Cup 2022 Shot Quality Explorer  
**Module:** Fundamentals of Data Visualization (GDV)  
**Student:** Emir Can  
**Dataset:** StatsBomb Open Data, FIFA World Cup 2022  
**Research question:** How do shot quality, shot locations and finishing efficiency differ between teams and matches in the FIFA World Cup 2022?

---

## 1. Introduction and research question

This project analyses shot data from the FIFA World Cup 2022. The main goal is not only to count goals or shots, but to understand how dangerous the created chances were. For this reason, the analysis focuses on three central aspects: shot quality, shot location and finishing efficiency.

The main research question is:

**How do shot quality, shot locations and finishing efficiency differ between teams and matches in the FIFA World Cup 2022?**

This question is useful because football results alone can be misleading. A team can win a match with only a few shots, while another team can create many chances but fail to score. By visualizing shot data, expected goals and spatial shot locations, we can better understand attacking performance across teams and matches.

The project also prepares the basis for the later IVI part. The static GDV analysis identifies the most important variables and patterns. These same variables can then be used in an interactive dashboard where users can filter by team, match, player, shot outcome and chance quality.

---

## 2. Dataset description

The dataset is based on StatsBomb Open Data for the FIFA World Cup 2022. The analysis uses all available matches from the tournament. The processed dataset contains:

- 64 matches
- 32 teams
- 1494 shots
- 195 goals

Each shot includes information such as the team, player, match, minute, pitch location, shot outcome and expected goals value. Expected goals, usually abbreviated as xG, estimates the probability that a shot becomes a goal based on its characteristics. In this project, xG is used as the main indicator for shot quality.

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

These variables are suitable for the project because they allow comparisons between teams, players, matches and shot locations.

---

## 3. Data preprocessing

The data preparation was done in `src/build_worldcup_shots.py`. The script loads all FIFA World Cup 2022 matches from StatsBomb Open Data and then extracts only shot events. This keeps the project focused and avoids unnecessary complexity.

The preprocessing steps were:

1. Load all FIFA World Cup 2022 matches.
2. Load event data for every match.
3. Filter the event data to keep only shots.
4. Add match information such as home team, away team, score and match label.
5. Extract shot coordinates from the `location` field.
6. Convert xG and minute values to numeric data types.
7. Calculate the distance from the shot position to the goal centre.
8. Create a boolean variable `is_goal` from the shot outcome.
9. Create a categorical variable `chance_quality` based on xG.

The created `chance_quality` categories are:

- **Low:** xG below 0.05
- **Medium:** xG from 0.05 to below 0.20
- **High:** xG of 0.20 or higher

This transformation makes xG easier to interpret. Instead of showing only numeric probabilities, users can quickly see whether a shot was a low, medium or high-quality chance.

The final processed files are:

- `data/processed/world_cup_2022_shots.csv`
- `data/processed/world_cup_2022_team_summary.csv`
- `data/processed/world_cup_2022_player_summary.csv`

---

## 4. Design rationale

The visualizations were designed to answer the research question step by step. The analysis starts with simple team comparisons and then moves toward more detailed spatial and temporal patterns.

Bar charts are used for comparing teams and players because they encode values through length. Length is easy to compare and works well for rankings such as number of shots, total xG or player xG.

Scatterplots are used where the relationship between two quantitative variables matters. For example, the distance vs xG plot shows how shot distance relates to chance quality.

The shot map uses pitch coordinates because football shots are spatial events. Position on the pitch is meaningful by itself, so a pitch map is more natural than a normal scatterplot. Larger or highlighted markers are used for more important events such as high-quality chances and goals.

The design follows these principles:

- Use simple chart types for clear comparisons.
- Use position and length for accurate quantitative reading.
- Use color mainly for categorical separation.
- Avoid unnecessary decoration.
- Keep titles, axis labels and legends explicit.
- Move from overview to detail.

This supports the GDV goal of connecting data, design decisions and interpretation.

---

## 5. Visual analysis and interpretation

### Figure 1: Top 10 teams by number of shots

This figure shows which teams produced the highest shot volume during the tournament. Shot volume is a useful first overview because it shows how often a team reached a shooting situation. However, this figure alone does not tell us whether the shots were dangerous.

Argentina had the highest shot volume with 110 shots. This means Argentina frequently reached shooting positions, but shot volume still needs to be combined with xG and location to understand quality.

### Figure 2: Top 10 teams by total xG

This figure compares teams by total expected goals. Total xG is more informative than only counting shots because it includes the estimated quality of each attempt.

Argentina also had the highest total xG with 20.99. This suggests that Argentina did not only shoot often, but also created many valuable chances.

### Figure 3: Goals compared with xG

This figure compares actual goals with expected goals for the highest xG teams. It helps identify whether teams scored more or fewer goals than expected based on chance quality.

A team that scores more goals than its xG can be interpreted as efficient or overperforming in finishing. A team that scores fewer goals than its xG may have created good chances but did not convert them as effectively.

### Figure 4: Chance quality categories by team

This figure shows low, medium and high-quality chances for the top xG teams. It makes the xG information easier to understand because probabilities are grouped into interpretable categories.

This view helps distinguish teams that mainly produced many low-quality shots from teams that created fewer but more dangerous chances.

### Figure 5: Shot map of all World Cup 2022 shots

The shot map shows the spatial distribution of all shots in the tournament. It highlights that high-quality chances are usually closer to goal and more central. This makes intuitive football sense and supports the interpretation of xG.

The map is important because it connects numerical values with the real pitch layout. Users can directly see where shots were taken and where goals or high-quality chances occurred.

### Figure 6: Distance to goal vs xG

This figure shows the relationship between shot distance and xG. In general, shots closer to goal tend to have higher xG values. This is expected because closer shots are usually easier to score.

The plot also shows that distance is not the only factor. Some close shots can still have low xG, and some shots from moderate distance can be dangerous depending on angle, pressure or situation.

### Figure 7: Top players by total xG

This figure ranks players by their total xG. It connects team-level attacking performance to individual players. This is useful because teams create chances collectively, but shots are taken by individual players.

The figure helps identify which players were most involved in dangerous finishing situations during the tournament.

### Figure 8: Case study Serbia vs Switzerland

The case study connects the tournament-wide overview to one concrete match. Serbia vs Switzerland is useful because it is easy to explain and directly relevant to a Swiss context.

The figure combines a shot map and a timeline. The shot map shows where the chances were created. The timeline shows when the shots happened during the match. This creates a bridge toward the later interactive dashboard, where users will be able to select a match and explore it in detail.

---

## 6. Main findings

The analysis shows that shot volume and chance quality are related, but they are not the same. Argentina had both the highest shot volume and the highest total xG, but this will not always be the case for every team or match.

The spatial visualizations show that shot location is very important. High-quality chances tend to come from central and close positions. This supports the use of pitch maps in football visualization.

Finishing efficiency differs between teams. Among teams with at least 10 shots, the Netherlands had the highest conversion rate at 27.10%. This indicates that some teams were more efficient in converting their chances into goals.

The player analysis adds another layer. It shows which players contributed most to attacking danger. This is useful for storytelling and for later interactive filtering.

Overall, the static analysis provides a clear foundation for the IVI dashboard. The most relevant dimensions for interactivity are team, match, player, shot outcome, chance quality, time and pitch location.

---

## 7. Connection to IVI

The GDV analysis directly informs the planned IVI dashboard. The static figures reveal which variables and comparisons are meaningful. The IVI dashboard will then allow users to explore the same data interactively.

The planned dashboard will include:

- filters for team, match, player, shot outcome and chance quality
- KPI cards for shots, goals, total xG, xG per shot and conversion rate
- an interactive shot map
- a timeline of shots
- team and player comparison charts
- hover details for individual shots

This means the user can move from a tournament overview to a specific team, match or player. This follows the idea of overview first, then filtering and details on demand.

---

## 8. Limitations

The analysis focuses only on shots. This keeps the project understandable and reproducible, but it also means that other important parts of football performance are not included. For example, passes, defensive actions, pressing and possession sequences are not analysed.

The xG values are used as provided by StatsBomb. The project does not build its own xG model. This is appropriate for the scope of the module, but it means that the analysis depends on the existing StatsBomb model.

Finally, the visualizations show patterns and support interpretation, but they do not prove causal relationships. For example, a team with a high conversion rate was efficient in the dataset, but the visualization alone does not explain all tactical or contextual reasons behind this efficiency.

---

## 9. Short conclusion

This GDV analysis shows how shot data from the FIFA World Cup 2022 can be visualized to compare attacking quality between teams, players and matches. By combining shot volume, xG, shot locations and finishing efficiency, the project provides a more complete view than goals or shots alone.

The static visualizations also create a strong basis for the IVI part of the project. The next step is to turn the same analysis into an interactive dashboard where users can filter and explore the data themselves.
