import math
import pandas as pd
from statsbombpy import sb

from dash import Dash, dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go



competitions = sb.competitions().copy()


if "competition_gender" not in competitions.columns:
    competitions["competition_gender"] = "unknown"

competitions["label"] = (
    competitions["competition_name"].astype(str)
    + " | "
    + competitions["season_name"].astype(str)
    + " | "
    + competitions["country_name"].astype(str)
)


default_gender = "male"
if "male" not in competitions["competition_gender"].astype(str).str.lower().unique():
    default_gender = competitions["competition_gender"].iloc[0]

filtered_default = competitions[
    competitions["competition_gender"].astype(str).str.lower() == default_gender
].copy()


if filtered_default.empty:
    filtered_default = competitions.copy()

default_competition_id = filtered_default.iloc[0]["competition_id"]
default_season_id = filtered_default.iloc[0]["season_id"]

matches_default = sb.matches(
    competition_id=default_competition_id,
    season_id=default_season_id
).copy()

matches_default["match_label"] = (
    matches_default["home_team"].astype(str)
    + " vs "
    + matches_default["away_team"].astype(str)
    + " | "
    + matches_default["match_date"].astype(str)
)

default_match_id = matches_default.iloc[0]["match_id"]




def load_matches(competition_id, season_id):
    matches = sb.matches(competition_id=competition_id, season_id=season_id).copy()
    matches["match_label"] = (
        matches["home_team"].astype(str)
        + " vs "
        + matches["away_team"].astype(str)
        + " | "
        + matches["match_date"].astype(str)
    )
    return matches


def load_events(match_id):
    events = sb.events(match_id=match_id).copy()

    
    events["x"] = events["location"].apply(
        lambda loc: loc[0] if isinstance(loc, list) and len(loc) >= 2 else None
    )
    events["y"] = events["location"].apply(
        lambda loc: loc[1] if isinstance(loc, list) and len(loc) >= 2 else None
    )

    
    if "team" not in events.columns:
        events["team"] = None
    if "player" not in events.columns:
        events["player"] = None
    if "minute" not in events.columns:
        events["minute"] = 0
    if "type" not in events.columns:
        events["type"] = "Unknown"

    
    def shot_distance(row):
        if pd.notnull(row["x"]) and pd.notnull(row["y"]) and row["type"] == "Shot":
            return round(math.sqrt((120 - row["x"]) ** 2 + (40 - row["y"]) ** 2), 2)
        return None

    events["shot_distance"] = events.apply(shot_distance, axis=1)

    
    if "shot_outcome" not in events.columns:
        events["shot_outcome"] = None
    if "pass_outcome" not in events.columns:
        events["pass_outcome"] = None

    return events


def draw_pitch():
    fig = go.Figure()

    
    fig.add_shape(type="rect", x0=0, y0=0, x1=120, y1=80, line=dict(width=2))
    fig.add_shape(type="line", x0=60, y0=0, x1=60, y1=80, line=dict(width=2))
    fig.add_shape(type="circle", x0=50, y0=30, x1=70, y1=50, line=dict(width=2))
    fig.add_shape(type="circle", x0=59, y0=39, x1=61, y1=41, line=dict(width=2), fillcolor="black")
    fig.add_shape(type="rect", x0=0, y0=18, x1=18, y1=62, line=dict(width=2))
    fig.add_shape(type="rect", x0=102, y0=18, x1=120, y1=62, line=dict(width=2))
    fig.add_shape(type="rect", x0=0, y0=30, x1=6, y1=50, line=dict(width=2))
    
    fig.add_shape(type="rect", x0=114, y0=30, x1=120, y1=50, line=dict(width=2))

    
    fig.add_shape(type="rect", x0=-2, y0=36, x1=0, y1=44, line=dict(width=2))
    
    fig.add_shape(type="rect", x0=120, y0=36, x1=122, y1=44, line=dict(width=2))

    fig.update_xaxes(range=[-5, 125], visible=False)
    fig.update_yaxes(range=[80, 0], visible=False)  # invert y-axis
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        height=450,
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=True,
        title="Match events on pitch"
    )
    return fig


