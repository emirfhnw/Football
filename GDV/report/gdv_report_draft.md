# Goal Build-up Analysis at the FIFA World Cup 2022

## Title page

**Module:** Fundamentals of Data Visualization (GDV)  
**Project:** Goal Build-up Analysis  
**Dataset:** StatsBomb Open Data, FIFA World Cup 2022  
**Student:** Emir Can  
**Semester of first enrollment:** FS26

---

## 1. Introduction and research question

This project analyses how goals were created at the FIFA World Cup 2022. The main question is whether goals were created more often through quick attacks with only a few completed passes or through longer passing sequences.

The research question is:

**How were goals created at the FIFA World Cup 2022: through quick attacks with few passes or through longer passing sequences?**

The project is relevant because goal build-ups are an important part of football analysis. A simple goal count only shows the final result, but not how the chance was created. By looking at completed passes before the goal, attack duration and team differences, the visualizations show different attacking styles more clearly.

The intended audience is football-interested viewers, students and beginner analysts. The visualizations are designed to be understandable without expert knowledge in football analytics.

---

## 2. Dataset description

The project uses StatsBomb Open Data from the FIFA World Cup 2022. The data contains event-level football data such as passes, shots, goals, teams, players, timestamps, match information and pitch coordinates.

For this GDV analysis, the relevant unit of analysis is a goal build-up. For every goal, the preprocessing identifies the goal shot, the possession before the goal, the completed passes before the shot and the duration of the attack.

The most relevant variables are:

| Variable | Meaning |
|---|---|
| `team` | Team that scored the goal |
| `scorer` | Player who scored |
| `match_name` | Match in which the goal happened |
| `passes_before_goal` | Number of completed passes before the goal within the possession |
| `attack_duration_seconds` | Duration of the attack before the goal |
| `build_up_type` | Quick, Medium or Long build-up |
| `minute` | Minute of the goal |
| `x`, `y`, `end_x`, `end_y` | Event coordinates used for sequence plots |

The build-up categories are defined as:

| Category | Definition |
|---|---|
| Quick | 0 to 2 completed passes before the goal |
| Medium | 3 to 6 completed passes before the goal |
| Long | 7 or more completed passes before the goal |

A limitation is that the data is event data only. It does not contain player tracking data. Therefore, the analysis cannot show off-ball movement, pressing behaviour or exact player runs.

---

## 3. Data preprocessing summary

The raw event data was transformed into goal-level and event-sequence tables. First, goal shots were identified. Then the corresponding possession was used to collect completed passes before the goal. For every goal, the number of completed passes and attack duration were calculated.

The processed data was saved as CSV files so that the visualizations can be reproduced without reloading the full raw data every time.

The preprocessing also created the build-up type variable. This variable makes the visual analysis easier because the viewer can compare simple categories instead of interpreting only raw pass counts.

---

## 4. Design rationale

The visualizations follow basic principles from data visualization and perception research. The goal was to keep the figures clear, avoid unnecessary decoration and use chart types that match the analytical questions.

### 4.1 Build-up type distribution

A bar chart is used to show the number of goals by build-up type. This is appropriate because the data is categorical and the main task is comparing quantities. Bar length supports accurate comparison better than angles or areas.

The chart answers the first part of the research question directly: whether quick, medium or long build-ups were most common.

**Figure 1:** Build-up type distribution.

### 4.2 Passes before goal vs attack duration

A scatterplot is used to compare the number of completed passes before a goal with the attack duration. This is suitable because both variables are quantitative. The scatterplot shows whether longer passing sequences also tend to take more time, while still allowing exceptions and spread to be visible.

This figure avoids reducing the relationship to only one average value. The spread of the points is important because football attacks can differ even when the number of passes is similar.

**Figure 2:** Completed passes before goal vs attack duration.

### 4.3 Team comparison

A horizontal bar chart is used to compare teams by average completed passes before goal. The horizontal layout makes team names easier to read. Sorting the bars helps the viewer quickly identify more direct and more patient teams.

This figure supports comparison between teams and connects the general tournament pattern to concrete team styles.

**Figure 3:** Direct vs patient teams.

### 4.4 Finishing efficiency and tournament progress

A scatterplot is used to compare finishing efficiency and tournament progress. The purpose of this figure is exploratory, not causal. It can show whether there is a visible association, but it does not prove that finishing efficiency caused tournament success.

This limitation is important because visualizations can easily create a false impression of causality. The report therefore states clearly that the chart should be interpreted as descriptive.

**Figure 4:** Finishing efficiency vs tournament progress.

