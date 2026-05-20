# FIFA World Cup 2022 Shot Quality Explorer

This project analyses shot quality, shot locations and finishing efficiency in the FIFA World Cup 2022 using StatsBomb Open Data.

The project is used for two visualization modules:

- **GDV – Fundamentals of Data Visualization**: static visual analysis and design reasoning
- **IVI – Interactive Visualization**: interactive dashboard based on the same prepared dataset

## Research question

**How do shot quality, shot locations and finishing efficiency differ between teams and matches in the FIFA World Cup 2022?**

The goal is not only to count shots or goals. The analysis also uses expected goals (xG), pitch location and conversion rate to compare attacking quality between teams, matches and players.

## Use case

The target user is a football fan, student analyst or coach who wants to explore which teams and players created dangerous chances during the tournament.

The user should be able to answer questions such as:

- Which teams produced the most shots?
- Which teams produced the highest total xG?
- Which teams were most efficient in converting shots into goals?
- Where on the pitch did high-quality chances occur?
- Which players contributed most to attacking danger?
- How does a specific match, such as Serbia vs Switzerland, compare to the tournament overview?

## Repository structure

```text
Football/
├── dashboard/
│   └── app.py                         # Current IVI dashboard prototype
├── data/
│   ├── raw/                           # Original/raw data files
│   └── processed/                     # Generated processed CSV files
├── notebooks/
│   ├── eda2.ipynb                     # Early exploratory notebook
│   └── gdv_eda_final.ipynb            # First GDV notebook draft
├── reports/
│   ├── figures/                       # Generated GDV figures
│   ├── gdv_insights.md                # Automatically generated insights
│   └── gdv_report_draft.md            # Current GDV report draft
├── src/
│   ├── build_worldcup_shots.py        # Builds processed World Cup shot dataset
│   ├── gdv_analysis.py                # Earlier single-match GDV analysis
│   └── gdv_worldcup_analysis.py       # Final GDV tournament analysis figures
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

The main figures are:

- Top 10 teams by shots
- Top 10 teams by total xG
- Goals compared with xG
- Chance quality by team
- Shot map of all World Cup 2022 shots
- Distance to goal vs xG
- Top players by total xG
- Serbia vs Switzerland case study

It also creates:

```text
reports/gdv_insights.md
```

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

The report draft explains:

- the research question
- dataset description
- preprocessing
- design rationale
- interpretation of the figures
- main findings
- connection to IVI
- limitations

## IVI part

The IVI part will use the same processed CSV file:

```text
data/processed/world_cup_2022_shots.csv
```

Planned dashboard features:

- KPI cards for shots, goals, total xG, xG per shot and conversion rate
- filters for team, match, player, shot outcome and chance quality
- interactive shot map
- shot timeline
- team and player comparison charts
- hover details for individual shots
- linked views where all charts react to the same filters

## Reproducibility

To reproduce the current GDV results from scratch:

```bash
pip install -r requirements.txt
python src/build_worldcup_shots.py
python src/gdv_worldcup_analysis.py
```

Then check:

```text
data/processed/
reports/figures/
reports/gdv_insights.md
```

## Data source

The project uses StatsBomb Open Data through the `statsbombpy` Python package.
