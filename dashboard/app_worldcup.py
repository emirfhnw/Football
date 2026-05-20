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

MINUTE_MAX = int(max(120, shots["minute"].max()))

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

COLORS = {
    "bg": "#f5f7fb",
    "panel": "#ffffff",
    "navy": "#0f172a",
    "muted": "#64748b",
    "border": "#e2e8f0",
    "blue": "#2563eb",
    "light_blue": "#eff6ff",
    "green": "#ecfdf5",
}


def filter_data(team, match, player, outcome, quality, minute_range):
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


def panel(children, style=None):
    base = {
        "backgroundColor": COLORS["panel"],
        "border": f"1px solid {COLORS['border']}",
        "borderRadius": "18px",
        "padding": "18px",
        "boxShadow": "0 8px 24px rgba(15, 23, 42, 0.06)",
    }
    if style:
        base.update(style)
    return html.Div(children, style=base)


def section_title(title, subtitle):
    return html.Div(
        [
            html.H3(title, style={"margin": "0", "fontSize": "18px", "color": COLORS["navy"]}),
            html.P(subtitle, style={"margin": "6px 0 0 0", "fontSize": "13px", "color": COLORS["muted"], "lineHeight": "1.45"}),
        ],
        style={"marginBottom": "8px"},
    )


def metric_card(title, value, subtitle=""):
    return html.Div(
        [
            html.Div(title, style={"fontSize": "12px", "color": COLORS["muted"], "fontWeight": "600"}),
            html.Div(value, style={"fontSize": "28px", "fontWeight": "800", "color": COLORS["navy"], "marginTop": "4px"}),
            html.Div(subtitle, style={"fontSize": "11px", "color": "#94a3b8", "marginTop": "2px"}),
        ],
        style={
            "backgroundColor": COLORS["panel"],
            "border": f"1px solid {COLORS['border']}",
            "borderRadius": "16px",
            "padding": "15px",
            "boxShadow": "0 4px 14px rgba(15, 23, 42, 0.05)",
            "width": "19%",
            "display": "inline-block",
            "marginRight": "1%",
            "boxSizing": "border-box",
            "verticalAlign": "top",
        },
    )


def empty_figure(title):
    fig = go.Figure()
    fig.update_layout(
        title=title,
        annotations=[dict(text="No data for the current filters", x=0.5, y=0.5, showarrow=False, xref="paper", yref="paper")],
        height=430,
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    return fig


def clean_layout(fig, height=430):
    fig.update_layout(
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial", size=12, color=COLORS["navy"]),
        margin=dict(l=20, r=20, t=55, b=35),
        legend_title_text="",
    )
    return fig


def create_pitch_figure(df):
    if df.empty:
        return empty_figure("Where were dangerous shots taken?")

    fig = go.Figure()
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

    # Full tournament overview can be cluttered. For the all-data view, keep the pitch readable by showing
    # high-quality chances and goals. Once users filter, all shots in that selection are shown.
    overview_mode = len(plot_df) > 400
    if overview_mode:
        plot_df = plot_df[(plot_df["chance_quality"] == "High") | (plot_df["is_goal"])]
        title = "Where were the best chances taken?  High-quality chances and goals shown for readability"
    else:
        title = "Where were the selected shots taken?  Size = xG, symbol = goal/no goal"

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
        title=title,
        height=520,
        margin=dict(l=10, r=10, t=65, b=10),
        plot_bgcolor="#dcfce7",
        paper_bgcolor="white",
        legend=dict(orientation="h", y=-0.05),
    )
    return fig


app = Dash(__name__)
app.title = "World Cup 2022 Shot Quality Explorer"

