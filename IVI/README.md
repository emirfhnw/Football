# Coach Attack Explorer

Interactive dashboard for exploring football goal build ups and tournament style patterns.

## Project idea

The Coach Attack Explorer is an interactive dashboard for inspecting how football teams create goals in tournament data.

The goal is not to predict match results or prove that one attacking style is always better. The dashboard is meant as an exploratory tool. A user can choose a tournament, select a team, replay one goal attack step by step and compare the team's attacking style with other teams in the same tournament.

The project was created for the module Interactive Visualisation.

## Research question

How do teams create goals in major tournaments, and how does their attacking style compare with other teams in the same tournament?

## Dataset

The project uses StatsBomb Open Data.

The dashboard works with prepared local CSV files in the `data/processed/` folder. This makes the app faster during normal use because it does not need to download full event data every time the dashboard is opened.

The processed data contains:

- analysed goal build ups
- events inside each goal build up
- team level comparison values

The raw folder contains the selected tournament list used for preparing the dashboard data.

## Intended users

The dashboard is designed for football interested users such as:

- coaches
- football players
- football fans
- beginner analysts

The dashboard should be understandable without advanced data science knowledge.

## What the dashboard shows

The dashboard focuses on goal attacks. Each selected sequence ends with a goal.

Main features:

- tournament selection
- team selection
- goal example selection
- pitch replay of one selected goal attack
- step by step controls
- full sequence view
- tournament goal pattern charts
- build up type comparison
- passes versus duration scatterplot
- team style map
- directness ranking

## Important note about the replay

The replay is based on event data.

The arrows show completed passes and the final shot. They do not show full player tracking or all off ball movement.

If two arrows do not connect perfectly, this does not mean that the data is wrong. It can happen because the receiver moves with the ball before playing the next pass.

## Build up categories

The dashboard uses three simple build up categories:

- Quick attack: few completed passes before the goal
- Medium build up: medium number of completed passes before the goal
- Long build up: more completed passes before the goal

These categories are simplified. They help users compare attacking styles, but they are not a full tactical model.

## Directness

Directness is used as a style comparison.

A more direct team usually needs fewer completed passes before goals. This does not automatically mean that the team is better. It only describes how direct the team's goal attacks were in the loaded tournament data.

## How to run the dashboard

Open a terminal in the IVI folder:

```bash
cd IVI
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Start the app:

```bash
python app.py
```

Then open the dashboard in the browser:

```text
http://127.0.0.1:8050/
```

If port 8050 is already in use, the app can use:

```text
http://127.0.0.1:8051/
```

## Project structure

```text
IVI/
│   app.py
│   build_static_tournament_data.py
│   create_selected_tournaments.py
│   README.md
│   requirements.txt
│
├── assets/
│   └── style.css
│
├── data/
│   ├── processed/
│   │   ├── build_up_events_df.csv
│   │   ├── goals_df.csv
│   │   └── team_efficiency_df.csv
│   │
│   └── raw/
│       └── selected_tournaments.csv
│
├── evaluation/
│   ├── Aufgaben_Yannick_Geiger.docx
│   ├── Aufgabe_Ivan_batista.docx
│   ├── Aufgabe_Kenan_Trainer.docx
│   ├── Evaluation.pdf
│   └── IVI_Evaluation.docx
│
├── report/
│   ├── IVI.pptx
│   ├── Rport_ivi.docx
│   └── Rport_ivi.pdf
│
└── src/
    ├── data_loader.py
    ├── figures.py
    ├── layout.py
    ├── metrics.py
    ├── pitch_plots.py
    ├── preprocessing.py
    ├── static_tournament_store.py
    ├── statsbomb_explorer.py
    └── utils.py
```

## Main files

`app.py` starts the Dash application.

`assets/style.css` contains the dashboard styling.

`src/layout.py` defines the dashboard layout.

`src/figures.py` creates the Plotly figures.

`src/pitch_plots.py` creates the pitch replay view.

`src/data_loader.py` loads the processed dashboard data.

`src/preprocessing.py` contains preprocessing logic.

`data/processed/` contains the prepared CSV files used by the dashboard.

## Evaluation

The evaluation material is stored in the `evaluation/` folder.

The final evaluation summary is:

```text
evaluation/IVI_Evaluation.docx
```

The individual task sheets are:

```text
evaluation/Aufgaben_Yannick_Geiger.docx
evaluation/Aufgabe_Ivan_batista.docx
evaluation/Aufgabe_Kenan_Trainer.docx
```

The evaluation was done with three football interested participants. The main result was that the goal replay was the easiest and most useful part. The comparison views were useful, but terms such as Directness Rank and the team style map needed clearer explanation.

Based on the final pitch and evaluation feedback, I made the dashboard clearer by using more consistent colours, improving plot explanations and adding a more detailed header explanation.

## Report and presentation

The final report is stored in:

```text
report/Rport_ivi.pdf
report/Rport_ivi.docx
```

The final presentation is stored in:

```text
report/IVI.pptx
```

## Limitations

The dashboard only analyses goal build ups. It does not show every attack in a match.

The data is event data. It does not include full tracking data, off ball runs, defensive positioning or coaching instructions.

The build up categories are simplified. They are useful for comparison, but they do not explain every tactical detail.

The evaluation was small and formative. It helped improve the prototype, but it does not make general claims about all possible users.

## Final note

The Coach Attack Explorer should be read as an interactive exploratory prototype. It helps users inspect selected goal attacks and compare attacking styles inside a tournament. It is not a prediction system and not a complete tactical model.
