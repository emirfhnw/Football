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
from dash import Dash, dcc, html, Input, Output, State

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "processed" / "world_cup_2022_shots.csv"

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Missing file: {DATA_FILE}\n"
        "Run first: python src/build_worldcup_shots.py"
    )

shots = pd.read_csv(DATA_FILE)

# -----------------------------------------------------------------------------
# Data cleanup

shots["is_goal"] = shots["is_goal"].astype(str).str.lower().eq("true")
shots["shot_statsbomb_xg"] = pd.to_numeric(shots["shot_statsbomb_xg"], errors="coerce").fillna(0)
shots["minute"] = pd.to_numeric(shots["minute"], errors="coerce").fillna(0)
shots["x"] = pd.to_numeric(shots["x"], errors="coerce")
shots["y"] = pd.to_numeric(shots["y"], errors="coerce")
shots["distance_to_goal"] = pd.to_numeric(shots["distance_to_goal"], errors="coerce")

for col in ["team", "player", "match_label", "shot_outcome", "chance_quality", "competition_stage"]:
    shots[col] = shots[col].fillna("Unknown").astype(str)

MINUTE_MAX = int(max(120, shots["minute"].max()))

# -----------------------------------------------------------------------------
# Design constants

COLORS = {
    "bg": "#eef2f7",
    "card": "#ffffff",
    "navy": "#0f172a",
    "text": "#1e293b",
    "muted": "#64748b",
    "border": "#dbe3ef",
    "blue": "#2563eb",
    "blue_dark": "#1e40af",
    "blue_soft": "#eff6ff",
    "orange_soft": "#fff7ed",
    "green_pitch": "#e8f7ed",
    "danger": "#ef4444",
}

CARD_STYLE = {
    "backgroundColor": COLORS["card"],
    "border": f"1px solid {COLORS['border']}",
    "borderRadius": "22px",
    "boxShadow": "0 12px 30px rgba(15, 23, 42, 0.08)",
}

# -----------------------------------------------------------------------------
# Option helpers


def option_list(values, all_label):
    return [{"label": all_label, "value": "All"}] + [
        {"label": value, "value": value} for value in sorted(values) if str(value) != "Unknown"
    ]


team_options = option_list(shots["team"].unique(), "All teams")
outcome_options = option_list(shots["shot_outcome"].unique(), "All outcomes")
quality_options = [{"label": "All qualities", "value": "All"}] + [
    {"label": q, "value": q} for q in ["Low", "Medium", "High"] if q in shots["chance_quality"].unique()
]


def get_match_options(team="All"):
    df = shots.copy()
    if team != "All":
        df = df[df["team"] == team]
    return option_list(df["match_label"].unique(), "All matches")


def get_player_options(team="All", match="All"):
    df = shots.copy()
    if team != "All":
        df = df[df["team"] == team]
    if match != "All":
        df = df[df["match_label"] == match]
    return option_list(df["player"].unique(), "All players")


# -----------------------------------------------------------------------------
# Utility functions


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
    return df[(df["minute"] >= minute_range[0]) & (df["minute"] <= minute_range[1])]


def panel(children, style=None):
    base = dict(CARD_STYLE)
    base.update({"padding": "18px"})
    if style:
        base.update(style)
    return html.Div(children, style=base)


def section_title(number, title, subtitle):
    return html.Div(
        [
            html.Div(
                f"{number}",
                style={
                    "display": "inline-block",
                    "backgroundColor": COLORS["blue"],
                    "color": "white",
                    "borderRadius": "999px",
                    "width": "26px",
                    "height": "26px",
                    "lineHeight": "26px",
                    "textAlign": "center",
                    "fontWeight": "800",
                    "marginRight": "10px",
                },
            ),
            html.Span(title, style={"fontWeight": "800", "fontSize": "18px", "color": COLORS["navy"]}),
            html.P(subtitle, style={"fontSize": "13px", "color": COLORS["muted"], "lineHeight": "1.45", "margin": "8px 0 0 0"}),
        ],
        style={"marginBottom": "10px"},
    )