def add_events_to_pitch(fig, df):
    if df.empty:
        return fig

    display_cols = [
        "minute", "team", "player", "type", "shot_outcome", "pass_outcome", "shot_distance"
    ]

    for team_name in df["team"].dropna().unique():
        team_df = df[df["team"] == team_name].copy()

        fig.add_trace(
            go.Scatter(
                x=team_df["x"],
                y=team_df["y"],
                mode="markers",
                name=str(team_name),
                marker=dict(size=10),
                customdata=team_df[display_cols].values,
                hovertemplate=(
                    "<b>Minute:</b> %{customdata[0]}<br>"
                    "<b>Team:</b> %{customdata[1]}<br>"
                    "<b>Player:</b> %{customdata[2]}<br>"
                    "<b>Event:</b> %{customdata[3]}<br>"
                    "<b>Shot outcome:</b> %{customdata[4]}<br>"
                    "<b>Pass outcome:</b> %{customdata[5]}<br>"
                    "<b>Shot distance:</b> %{customdata[6]}<extra></extra>"
                )
            )
        )
    return fig


def build_hover_info(hoverData):
    if hoverData is None or "points" not in hoverData or len(hoverData["points"]) == 0:
        return html.Div([
            html.H4("Event Info"),
            html.P("Hover over an event on the pitch.")
        ])

    point = hoverData["points"][0]
    custom = point.get("customdata", [])

    minute = custom[0] if len(custom) > 0 else None
    team = custom[1] if len(custom) > 1 else None
    player = custom[2] if len(custom) > 2 else None
    event_type = custom[3] if len(custom) > 3 else None
    shot_outcome = custom[4] if len(custom) > 4 else None
    pass_outcome = custom[5] if len(custom) > 5 else None
    shot_distance = custom[6] if len(custom) > 6 else None

    return html.Div([
        html.H4("Event Info"),
        html.P(f"Minute: {minute}"),
        html.P(f"Team: {team}"),
        html.P(f"Player: {player}"),
        html.P(f"Event type: {event_type}"),
        html.P(f"Shot outcome: {shot_outcome}"),
        html.P(f"Pass outcome: {pass_outcome}"),
        html.P(f"Shot distance: {shot_distance}")
    ])




app = Dash(__name__)
app.title = "Football Match Event Dashboard"

app.layout = html.Div([
    html.H1("Football Match Event Dashboard", style={"textAlign": "center"}),

    
    dcc.Store(id="events-store"),
    dcc.Store(id="play-state", data=False),

    
    html.Div([
        html.Div([
            html.Label("Competition"),
            dcc.Dropdown(
                id="competition-dropdown",
                options=[
                    {
                        "label": row["label"],
                        "value": f"{row['competition_id']}|{row['season_id']}"
                    }
                    for _, row in filtered_default.iterrows()
                ],
                value=f"{default_competition_id}|{default_season_id}",
                clearable=False
            )
        ], style={"width": "34%", "display": "inline-block", "padding": "5px"}),

        html.Div([
            html.Label("Men / Women"),
            dcc.Dropdown(
                id="gender-dropdown",
                options=[
                    {"label": g.title(), "value": g}
                    for g in sorted(competitions["competition_gender"].astype(str).str.lower().dropna().unique())
                ],
                value=default_gender,
                clearable=False
            )
        ], style={"width": "15%", "display": "inline-block", "padding": "5px"}),

        html.Div([
            html.Label("Match"),
            dcc.Dropdown(
                id="match-dropdown",
                options=[
                    {"label": row["match_label"], "value": row["match_id"]}
                    for _, row in matches_default.iterrows()
                ],
                value=default_match_id,
                clearable=False
            )
        ], style={"width": "34%", "display": "inline-block", "padding": "5px"}),

        html.Div([
            html.Label("Event type"),
            dcc.Dropdown(
                id="event-type-dropdown",
                options=[],
                value="All",
                clearable=False
            )
        ], style={"width": "15%", "display": "inline-block", "padding": "5px"}),
    ], style={"marginBottom": "10px"}),

    html.Div([
        html.Div([
            html.Button("Play / Pause", id="play-pause-button", n_clicks=0),
            dcc.Interval(id="play-interval", interval=1200, n_intervals=0, disabled=True),
            html.Br(),
            html.Br(),
            html.Label("Minute"),
            dcc.Slider(
                id="minute-slider",
                min=0,
                max=130,
                step=1,
                value=130,
                marks={i: str(i) for i in range(0, 131, 15)}
            )
        ], style={"width": "100%"})
    ], style={"marginBottom": "15px"}),

    
    html.Div([
        html.Div([
            dcc.Graph(id="pitch-graph")
        ], style={"width": "70%", "display": "inline-block", "verticalAlign": "top"}),

        html.Div([
            html.Div(id="hover-info-panel", children=[
                html.H4("Event Info"),
                html.P("Hover over an event on the pitch.")
            ], style={
                "border": "2px solid black",
                "padding": "15px",
                "minHeight": "420px",
                "backgroundColor": "#f9f9f9"
            })
        ], style={"width": "28%", "display": "inline-block", "paddingLeft": "2%"})
    ]),

    
    html.Div([
        html.Div([
            dcc.Graph(id="timeline-plot")
        ], style={"width": "49%", "display": "inline-block"}),

        html.Div([
            dcc.Graph(id="team-count-plot")
        ], style={"width": "49%", "display": "inline-block", "float": "right"})
    ])
])