app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.Div("FIFA World Cup 2022", style={"fontSize": "13px", "fontWeight": "700", "letterSpacing": "0.08em", "color": "#bfdbfe"}),
                        html.H1("Shot Quality Explorer", style={"fontSize": "42px", "margin": "8px 0 8px 0", "color": "white"}),
                        html.P(
                            "A focused dashboard to compare shot quality, shot locations and finishing efficiency between teams, matches and players.",
                            style={"fontSize": "16px", "color": "#dbeafe", "maxWidth": "900px", "lineHeight": "1.5"},
                        ),
                    ]
                )
            ],
            style={"background": "linear-gradient(135deg, #0f172a, #1d4ed8)", "padding": "30px 34px", "borderRadius": "0 0 26px 26px"},
        ),

        html.Div(
            [
                panel(
                    [
                        html.Div(
                            [
                                html.Strong("Research question: "),
                                "How do shot quality, shot locations and finishing efficiency differ between teams and matches in the FIFA World Cup 2022?",
                            ],
                            style={"fontSize": "14px", "color": COLORS["navy"], "marginBottom": "8px"},
                        ),
                        html.Div(
                            [
                                html.Strong("How to read it: "),
                                "xG estimates the probability that a shot becomes a goal. Higher xG means a better chance. Chance quality: Low < 0.05, Medium 0.05–0.20, High ≥ 0.20.",
                            ],
                            style={"fontSize": "14px", "color": COLORS["navy"], "lineHeight": "1.45"},
                        ),
                    ],
                    style={"backgroundColor": COLORS["light_blue"], "border": "1px solid #bfdbfe"},
                )
            ],
            style={"padding": "22px 28px 10px 28px"},
        ),

        html.Div(id="insight-container", style={"padding": "0 28px 10px 28px"}),
        html.Div(id="kpi-container", style={"padding": "0 28px 18px 28px"}),

        html.Div(
            [
                panel(
                    [
                        section_title("Filters", "Use the filters to move from tournament overview to team, match or player detail."),
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
                            max=MINUTE_MAX,
                            step=1,
                            value=[0, MINUTE_MAX],
                            marks={i: str(i) for i in range(0, MINUTE_MAX + 1, 15)},
                            tooltip={"placement": "bottom", "always_visible": False},
                        ),
                        html.Div(
                            [
                                html.Strong("Linked views: "),
                                "Every chart below uses the same filtered data. Change one filter and the full story updates.",
                            ],
                            style={"fontSize": "12px", "lineHeight": "1.45", "color": COLORS["muted"], "marginTop": "18px"},
                        ),
                    ],
                    style={"width": "25%", "display": "inline-block", "verticalAlign": "top", "boxSizing": "border-box"},
                ),
                html.Div(
                    [
                        panel(
                            [
                                section_title("1. Chance creation quality", "This chart answers: who creates many shots and who creates valuable shots? Higher xG means better chance quality."),
                                dcc.Graph(id="team-quality-chart"),
                            ]
                        )
                    ],
                    style={"width": "73%", "display": "inline-block", "verticalAlign": "top", "marginLeft": "2%"},
                ),
            ],
            style={"padding": "0 28px 18px 28px"},
        ),

        html.Div(
            [
                html.Div(
                    [
                        panel([section_title("2. Shot locations", "This shows where dangerous chances happen. Close and central shots usually have higher xG."), dcc.Graph(id="shot-map")])
                    ],
                    style={"width": "58%", "display": "inline-block", "verticalAlign": "top"},
                ),
                html.Div(
                    [
                        panel([section_title("3. Timing of shots", "This shows when shots happened and whether dangerous moments came in specific match phases."), dcc.Graph(id="shot-timeline")])
                    ],
                    style={"width": "40%", "display": "inline-block", "verticalAlign": "top", "marginLeft": "2%"},
                ),
            ],
            style={"padding": "0 28px 18px 28px"},
        ),

        html.Div(
            [
                html.Div(
                    [
                        panel([section_title("4. Finishing efficiency", "This compares actual goals with expected goals. Positive values mean a team scored more than its xG."), dcc.Graph(id="efficiency-chart")])
                    ],
                    style={"width": "49%", "display": "inline-block", "verticalAlign": "top"},
                ),
                html.Div(
                    [
                        panel([section_title("5. Key players", "This identifies players who contributed most to total xG in the selected data."), dcc.Graph(id="top-players")])
                    ],
                    style={"width": "49%", "display": "inline-block", "verticalAlign": "top", "marginLeft": "2%"},
                ),
            ],
            style={"padding": "0 28px 28px 28px"},
        ),
    ],
    style={"backgroundColor": COLORS["bg"], "fontFamily": "Arial, sans-serif", "minHeight": "100vh"},
)


