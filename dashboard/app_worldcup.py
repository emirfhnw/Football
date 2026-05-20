"""
Interactive Visualization (IVI) dashboard for the FIFA World Cup 2022 Shot Quality Explorer.

Run from repository root:
    python dashboard/app_worldcup.py

Required input:
    data/processed/world_cup_2022_shots.csv

If the file is missing, run first:
    python src/build_worldcup_shots.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "processed" / "world_cup_2022_shots.csv"

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Missing file: {DATA_FILE}\n"
        "Run first: python src/build_worldcup_shots.py"
    )

shots = pd.read_csv(DATA_FILE)

# Basic cleanup after CSV loading
shots["is_goal"] = shots["is_goal"].astype(str).str.lower().eq("true")
shots["shot_statsbomb_xg"] = pd.to_numeric(shots["shot_statsbomb_xg"], errors="coerce").fillna(0)
shots["minute"] = pd.to_numeric(shots["minute"], errors="coerce").fillna(0)
shots["x"] = pd.to_numeric(shots["x"], errors="coerce")
shots["y"] = pd.to_numeric(shots["y"], errors="coerce")
shots["distance_to_goal"] = pd.to_numeric(shots["distance_to_goal"], errors="coerce")

for col in ["team", "player", "match_label", "shot_outcome", "chance_quality", "competition_stage"]:
    shots[col] = shots[col].fillna("Unknown").astype(str)

# Dropdown options
team_options = [{"label": "All teams", "value": "All"}] + [
    {"label": team, "value": team} for team in sorted(shots["team"].unique())
]
match_options = [{"label": "All matches", "value": "All"}] + [
    {"label": match, "value": match} for match in sorted(shots["match_label"].unique())
]
player_options = [{"label": "All players", "value": "All"}] + [
    {"label": player, "value": player} for player in sorted(shots["player"].unique())
]
outcome_options = [{"label": "All outcomes", "value": "All"}] + [
    {"label": outcome, "value": outcome} for outcome in sorted(shots["shot_outcome"].unique())
]
quality_options = [{"label": "All qualities", "value": "All"}] + [
    {"label": q, "value": q} for q in ["Low", "Medium", "High"] if q in shots["chance_quality"].unique()
]


def filter_data(team, match, player, outcome, quality, minute_range):
    """Apply dashboard filters."""
    df = shots.copy()

    if team != "All":
        df = df[df["team"] == team]
    if match != "All":
        df = df[df["match_label"] == match]
    if player != "All":
        df = df[df["player"] == player]
    if outcome != "All":
        df = df[df["shot_outcome"] == outcome]
    if quality != "All":
        df = df[df["chance_quality"] == quality]

    df = df[(df["minute"] >= minute_range[0]) & (df["minute"] <= minute_range[1])]
    return df


def metric_card(title, value, subtitle=""):
    return html.Div(
        [
            html.Div(title, style={"fontSize": "13px", "color": "#64748b"}),
            html.Div(value, style={"fontSize": "26px", "fontWeight": "700", "color": "#0f172a"}),
            html.Div(subtitle, style={"fontSize": "11px", "color": "#94a3b8"}),
        ],
        style={
            "backgroundColor": "white",
            "border": "1px solid #e2e8f0",
            "borderRadius": "14px",
            "padding": "14px",
            "boxShadow": "0 1px 4px rgba(15, 23, 42, 0.08)",
            "width": "19%",
            "display": "inline-block",
            "marginRight": "1%",
            "verticalAlign": "top",
        },
    )


def info_box(title, text):
    return html.Div(
        [
            html.Div(title, style={"fontWeight": "700", "fontSize": "13px", "color": "#0f172a", "marginBottom": "4px"}),
            html.Div(text, style={"fontSize": "12px", "lineHeight": "1.45", "color": "#475569"}),
        ],
        style={
            "backgroundColor": "#f8fafc",
            "border": "1px solid #e2e8f0",
            "borderRadius": "12px",
            "padding": "10px 12px",
            "marginTop": "10px",
        },
    )


def empty_figure(title):
    fig = go.Figure()
    fig.update_layout(
        title=title,
        annotations=[
            dict(
                text="No data for the current filters",
                x=0.5,
                y=0.5,
                showarrow=False,
                xref="paper",
                yref="paper",
                font=dict(size=16),
            )
        ],
        height=420,
    )
    return fig


def create_pitch_figure(df):
    """Create interactive shot map."""
    if df.empty:
        return empty_figure("Interactive shot map")

    fig = go.Figure()

    # Pitch lines
    line = dict(color="#334155", width=2)
    fig.add_shape(type="rect", x0=0, y0=0, x1=120, y1=80, line=line)
    fig.add_shape(type="line", x0=60, y0=0, x1=60, y1=80, line=line)
    fig.add_shape(type="circle", x0=50, y0=30, x1=70, y1=50, line=line)
    fig.add_shape(type="rect", x0=0, y0=18, x1=18, y1=62, line=line)
    fig.add_shape(type="rect", x0=102, y0=18, x1=120, y1=62, line=line)
    fig.add_shape(type="rect", x0=0, y0=30, x1=6, y1=50, line=line)
    fig.add_shape(type="rect", x0=114, y0=30, x1=120, y1=50, line=line)

    plot_df = df.dropna(subset=["x", "y"]).copy()
    plot_df["goal_label"] = plot_df["is_goal"].map({True: "Goal", False: "No goal"})

    fig_px = px.scatter(
        plot_df,
        x="x",
        y="y",
        color="team",
        symbol="goal_label",
        size="shot_statsbomb_xg",
        size_max=24,
        hover_data={
            "player": True,
            "team": True,
            "match_label": True,
            "minute": True,
            "shot_statsbomb_xg": ":.3f",
            "shot_outcome": True,
            "chance_quality": True,
            "distance_to_goal": ":.1f",
            "x": False,
            "y": False,
        },
    )

    for trace in fig_px.data:
        fig.add_trace(trace)

    fig.update_xaxes(range=[0, 120], visible=False)
    fig.update_yaxes(range=[80, 0], visible=False)
    fig.update_layout(
        title="Interactive shot map – marker size represents xG, star/cross symbols indicate goals",
        height=520,
        margin=dict(l=10, r=10, t=60, b=10),
        plot_bgcolor="#ecfdf5",
        paper_bgcolor="white",
        legend_title_text="Team / Goal",
    )
    return fig


app = Dash(__name__)
app.title = "World Cup 2022 Shot Quality Explorer"

app.layout = html.Div(
    [
        html.Div(
            [
                html.H1("FIFA World Cup 2022 Shot Quality Explorer", style={"marginBottom": "4px"}),
                html.P(
                    "Explore shot quality, shot locations and finishing efficiency across teams, matches and players.",
                    style={"color": "#64748b", "fontSize": "16px", "marginTop": "0"},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Strong("How to use this dashboard: "),
                                "Start with the tournament overview, then filter by team, match, player, outcome, chance quality or minute range. All charts update together.",
                            ],
                            style={"fontSize": "13px", "color": "#334155", "marginBottom": "6px"},
                        ),
                        html.Div(
                            [
                                html.Strong("xG explanation: "),
                                "Expected goals (xG) estimates how likely a shot is to become a goal. Higher xG means a better chance. Chance quality is grouped as Low (<0.05), Medium (0.05–0.20) and High (>=0.20).",
                            ],
                            style={"fontSize": "13px", "color": "#334155"},
                        ),
                    ],
                    style={
                        "backgroundColor": "#e0f2fe",
                        "border": "1px solid #7dd3fc",
                        "borderRadius": "14px",
                        "padding": "12px 14px",
                        "marginTop": "12px",
                    },
                ),
            ],
            style={"padding": "20px 24px 8px 24px"},
        ),

        html.Div(id="kpi-container", style={"padding": "0 24px 16px 24px"}),

        html.Div(
            [
                html.Div(
                    [
                        html.H3("Filters", style={"marginTop": "0"}),
                        html.Label("Team"),
                        dcc.Dropdown(id="team-filter", options=team_options, value="All", clearable=False),
                        html.Br(),
                        html.Label("Match"),
                        dcc.Dropdown(id="match-filter", options=match_options, value="All", clearable=False),
                        html.Br(),
                        html.Label("Player"),
                        dcc.Dropdown(id="player-filter", options=player_options, value="All", clearable=False),
                        html.Br(),
                        html.Label("Shot outcome"),
                        dcc.Dropdown(id="outcome-filter", options=outcome_options, value="All", clearable=False),
                        html.Br(),
                        html.Label("Chance quality"),
                        dcc.Dropdown(id="quality-filter", options=quality_options, value="All", clearable=False),
                        html.Br(),
                        html.Label("Minute range"),
                        dcc.RangeSlider(
                            id="minute-filter",
                            min=0,
                            max=int(max(120, shots["minute"].max())),
                            step=1,
                            value=[0, int(max(120, shots["minute"].max()))],
                            marks={i: str(i) for i in range(0, int(max(120, shots["minute"].max())) + 1, 15)},
                            tooltip={"placement": "bottom", "always_visible": False},
                        ),
                        html.Hr(),
                        info_box(
                            "User task",
                            "Select a team, match or player and compare shot volume, xG, chance quality and spatial patterns.",
                        ),
                        info_box(
                            "Linked views",
                            "The KPI cards, pitch map, timeline and bar charts always represent the same filtered data.",
                        ),
                    ],
                    style={
                        "width": "24%",
                        "display": "inline-block",
                        "verticalAlign": "top",
                        "backgroundColor": "white",
                        "padding": "18px",
                        "borderRadius": "14px",
                        "boxShadow": "0 1px 4px rgba(15, 23, 42, 0.08)",
                    },
                ),
                html.Div(
                    [dcc.Graph(id="shot-map")],
                    style={"width": "74%", "display": "inline-block", "verticalAlign": "top", "marginLeft": "2%"},
                ),
            ],
            style={"padding": "0 24px 16px 24px"},
        ),

        html.Div(
            [
                html.Div([dcc.Graph(id="xg-by-team")], style={"width": "49%", "display": "inline-block"}),
                html.Div([dcc.Graph(id="shot-timeline")], style={"width": "49%", "display": "inline-block", "marginLeft": "2%"}),
            ],
            style={"padding": "0 24px 16px 24px"},
        ),

        html.Div(
            [
                html.Div([dcc.Graph(id="top-players")], style={"width": "49%", "display": "inline-block"}),
                html.Div([dcc.Graph(id="outcome-chart")], style={"width": "49%", "display": "inline-block", "marginLeft": "2%"}),
            ],
            style={"padding": "0 24px 24px 24px"},
        ),
    ],
    style={"backgroundColor": "#f8fafc", "fontFamily": "Arial, sans-serif", "minHeight": "100vh"},
)


@app.callback(
    Output("kpi-container", "children"),
    Output("shot-map", "figure"),
    Output("xg-by-team", "figure"),
    Output("shot-timeline", "figure"),
    Output("top-players", "figure"),
    Output("outcome-chart", "figure"),
    Input("team-filter", "value"),
    Input("match-filter", "value"),
    Input("player-filter", "value"),
    Input("outcome-filter", "value"),
    Input("quality-filter", "value"),
    Input("minute-filter", "value"),
)
def update_dashboard(team, match, player, outcome, quality, minute_range):
    df = filter_data(team, match, player, outcome, quality, minute_range)

    total_shots = len(df)
    total_goals = int(df["is_goal"].sum()) if not df.empty else 0
    total_xg = df["shot_statsbomb_xg"].sum() if not df.empty else 0
    xg_per_shot = total_xg / total_shots if total_shots else 0
    conversion_rate = total_goals / total_shots if total_shots else 0

    kpis = [
        metric_card("Shots", f"{total_shots:,}", "Filtered attempts"),
        metric_card("Goals", f"{total_goals:,}", "Successful shots"),
        metric_card("Total xG", f"{total_xg:.2f}", "Chance quality sum"),
        metric_card("xG / Shot", f"{xg_per_shot:.3f}", "Average shot quality"),
        metric_card("Conversion", f"{conversion_rate:.1%}", "Goals divided by shots"),
    ]

    shot_map = create_pitch_figure(df)

    if df.empty:
        return (
            kpis,
            shot_map,
            empty_figure("xG by team"),
            empty_figure("Shot timeline"),
            empty_figure("Top players by xG"),
            empty_figure("Shot outcomes"),
        )

    # xG by team
    team_df = (
        df.groupby("team")
        .agg(shots=("team", "size"), goals=("is_goal", "sum"), total_xg=("shot_statsbomb_xg", "sum"))
        .reset_index()
        .sort_values("total_xg", ascending=False)
        .head(12)
    )
    xg_fig = px.bar(team_df, x="total_xg", y="team", orientation="h", text="total_xg", title="xG by team")
    xg_fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    xg_fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=420, margin=dict(l=10, r=20, t=50, b=10))

    # Timeline
    timeline_fig = px.scatter(
        df,
        x="minute",
        y="team",
        color="team",
        size="shot_statsbomb_xg",
        symbol="is_goal",
        hover_data=["player", "match_label", "shot_outcome", "chance_quality", "shot_statsbomb_xg"],
        title="Shot timeline – symbol indicates goal / no goal",
    )
    timeline_fig.add_vline(x=45, line_dash="dash", line_color="gray")
    timeline_fig.update_layout(height=420, margin=dict(l=10, r=20, t=50, b=10))

    # Top players
    player_df = (
        df.groupby(["player", "team"])
        .agg(shots=("player", "size"), goals=("is_goal", "sum"), total_xg=("shot_statsbomb_xg", "sum"))
        .reset_index()
        .sort_values("total_xg", ascending=False)
        .head(12)
    )
    players_fig = px.bar(
        player_df,
        x="total_xg",
        y="player",
        color="team",
        orientation="h",
        title="Top players by xG",
        hover_data=["shots", "goals"],
    )
    players_fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=420, margin=dict(l=10, r=20, t=50, b=10))

    # Outcomes
    outcome_df = df.groupby(["shot_outcome", "team"]).size().reset_index(name="count")
    outcome_fig = px.bar(
        outcome_df,
        x="shot_outcome",
        y="count",
        color="team",
        barmode="group",
        title="Shot outcomes",
    )
    outcome_fig.update_layout(height=420, margin=dict(l=10, r=20, t=50, b=10), xaxis_title="Outcome", yaxis_title="Shots")

    return kpis, shot_map, xg_fig, timeline_fig, players_fig, outcome_fig


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