def metric_card(title, value, subtitle, accent="#2563eb"):
    return html.Div(
        [
            html.Div(title, style={"fontSize": "12px", "color": COLORS["muted"], "fontWeight": "700"}),
            html.Div(value, style={"fontSize": "30px", "fontWeight": "900", "color": COLORS["navy"], "marginTop": "5px"}),
            html.Div(subtitle, style={"fontSize": "11px", "color": "#94a3b8", "marginTop": "3px"}),
            html.Div(style={"height": "4px", "backgroundColor": accent, "borderRadius": "10px", "marginTop": "12px"}),
        ],
        style={
            **CARD_STYLE,
            "padding": "16px",
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
        annotations=[dict(text="No data for current filters", x=0.5, y=0.5, showarrow=False, xref="paper", yref="paper")],
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
        margin=dict(l=18, r=18, t=55, b=35),
        legend_title_text="",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#eef2f7")
    fig.update_yaxes(showgrid=False)
    return fig


def team_summary(df):
    if df.empty:
        return pd.DataFrame(columns=["team", "shots", "goals", "total_xg", "xg_per_shot", "conversion_rate", "goals_minus_xg"])
    summary = (
        df.groupby("team")
        .agg(
            shots=("team", "size"),
            goals=("is_goal", "sum"),
            total_xg=("shot_statsbomb_xg", "sum"),
            xg_per_shot=("shot_statsbomb_xg", "mean"),
        )
        .reset_index()
    )
    summary["conversion_rate"] = summary["goals"] / summary["shots"]
    summary["goals_minus_xg"] = summary["goals"] - summary["total_xg"]
    return summary


# -----------------------------------------------------------------------------
# Figure builders


def create_pitch_figure(df):
    if df.empty:
        return empty_figure("Shot map")

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

    overview_mode = len(plot_df) > 450
    if overview_mode:
        plot_df = plot_df[(plot_df["chance_quality"] == "High") | (plot_df["is_goal"])]
        title = "Shot map: high-quality chances and goals (overview mode)"
    else:
        title = "Shot map: every selected shot"

    fig_px = px.scatter(
        plot_df,
        x="x",
        y="y",
        color="team",
        symbol="goal_label",
        size="shot_statsbomb_xg",
        size_max=26,
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
        height=540,
        margin=dict(l=10, r=10, t=60, b=10),
        plot_bgcolor=COLORS["green_pitch"],
        paper_bgcolor="white",
        legend=dict(orientation="h", y=-0.04),
    )
    return fig


def create_quality_figure(df):
    summary = team_summary(df)
    if summary.empty:
        return empty_figure("Shot volume vs chance quality")

    if len(summary) > 14:
        summary = summary.sort_values("total_xg", ascending=False).head(14)

    fig = px.scatter(
        summary,
        x="shots",
        y="xg_per_shot",
        size="total_xg",
        color="goals_minus_xg",
        color_continuous_scale="RdBu",
        hover_name="team",
        hover_data={"total_xg": ":.2f", "goals": True, "conversion_rate": ":.1%", "goals_minus_xg": ":.2f"},
        title="Shot volume vs average shot quality",
        labels={
            "shots": "Number of shots",
            "xg_per_shot": "xG per shot (average shot quality)",
            "goals_minus_xg": "Goals - xG",
        },
        size_max=42,
    )
    fig.add_annotation(
        text="Upper right = many shots and good average quality",
        xref="paper",
        yref="paper",
        x=0.02,
        y=0.98,
        showarrow=False,
        bgcolor="rgba(255,255,255,0.85)",
        bordercolor="#dbe3ef",
        font=dict(size=12),
    )
    fig.update_layout(coloraxis_colorbar=dict(title="Goals - xG"))
    return clean_layout(fig, 440)


def create_efficiency_figure(df):
    summary = team_summary(df)
    if summary.empty:
        return empty_figure("Finishing efficiency")
    summary = summary[summary["shots"] >= 3].copy()
    if len(summary) > 12:
        # Show strongest over- and under-performers, not just one side.
        top = summary.sort_values("goals_minus_xg", ascending=False).head(6)
        bottom = summary.sort_values("goals_minus_xg", ascending=True).head(6)
        summary = pd.concat([top, bottom]).drop_duplicates("team")
    summary = summary.sort_values("goals_minus_xg", ascending=True)
    fig = px.bar(
        summary,
        x="goals_minus_xg",
        y="team",
        orientation="h",
        color="goals_minus_xg",
        color_continuous_scale="RdBu",
        title="Finishing efficiency: actual goals compared with xG",
        labels={"goals_minus_xg": "Goals - xG", "team": "Team"},
        hover_data={"goals": True, "total_xg": ":.2f", "conversion_rate": ":.1%", "shots": True},
    )
    fig.add_vline(x=0, line_dash="dash", line_color="#334155")
    fig.update_layout(coloraxis_showscale=False)
    return clean_layout(fig, 440)


def create_timeline_figure(df):
    if df.empty:
        return empty_figure("Shot timing")
    if df["match_label"].nunique() == 1:
        fig = px.scatter(
            df,
            x="minute",
            y="team",
            color="team",
            size="shot_statsbomb_xg",
            symbol="is_goal",
            hover_data=["player", "shot_outcome", "chance_quality", "shot_statsbomb_xg"],
            title="Shot timeline for selected match",
        )
        fig.add_vline(x=45, line_dash="dash", line_color="gray")
    else:
        temp = df.copy()
        temp["minute_bin"] = (temp["minute"] // 15 * 15).astype(int).astype(str) + "-" + ((temp["minute"] // 15 * 15) + 14).astype(int).astype(str)
        timeline = temp.groupby("minute_bin", sort=False).agg(shots=("team", "size"), total_xg=("shot_statsbomb_xg", "sum")).reset_index()
        fig = px.bar(
            timeline,
            x="minute_bin",
            y="total_xg",
            text="shots",
            title="When does chance quality appear? Total xG by 15-minute phase",
            labels={"minute_bin": "Minute phase", "total_xg": "Total xG", "shots": "Shots"},
        )
        fig.update_traces(texttemplate="%{text} shots", textposition="outside")
    return clean_layout(fig, 540)


def create_player_figure(df):
    if df.empty:
        return empty_figure("Key players")
    player_df = (
        df.groupby(["player", "team"])
        .agg(shots=("player", "size"), goals=("is_goal", "sum"), total_xg=("shot_statsbomb_xg", "sum"), xg_per_shot=("shot_statsbomb_xg", "mean"))
        .reset_index()
        .sort_values("total_xg", ascending=False)
        .head(12)
    )
    fig = px.bar(
        player_df,
        x="total_xg",
        y="player",
        color="team",
        orientation="h",
        title="Players who generated the most total xG",
        hover_data={"shots": True, "goals": True, "xg_per_shot": ":.3f"},
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return clean_layout(fig, 440)


def create_chance_quality_figure(df):
    if df.empty:
        return empty_figure("Chance quality mix")
    summary = team_summary(df).sort_values("total_xg", ascending=False).head(10)
    temp = df[df["team"].isin(summary["team"])].copy()
    quality_counts = temp.groupby(["team", "chance_quality"]).size().reset_index(name="shots")
    quality_order = ["Low", "Medium", "High"]
    fig = px.bar(
        quality_counts,
        x="team",
        y="shots",
        color="chance_quality",
        category_orders={"chance_quality": quality_order},
        title="Chance quality mix: how many low, medium and high-quality shots?",
        labels={"shots": "Shots", "team": "Team", "chance_quality": "Chance quality"},
    )
    return clean_layout(fig, 420)


# -----------------------------------------------------------------------------
# App layout

app = Dash(__name__)
app.title = "World Cup 2022 Shot Quality Explorer"

app.layout = html.Div(
    [
        html.Div(
            [
                html.Div("FIFA World Cup 2022", style={"fontSize": "13px", "fontWeight": "800", "letterSpacing": "0.10em", "color": "#bfdbfe"}),
                html.H1("Shot Quality Explorer", style={"fontSize": "44px", "margin": "8px 0", "color": "white"}),
                html.P(
                    "Compare who shoots often, who creates valuable chances, where those chances happen and who finishes efficiently.",
                    style={"fontSize": "17px", "color": "#dbeafe", "maxWidth": "1000px", "lineHeight": "1.55", "margin": "0"},
                ),
            ],
            style={"background": "linear-gradient(135deg, #0f172a, #1d4ed8)", "padding": "34px 38px", "borderRadius": "0 0 30px 30px"},
        ),

        html.Div(
            [
                panel(
                    [
                        html.Div([html.Strong("Research question: "), "How do shot quality, shot locations and finishing efficiency differ between teams and matches in the FIFA World Cup 2022?"], style={"fontSize": "14px", "marginBottom": "8px"}),
                        html.Div([html.Strong("Why these plots matter: "), "The dashboard separates four ideas: volume (shots), quality (xG), space (shot map) and efficiency (goals minus xG). The filters let you compare these ideas for any team, match or player."], style={"fontSize": "14px", "lineHeight": "1.45"}),
                        html.Div([html.Strong("xG: "), "Expected goals estimates how likely a shot is to become a goal. Low < 0.05, Medium 0.05–0.20, High ≥ 0.20."], style={"fontSize": "14px", "lineHeight": "1.45", "marginTop": "8px"}),
                    ],
                    style={"backgroundColor": COLORS["blue_soft"], "border": "1px solid #bfdbfe"},
                )
            ],
            style={"padding": "22px 30px 10px 30px"},
        ),

        html.Div(id="insight-container", style={"padding": "0 30px 12px 30px"}),
        html.Div(id="kpi-container", style={"padding": "0 30px 18px 30px"}),

        html.Div(
            [
                panel(
                    [
                        section_title("A", "Filters with a real purpose", "Use filters to move from tournament overview to a team, match or player. Match and player lists react to the selected team."),
                        html.Label("Team", style={"fontWeight": "700"}),
                        dcc.Dropdown(id="team-filter", options=team_options, value="All", clearable=False),
                        html.Br(),
                        html.Label("Match", style={"fontWeight": "700"}),
                        dcc.Dropdown(id="match-filter", options=get_match_options(), value="All", clearable=False),
                        html.Br(),
                        html.Label("Player", style={"fontWeight": "700"}),
                        dcc.Dropdown(id="player-filter", options=get_player_options(), value="All", clearable=False),
                        html.Br(),
                        html.Label("Shot outcome", style={"fontWeight": "700"}),
                        dcc.Dropdown(id="outcome-filter", options=outcome_options, value="All", clearable=False),
                        html.Br(),
                        html.Label("Chance quality", style={"fontWeight": "700"}),
                        dcc.Dropdown(id="quality-filter", options=quality_options, value="All", clearable=False),
                        html.Br(),
                        html.Label("Minute range", style={"fontWeight": "700"}),
                        dcc.RangeSlider(
                            id="minute-filter",
                            min=0,
                            max=MINUTE_MAX,
                            step=1,
                            value=[0, MINUTE_MAX],
                            marks={i: str(i) for i in range(0, MINUTE_MAX + 1, 30)},
                            tooltip={"placement": "bottom", "always_visible": False},
                        ),
                    ],
                    style={"width": "25%", "display": "inline-block", "verticalAlign": "top", "boxSizing": "border-box"},
                ),
                html.Div(
                    [
                        panel([section_title("1", "Volume vs quality", "This is the main comparison. A strong team is not just one that shoots often, but one that also creates high average xG."), dcc.Graph(id="quality-chart")])
                    ],
                    style={"width": "73%", "display": "inline-block", "verticalAlign": "top", "marginLeft": "2%"},
                ),
            ],
            style={"padding": "0 30px 18px 30px"},
        ),

        html.Div(
            [
                html.Div([panel([section_title("2", "Shot locations", "The shot map explains why xG differs. Better chances usually come from central and close locations."), dcc.Graph(id="shot-map")])], style={"width": "58%", "display": "inline-block", "verticalAlign": "top"}),
                html.Div([panel([section_title("3", "Timing", "For a whole tournament, this aggregates chance quality by match phase. For one match, it becomes a shot-by-shot timeline."), dcc.Graph(id="timeline-chart")])], style={"width": "40%", "display": "inline-block", "verticalAlign": "top", "marginLeft": "2%"}),
            ],
            style={"padding": "0 30px 18px 30px"},
        ),

        html.Div(
            [
                html.Div([panel([section_title("4", "Finishing efficiency", "Goals minus xG shows whether teams scored more or fewer goals than expected from their chances."), dcc.Graph(id="efficiency-chart")])], style={"width": "49%", "display": "inline-block", "verticalAlign": "top"}),
                html.Div([panel([section_title("5", "Chance quality mix", "This answers whether teams create mainly low, medium or high-quality shots."), dcc.Graph(id="chance-quality-chart")])], style={"width": "49%", "display": "inline-block", "verticalAlign": "top", "marginLeft": "2%"}),
            ],
            style={"padding": "0 30px 18px 30px"},
        ),

        html.Div(
            [
                panel([section_title("6", "Key players", "This connects the team-level analysis to the players who created the most dangerous shots."), dcc.Graph(id="player-chart")])
            ],
            style={"padding": "0 30px 30px 30px"},
        ),
    ],
    style={"backgroundColor": COLORS["bg"], "fontFamily": "Arial, sans-serif", "minHeight": "100vh"},
)


# -----------------------------------------------------------------------------
# Dependent filters


@app.callback(
    Output("match-filter", "options"),
    Output("match-filter", "value"),
    Input("team-filter", "value"),
    State("match-filter", "value"),
)
def update_match_options(team, current_match):
    options = get_match_options(team)
    values = [opt["value"] for opt in options]
    if current_match in values:
        return options, current_match
    return options, "All"


@app.callback(
    Output("player-filter", "options"),
    Output("player-filter", "value"),
    Input("team-filter", "value"),
    Input("match-filter", "value"),
    State("player-filter", "value"),
)
def update_player_options(team, match, current_player):
    options = get_player_options(team, match)
    values = [opt["value"] for opt in options]
    if current_player in values:
        return options, current_player
    return options, "All"


# -----------------------------------------------------------------------------
# Main dashboard callback


@app.callback(
    Output("insight-container", "children"),
    Output("kpi-container", "children"),
    Output("quality-chart", "figure"),
    Output("shot-map", "figure"),
    Output("timeline-chart", "figure"),
    Output("efficiency-chart", "figure"),
    Output("chance-quality-chart", "figure"),
    Output("player-chart", "figure"),
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

    if df.empty:
        insight_text = "No data for the current filters. Remove one filter or widen the minute range."
    else:
        summary = team_summary(df).sort_values("total_xg", ascending=False)
        best_team = summary.iloc[0]
        insight_text = (
            f"This view contains {total_shots:,} shots, {total_goals:,} goals and {total_xg:.2f} total xG. "
            f"The strongest team in this selection by total xG is {best_team['team']} ({best_team['total_xg']:.2f} xG). "
            "Read the dashboard from left to right: first volume vs quality, then shot locations, timing and finishing efficiency."
        )

    insight = panel(
        [
            html.Div("Current insight", style={"fontWeight": "900", "fontSize": "15px", "color": COLORS["navy"], "marginBottom": "6px"}),
            html.Div(insight_text, style={"fontSize": "14px", "lineHeight": "1.55", "color": COLORS["text"]}),
        ],
        style={"backgroundColor": COLORS["orange_soft"], "border": "1px solid #fed7aa"},
    )

    kpis = [
        metric_card("Shots", f"{total_shots:,}", "Volume", "#2563eb"),
        metric_card("Goals", f"{total_goals:,}", "Actual outcome", "#16a34a"),
        metric_card("Total xG", f"{total_xg:.2f}", "Chance quality sum", "#7c3aed"),
        metric_card("xG / Shot", f"{xg_per_shot:.3f}", "Average quality", "#f97316"),
        metric_card("Conversion", f"{conversion_rate:.1%}", "Goals / shots", "#ef4444"),
    ]

    if df.empty:
        return (
            insight,
            kpis,
            empty_figure("Shot volume vs quality"),
            empty_figure("Shot map"),
            empty_figure("Timeline"),
            empty_figure("Efficiency"),
            empty_figure("Chance quality mix"),
            empty_figure("Key players"),
        )

    return (
        insight,
        kpis,
        create_quality_figure(df),
        create_pitch_figure(df),
        create_timeline_figure(df),
        create_efficiency_figure(df),
        create_chance_quality_figure(df),
        create_player_figure(df),
    )


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