@app.callback(
    Output("insight-container", "children"),
    Output("kpi-container", "children"),
    Output("team-quality-chart", "figure"),
    Output("shot-map", "figure"),
    Output("shot-timeline", "figure"),
    Output("efficiency-chart", "figure"),
    Output("top-players", "figure"),
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

    insight_text = "No data for the current filters. Try removing one filter."
    if not df.empty:
        grouped = (
            df.groupby("team")
            .agg(shots=("team", "size"), goals=("is_goal", "sum"), total_xg=("shot_statsbomb_xg", "sum"))
            .reset_index()
        )
        top_xg = grouped.sort_values("total_xg", ascending=False).iloc[0]
        insight_text = (
            f"Current selection contains {total_shots:,} shots and {total_goals:,} goals. "
            f"The strongest team by total xG in this selection is {top_xg['team']} with {top_xg['total_xg']:.2f} xG. "
            "Use the filters to compare whether this comes from many shots, better locations or more efficient finishing."
        )

    insight = panel(
        [
            html.Div("Main reading of the current view", style={"fontWeight": "800", "fontSize": "14px", "color": COLORS["navy"], "marginBottom": "6px"}),
            html.Div(insight_text, style={"fontSize": "14px", "lineHeight": "1.45", "color": "#334155"}),
        ],
        style={"backgroundColor": "#fff7ed", "border": "1px solid #fed7aa"},
    )

    kpis = [
        metric_card("Shots", f"{total_shots:,}", "How often teams finished"),
        metric_card("Goals", f"{total_goals:,}", "Actual result of shots"),
        metric_card("Total xG", f"{total_xg:.2f}", "Overall chance quality"),
        metric_card("xG / Shot", f"{xg_per_shot:.3f}", "Average shot quality"),
        metric_card("Conversion", f"{conversion_rate:.1%}", "Goals / shots"),
    ]

    if df.empty:
        return insight, kpis, empty_figure("Chance creation quality"), empty_figure("Shot map"), empty_figure("Timeline"), empty_figure("Efficiency"), empty_figure("Top players")

    team_df = (
        df.groupby("team")
        .agg(
            shots=("team", "size"),
            goals=("is_goal", "sum"),
            total_xg=("shot_statsbomb_xg", "sum"),
            xg_per_shot=("shot_statsbomb_xg", "mean"),
        )
        .reset_index()
    )
    team_df["conversion_rate"] = team_df["goals"] / team_df["shots"]
    team_df["goals_minus_xg"] = team_df["goals"] - team_df["total_xg"]

    quality_fig = px.scatter(
        team_df,
        x="shots",
        y="total_xg",
        size="goals",
        color="team",
        hover_data={"xg_per_shot": ":.3f", "conversion_rate": ":.1%", "goals": True},
        title="Shots vs total xG – volume compared with chance quality",
        labels={"shots": "Shots", "total_xg": "Total xG"},
        size_max=35,
    )
    quality_fig = clean_layout(quality_fig, height=430)

    shot_map = create_pitch_figure(df)

    timeline_fig = px.scatter(
        df,
        x="minute",
        y="team",
        color="team",
        size="shot_statsbomb_xg",
        symbol="is_goal",
        hover_data=["player", "match_label", "shot_outcome", "chance_quality", "shot_statsbomb_xg"],
        title="Shot timeline – larger points have higher xG",
    )
    timeline_fig.add_vline(x=45, line_dash="dash", line_color="gray")
    timeline_fig = clean_layout(timeline_fig, height=520)

    efficiency_df = team_df.sort_values("goals_minus_xg", ascending=False).head(12)
    efficiency_fig = px.bar(
        efficiency_df,
        x="goals_minus_xg",
        y="team",
        orientation="h",
        color="goals_minus_xg",
        color_continuous_scale="RdBu",
        title="Finishing efficiency: goals minus xG",
        labels={"goals_minus_xg": "Goals - xG", "team": "Team"},
        hover_data={"goals": True, "total_xg": ":.2f", "conversion_rate": ":.1%"},
    )
    efficiency_fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
    efficiency_fig = clean_layout(efficiency_fig, height=430)

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
        title="Top players by total xG",
        hover_data=["shots", "goals"],
    )
    players_fig.update_layout(yaxis={"categoryorder": "total ascending"})
    players_fig = clean_layout(players_fig, height=430)

    return insight, kpis, quality_fig, shot_map, timeline_fig, efficiency_fig, players_fig


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