@app.callback(
    Output("competition-dropdown", "options"),
    Output("competition-dropdown", "value"),
    Input("gender-dropdown", "value")
)
def update_competitions_by_gender(selected_gender):
    comps = competitions[
        competitions["competition_gender"].astype(str).str.lower() == str(selected_gender).lower()
    ].copy()

    if comps.empty:
        comps = competitions.copy()

    options = [
        {
            "label": row["label"],
            "value": f"{row['competition_id']}|{row['season_id']}"
        }
        for _, row in comps.iterrows()
    ]

    value = options[0]["value"]
    return options, value


@app.callback(
    Output("match-dropdown", "options"),
    Output("match-dropdown", "value"),
    Input("competition-dropdown", "value")
)
def update_matches(selected_comp):
    competition_id, season_id = selected_comp.split("|")
    matches = load_matches(int(competition_id), int(season_id))

    options = [
        {"label": row["match_label"], "value": row["match_id"]}
        for _, row in matches.iterrows()
    ]
    value = options[0]["value"]
    return options, value


@app.callback(
    Output("events-store", "data"),
    Output("event-type-dropdown", "options"),
    Output("event-type-dropdown", "value"),
    Input("match-dropdown", "value")
)
def update_events(match_id):
    events = load_events(match_id)

    event_types = sorted(events["type"].dropna().astype(str).unique().tolist())
    options = [{"label": "All", "value": "All"}] + [
        {"label": ev, "value": ev} for ev in event_types
    ]

    return events.to_json(date_format="iso", orient="split"), options, "All"


@app.callback(
    Output("play-state", "data"),
    Output("play-interval", "disabled"),
    Input("play-pause-button", "n_clicks"),
    State("play-state", "data"),
    prevent_initial_call=True
)
def toggle_play(n_clicks, play_state):
    new_state = not play_state
    return new_state, not new_state


@app.callback(
    Output("minute-slider", "value"),
    Input("play-interval", "n_intervals"),
    State("play-state", "data"),
    State("minute-slider", "value"),
    prevent_initial_call=True
)
def advance_minute(n_intervals, play_state, current_minute):
    if not play_state:
        return current_minute
    if current_minute >= 130:
        return 0
    return current_minute + 1


@app.callback(
    Output("pitch-graph", "figure"),
    Output("timeline-plot", "figure"),
    Output("team-count-plot", "figure"),
    Input("events-store", "data"),
    Input("event-type-dropdown", "value"),
    Input("minute-slider", "value")
)
def update_visuals(events_json, selected_event_type, selected_minute):
    events = pd.read_json(events_json, orient="split")

    df = events.copy()
    df = df[df["minute"] <= selected_minute]

    if selected_event_type != "All":
        df = df[df["type"] == selected_event_type]

    
    pitch_df = df[df["x"].notnull() & df["y"].notnull()].copy()

    pitch_fig = draw_pitch()
    pitch_fig = add_events_to_pitch(pitch_fig, pitch_df)

    
    timeline = df.groupby(["minute", "team"]).size().reset_index(name="count")
    if timeline.empty:
        timeline_fig = go.Figure()
        timeline_fig.update_layout(title="Events over time")
    else:
        timeline_fig = px.line(
            timeline,
            x="minute",
            y="count",
            color="team",
            markers=True,
            title="Events over time"
        )
        timeline_fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))

    
    team_counts = df.groupby(["team"]).size().reset_index(name="count")
    if team_counts.empty:
        team_fig = go.Figure()
        team_fig.update_layout(title="Event count by team")
    else:
        team_fig = px.bar(
            team_counts,
            x="team",
            y="count",
            color="team",
            title="Event count by team"
        )
        team_fig.update_layout(margin=dict(l=20, r=20, t=50, b=20), showlegend=False)

    return pitch_fig, timeline_fig, team_fig


@app.callback(
    Output("hover-info-panel", "children"),
    Input("pitch-graph", "hoverData")
)
def update_hover_info(hoverData):
    return build_hover_info(hoverData)


if __name__ == "__main__":
    print("Starting Dash app...")
    app.run(debug=True, host="127.0.0.1", port=8050)