### 4.5 Case study sequence

A selected goal sequence is visualized on a football pitch. The numbered events show the order of successful passes before the goal. This figure helps connect the aggregate analysis with one concrete example.

The case study is useful because it shows what a build-up category means in football terms. Instead of only seeing that a build-up was long or quick, the viewer can inspect the actual sequence.

**Figure 5:** Spain case study goal build-up.

---

## 5. Main findings

The first main finding is that quick attacks were the most common build-up type in the analysed goals. This suggests that many goals at the FIFA World Cup 2022 were created after relatively few completed passes.

The second finding is that longer passing sequences usually also took more time, but not perfectly. The scatterplot shows variation, which means that pass count and duration are related but not identical measures.

The third finding is that teams differed in their goal build-up style. Some teams appeared more direct, while others scored after longer passing sequences. This supports the idea that team-level comparison adds value beyond the overall tournament distribution.

The fourth finding is that efficiency and tournament progress should be interpreted carefully. The visualization can show patterns, but it cannot prove that one variable caused the other.

---

## 6. Evaluation methodology

A small formative evaluation was conducted with three football-interested participants. The goal was to check whether the static GDV visualizations communicate the intended insights clearly.

The participants inspected the final figures and answered five interpretation tasks. They were also asked which figure was easiest to understand, which figure was most confusing and what they would improve.

The evaluation tasks were:

1. Identify the most common goal build-up type.
2. Interpret the relationship between passes before goal and attack duration.
3. Name one direct and one patient team.
4. Interpret the finishing efficiency vs tournament progress chart without making a causal claim.
5. Explain the Spain case study sequence.

This method was chosen because the project focuses on interpretability. A small think-aloud evaluation is useful for finding unclear labels, confusing legends and possible misinterpretations.

---

## 7. Evaluation results and improvements

All three participants answered all five tasks correctly. This indicates that the main static figures were understandable.

However, the evaluation also showed three improvement points.

First, the finishing efficiency vs tournament progress chart needed a clearer explanation. Participants understood the chart, but the figure could be misread as causal. Therefore, the report text was revised to explain that the figure shows an association, not causation.

Second, the Spain case study needed a short explanation. The numbered sequence was understandable after participants knew that the numbers represent the order of completed passes before the goal. Therefore, the final explanation was made more explicit.

Third, the build-up type categories needed to be defined before interpreting the charts. Therefore, the report now explains Quick, Medium and Long before discussing the figures.

The evaluation led mainly to textual and explanatory improvements. The chart types themselves were kept because participants could answer the interpretation tasks correctly.

---

## 8. Limitations

The project has several limitations.

First, only event data is used. This means the analysis cannot include off-ball movement, pressing shape or player runs.

Second, the build-up categories are simplified. A quick attack is defined only by completed passes before the goal. This does not capture every tactical detail.

Third, the evaluation used only three participants. This is acceptable for a small formative course evaluation, but it is not enough for strong general conclusions.

Fourth, the figures are descriptive. They show patterns in the data, but they do not prove causal relationships.

---

## 9. Conclusion

The GDV analysis shows that goal build-ups at the FIFA World Cup 2022 can be communicated clearly through a small set of static visualizations. Bar charts and scatterplots were suitable because they matched the main analytical tasks: comparing categories, comparing teams and exploring relationships between quantitative variables.

The main insight is that quick attacks were the most common build-up type in the analysed goals. At the same time, team comparison and case study visualizations show that goal creation is not uniform across all teams.

The evaluation confirmed that the figures were generally understandable. The most important improvements were clearer explanations of category definitions, sequence numbering and the non-causal interpretation of efficiency.

---

## References

Cleveland, W. S., & McGill, R. (1984). Graphical perception: Theory, experimentation, and application to the development of graphical methods. *Journal of the American Statistical Association, 79*(387), 531–554.

Munzner, T. (2014). *Visualization Analysis and Design*. CRC Press.

StatsBomb. (n.d.). *StatsBomb Open Data*. GitHub. https://github.com/statsbomb/open-data

Tufte, E. R. (1983). *The Visual Display of Quantitative Information*. Graphics Press.

Wilke, C. O. (2019). *Fundamentals of Data Visualization*. O’Reilly Media.

---

## Figures

The final PDF should include the exported static figures after the main text. Each figure should be labelled and referenced in the text.

Required figures:

1. Build-up type distribution
2. Passes before goal vs attack duration
3. Direct vs patient teams
4. Finishing efficiency vs tournament progress
5. Build-up type share by team
6. Spain case study goal build-up
