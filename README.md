# FIFA World Cup 2022 Shot Quality Explorer

This project analyses shot quality, shot locations and finishing efficiency in the FIFA World Cup 2022 using StatsBomb Open Data.

It is designed for two visualization modules:

- **GDV – Fundamentals of Data Visualization:** static visual analysis and design reasoning
- **IVI – Interactive Visualization:** an interactive dashboard based on the same prepared dataset

## Research question

**How do shot quality, shot locations and finishing efficiency differ between teams and matches in the FIFA World Cup 2022?**

The project does not only compare goals or shot counts. It separates four analytical dimensions:

1. **Shot volume:** how often teams shoot
2. **Chance quality:** how valuable the shots are, measured with xG
3. **Shot location:** where dangerous chances happen on the pitch
4. **Finishing efficiency:** whether teams score more or fewer goals than expected from xG

## Use case

The dashboard is intended for a football fan, student analyst or assistant coach who wants to quickly understand attacking performance during the World Cup 2022.

A typical user scenario:

> After a match or during a tournament review, the user wants to compare whether a team was actually dangerous or only had many low-quality shots. The user starts with the tournament overview, then filters down to one team, one match or one player.

The dashboard helps answer questions such as:

- Did a team create many shots or actually good chances?
- Which teams had the highest total xG?
- Which teams scored more or fewer goals than expected?
- Where on the pitch did high-quality chances occur?
- Which players contributed most to attacking danger?
- How does a specific match, such as Serbia vs Switzerland, compare to the tournament overview?

## Final repository structure

```text
Football/
├── dashboard/
│   └── app_worldcup.py                # Final IVI dashboard
├── data/
│   ├── raw/                           # Original/raw data files
│   └── processed/                     # Generated processed CSV files
├── evaluation/
│   ├── evaluation_tasks.md            # User test tasks
│   ├── sus_questionnaire.md           # SUS questionnaire
│   ├── evaluation_results_template.csv
│   ├── evaluation_summary.md
│   └── evaluation_analysis.md
├── notebooks/
│   ├── eda2.ipynb                     # Exploratory notebook
│   └── gdv_eda_final.ipynb            # GDV notebook draft
├── reports/
│   ├── figures/                       # Generated GDV figures
│   ├── gdv_insights.md                # Automatically generated insights
│   ├── gdv_report_draft.md            # GDV report draft
│   ├── ivi_report_draft.md            # IVI report draft
│   └── final_report_draft.md          # Combined final report draft
├── src/
│   ├── build_worldcup_shots.py        # Builds processed World Cup shot dataset
│   └── gdv_worldcup_analysis.py       # Final GDV tournament analysis figures
├── SUBMISSION_CHECKLIST.md
├── requirements.txt
└── README.md
```

## Setup

Create and activate a Python environment if needed. Then install the required packages:

```bash
pip install -r requirements.txt
```

## Step 1: Build the processed shot dataset

Run this command from the repository root:

```bash
python src/build_worldcup_shots.py
```

This creates:

```text
data/processed/world_cup_2022_shots.csv
data/processed/world_cup_2022_team_summary.csv
```

The script loads all FIFA World Cup 2022 matches from StatsBomb Open Data, extracts shot events, adds match metadata and calculates derived variables.

Generated variables include:

- `x` and `y`: shot coordinates
- `distance_to_goal`: distance from shot location to goal centre
- `is_goal`: whether the shot resulted in a goal
- `chance_quality`: Low, Medium or High based on xG

## Step 2: Generate GDV figures

Run:

```bash
python src/gdv_worldcup_analysis.py
```

This creates the GDV figures in:

```text
reports/figures/
```

The main GDV figures analyse:

- top teams by shots
- top teams by total xG
- goals compared with xG
- chance quality by team
- shot locations
- distance to goal vs xG
- top players by total xG
- Serbia vs Switzerland as case study

It also creates:

```text
reports/gdv_insights.md
```

## Step 3: Run the IVI dashboard

After the processed dataset exists, start the interactive dashboard with:

```bash
python dashboard/app_worldcup.py
```

Then open the dashboard in your browser:

```text
http://127.0.0.1:8050
```

The dashboard provides:

- KPI cards for shots, goals, total xG, xG per shot and conversion rate
- dependent filters for team, match and player
- filters for shot outcome, chance quality and minute range
- linked visualizations that update together
- hover details for individual shots
- shot map
- timing chart
- finishing efficiency chart
- chance quality mix
- player ranking

## Current GDV results

The processed dataset contains:

- 64 matches
- 32 teams
- 1494 shots
- 195 goals

Important findings:

- Argentina had the highest shot volume with 110 shots.
- Argentina also had the highest total xG with 20.99.
- High-quality chances are usually closer to goal and more central.
- Among teams with at least 10 shots, the Netherlands had the highest conversion rate at 27.10%.
- The Serbia vs Switzerland case study connects the tournament overview to a concrete match.

## GDV part

The GDV part focuses on static visualization and design reasoning.

Relevant files:

```text
src/build_worldcup_shots.py
src/gdv_worldcup_analysis.py
reports/figures/
reports/gdv_insights.md
reports/gdv_report_draft.md
```

## IVI part

The IVI part uses the same processed CSV file:

```text
data/processed/world_cup_2022_shots.csv
```

Relevant files:

```text
dashboard/app_worldcup.py
reports/ivi_report_draft.md
evaluation/evaluation_tasks.md
evaluation/sus_questionnaire.md
evaluation/evaluation_results_template.csv
```

The dashboard follows the interaction principle:

```text
overview first, filter, then details on demand
```

Users start with the tournament overview and then filter down to a team, match or player.

## Evaluation

The evaluation material is stored in:

```text
evaluation/
```

The evaluation uses:

- task-based user testing
- think-aloud observation
- SUS questionnaire
- short qualitative feedback

The planned tasks include finding the highest-xG team, comparing Argentina, analysing Serbia vs Switzerland, filtering high-quality chances and exploring top players.

## Reproducibility

To reproduce the current GDV results and start the IVI dashboard from scratch:

```bash
pip install -r requirements.txt
python src/build_worldcup_shots.py
python src/gdv_worldcup_analysis.py
python dashboard/app_worldcup.py
```

Then check:

```text
data/processed/
reports/figures/
reports/gdv_insights.md
http://127.0.0.1:8050
```

## Data source

The project uses StatsBomb Open Data through the `statsbombpy` Python package.
