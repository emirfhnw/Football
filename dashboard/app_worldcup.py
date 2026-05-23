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

# -----------------------------------------------------------------------------
# Data loading

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "processed" / "world_cup_2022_shots.csv"

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Missing file: {DATA_FILE}\n"
        "Run first: python src/build_worldcup_shots.py"
    )

shots = pd.read_csv(DATA_FILE)

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
# Visual style

COLORS = {
    "bg": "#eef2f7",
    "card": "#ffffff",
    "navy": "#0f172a",
    "text": "#243247",
    "muted": "#64748b",
    "border": "#dbe3ef",
    "blue": "#2563eb",
    "blue_dark": "#1e3a8a",
    "blue_soft": "#eff6ff",
    "orange_soft": "#fff7ed",
    "green_soft": "#ecfdf5",
    "pitch": "#e6f7ea",
    "purple": "#7c3aed",
    "red": "#ef4444",
    "green": "#16a34a",
}

CARD_STYLE = {
    "backgroundColor": COLORS["card"],
    "border": f"1px solid {COLORS['border']}",
    "borderRadius": "22px",
    "boxShadow": "0 14px 32px rgba(15, 23, 42, 0.08)",
}

# -----------------------------------------------------------------------------
# Option helpers


def option_list(values, all_label):
    clean_values = [v for v in sorted(values) if str(v) != "Unknown"]
    return [{"label": all_label, "value": "All"}] + [{"label": v, "value": v} for v in clean_values]


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
# Data helpers


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


def team_summary(df):
    if df.empty:
        return pd.DataFrame(
            columns=["team", "shots", "goals", "total_xg", "xg_per_shot", "conversion_rate", "goals_minus_xg"]
        )
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
# UI helpers


def panel(children, style=None):
    base = dict(CARD_STYLE)
    base.update({"padding": "18px"})
    if style:
        base.update(style)
    return html.Div(children, style=base)


def metric_card(title, value, subtitle, accent):
    return html.Div(
        [
            html.Div(title, style={"fontSize": "12px", "color": COLORS["muted"], "fontWeight": "800"}),
            html.Div(value, style={"fontSize": "30px", "fontWeight": "900", "color": COLORS["navy"], "marginTop": "4px"}),
            html.Div(subtitle, style={"fontSize": "11px", "color": "#94a3b8", "marginTop": "2px"}),
            html.Div(style={"height": "4px", "backgroundColor": accent, "borderRadius": "999px", "marginTop": "12px"}),
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


def section_title(number, title, subtitle):
    return html.Div(
        [
            html.Div(
                str(number),
                style={
                    "display": "inline-block",
                    "backgroundColor": COLORS["blue"],
                    "color": "white",
                    "borderRadius": "999px",
                    "width": "28px",
                    "height": "28px",
                    "lineHeight": "28px",
                    "textAlign": "center",
                    "fontWeight": "900",
                    "marginRight": "10px",
                },
            ),
            html.Span(title, style={"fontWeight": "900", "fontSize": "18px", "color": COLORS["navy"]}),
            html.P(subtitle, style={"fontSize": "13px", "color": COLORS["muted"], "lineHeight": "1.45", "margin": "9px 0 0 0"}),
        ],
        style={"marginBottom": "10px"},
    )


def empty_figure(title):
    fig = go.Figure()
    fig.update_layout(
        title=title,
        annotations=[dict(text="No data for current filters", x=0.5, y=0.5, showarrow=False, xref="paper", yref="paper")],
        height=430,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial", color=COLORS["navy"]),
    )
    return fig


def clean_layout(fig, height=430):
    fig.update_layout(
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial", size=12, color=COLORS["navy"]),
        margin=dict(l=20, r=20, t=58, b=38),
        legend_title_text="",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#eef2f7", zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)
    return fig

# -----------------------------------------------------------------------------
# Figure builders


def create_quality_figure(df):
    summary = team_summary(df)
    if summary.empty:
        return empty_figure("Volume vs quality")

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
        title="Volume vs quality: more shots are not automatically better chances",
        labels={
            "shots": "Number of shots",
            "xg_per_shot": "xG per shot",
            "goals_minus_xg": "Goals - xG",
        },
        size_max=42,
    )
    fig.add_annotation(
        text="Upper right = many shots and strong average chance quality",
        xref="paper",
        yref="paper",
        x=0.02,
        y=0.98,
        showarrow=False,
        bgcolor="rgba(255,255,255,0.88)",
        bordercolor="#dbe3ef",
        font=dict(size=12),
    )
    fig.update_layout(coloraxis_colorbar=dict(title="Goals - xG"))
    return clean_layout(fig, 450)


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
        title = "Shot map: high-quality chances and goals only in overview mode"
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
        height=535,
        margin=dict(l=10, r=10, t=60, b=10),
        plot_bgcolor=COLORS["pitch"],
        paper_bgcolor="white",
        legend=dict(orientation="h", y=-0.04),
    )
    return fig


def create_timeline_figure(df):
    if df.empty:
        return empty_figure("Timing")

    if df["match_label"].nunique() == 1:
        fig = px.scatter(
            df,
            x="minute",
            y="team",
            color="team",
            size="shot_statsbomb_xg",
            symbol="is_goal",
            hover_data=["player", "shot_outcome", "chance_quality", "shot_statsbomb_xg"],
            title="Match timeline: when did shots and high-xG chances happen?",
        )
        fig.add_vline(x=45, line_dash="dash", line_color="gray")
    else:
        temp = df.copy()
        temp["minute_bin_start"] = (temp["minute"] // 15 * 15).astype(int)
        temp["minute_bin"] = temp["minute_bin_start"].astype(str) + "-" + (temp["minute_bin_start"] + 14).astype(str)
        timeline = (
            temp.groupby(["minute_bin_start", "minute_bin"])
            .agg(shots=("team", "size"), total_xg=("shot_statsbomb_xg", "sum"))
            .reset_index()
            .sort_values("minute_bin_start")
        )
        fig = px.bar(
            timeline,
            x="minute_bin",
            y="total_xg",
            text="shots",
            title="Tournament timing: total xG by 15-minute phase",
            labels={"minute_bin": "Minute phase", "total_xg": "Total xG", "shots": "Shots"},
        )
        fig.update_traces(texttemplate="%{text} shots", textposition="outside")
    return clean_layout(fig, 535)


def create_efficiency_figure(df):
    summary = team_summary(df)
    if summary.empty:
        return empty_figure("Finishing efficiency")

    summary = summary[summary["shots"] >= 3].copy()
    if len(summary) > 12:
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
        title="Finishing efficiency: who scored more or fewer goals than expected?",
        labels={"goals_minus_xg": "Goals - xG", "team": "Team"},
        hover_data={"goals": True, "total_xg": ":.2f", "conversion_rate": ":.1%", "shots": True},
    )
    fig.add_vline(x=0, line_dash="dash", line_color="#334155")
    fig.update_layout(coloraxis_showscale=False)
    return clean_layout(fig, 440)


def create_chance_quality_figure(df):
    if df.empty:
        return empty_figure("Chance quality mix")

    summary = team_summary(df).sort_values("total_xg", ascending=False).head(10)
    temp = df[df["team"].isin(summary["team"])].copy()
    quality_counts = temp.groupby(["team", "chance_quality"]).size().reset_index(name="shots")
    totals = quality_counts.groupby("team")["shots"].transform("sum")
    quality_counts["share"] = quality_counts["shots"] / totals

    fig = px.bar(
        quality_counts,
        x="team",
        y="share",
        color="chance_quality",
        category_orders={"chance_quality": ["Low", "Medium", "High"]},
        title="Chance quality mix: share of low, medium and high-quality chances",
        labels={"share": "Share of shots", "team": "Team", "chance_quality": "Chance quality"},
    )
    fig.update_yaxes(tickformat=".0%")
    return clean_layout(fig, 440)


def create_player_figure(df):
    if df.empty:
        return empty_figure("Key players")

    player_df = (
        df.groupby(["player", "team"])
        .agg(
            shots=("player", "size"),
            goals=("is_goal", "sum"),
            total_xg=("shot_statsbomb_xg", "sum"),
            xg_per_shot=("shot_statsbomb_xg", "mean"),
        )
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
        title="Key players: who generated the most total xG?",
        hover_data={"shots": True, "goals": True, "xg_per_shot": ":.3f"},
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return clean_layout(fig, 440)


def create_match_figure(df):
    if df.empty:
        return empty_figure("Match comparison")

    match_df = (
        df.groupby("match_label")
        .agg(shots=("match_label", "size"), goals=("is_goal", "sum"), total_xg=("shot_statsbomb_xg", "sum"))
        .reset_index()
        .sort_values("total_xg", ascending=False)
        .head(10)
    )
    fig = px.bar(
        match_df,
        x="total_xg",
        y="match_label",
        orientation="h",
        text="goals",
        title="Matches with the highest total chance quality",
        labels={"total_xg": "Total xG", "match_label": "Match"},
        hover_data={"shots": True, "goals": True},
    )
    fig.update_traces(texttemplate="%{text} goals", textposition="outside")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return clean_layout(fig, 440)

# -----------------------------------------------------------------------------
# App layout

app = Dash(__name__)
app.title = "World Cup 2022 Shot Quality Explorer"

app.layout = html.Div(
    [
        html.Div(
            [
                html.Div("FIFA WORLD CUP 2022", style={"fontSize": "13px", "fontWeight": "900", "letterSpacing": "0.12em", "color": "#bfdbfe"}),
                html.H1("Shot Quality Explorer", style={"fontSize": "46px", "margin": "8px 0", "color": "white"}),
                html.P(
                    "A compact football analytics dashboard for comparing shot volume, chance quality, locations and finishing efficiency.",
                    style={"fontSize": "17px", "color": "#dbeafe", "maxWidth": "1050px", "lineHeight": "1.55", "margin": "0"},
                ),
            ],
            style={"background": "linear-gradient(135deg, #0f172a, #1d4ed8)", "padding": "34px 38px", "borderRadius": "0 0 32px 32px"},
        ),

        html.Div(
            [
                panel(
                    [
                        html.Div([html.Strong("Use case: "), "A fan, student analyst or assistant coach wants to know whether a team was actually dangerous or only took many low-quality shots."], style={"fontSize": "14px", "marginBottom": "8px", "lineHeight": "1.45"}),
                        html.Div([html.Strong("How to read it: "), "Volume = shots, quality = xG, space = shot map, efficiency = goals minus xG. The filters turn the tournament overview into team, match or player analysis."], style={"fontSize": "14px", "lineHeight": "1.45"}),
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
                        section_title("A", "Filters", "Start broad, then narrow down. Team selection changes available matches and players."),
                        html.Label("Team", style={"fontWeight": "800"}),
                        dcc.Dropdown(id="team-filter", options=team_options, value="All", clearable=False),
                        html.Br(),
                        html.Label("Match", style={"fontWeight": "800"}),
                        dcc.Dropdown(id="match-filter", options=get_match_options(), value="All", clearable=False),
                        html.Br(),
                        html.Label("Player", style={"fontWeight": "800"}),
                        dcc.Dropdown(id="player-filter", options=get_player_options(), value="All", clearable=False),
                        html.Br(),
                        html.Label("Shot outcome", style={"fontWeight": "800"}),
                        dcc.Dropdown(id="outcome-filter", options=outcome_options, value="All", clearable=False),
                        html.Br(),
                        html.Label("Chance quality", style={"fontWeight": "800"}),
                        dcc.Dropdown(id="quality-filter", options=quality_options, value="All", clearable=False),
                        html.Br(),
                        html.Label("Minute range", style={"fontWeight": "800"}),
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
                        dcc.Tabs(
                            id="main-tabs",
                            value="overview",
                            children=[
                                dcc.Tab(label="Overview", value="overview"),
                                dcc.Tab(label="Pitch & Time", value="pitch_time"),
                                dcc.Tab(label="Players & Matches", value="players_matches"),
                            ],
                            style={"marginBottom": "12px"},
                        ),
                        html.Div(id="tab-content"),
                    ],
                    style={"width": "73%", "display": "inline-block", "verticalAlign": "top", "marginLeft": "2%"},
                ),
            ],
            style={"padding": "0 30px 30px 30px"},
        ),
    ],
    style={"backgroundColor": COLORS["bg"], "fontFamily": "Arial, sans-serif", "minHeight": "100vh"},
)

# -----------------------------------------------------------------------------
# Dependent filter callbacks


@app.callback(
    Output("match-filter", "options"),
    Output("match-filter", "value"),
    Input("team-filter", "value"),
    State("match-filter", "value"),
)
def update_match_options(team, current_match):
    options = get_match_options(team)
    values = [opt["value"] for opt in options]
    return options, current_match if current_match in values else "All"


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
    return options, current_player if current_player in values else "All"

# -----------------------------------------------------------------------------
# Main dashboard callback


@app.callback(
    Output("insight-container", "children"),
    Output("kpi-container", "children"),
    Output("tab-content", "children"),
    Input("team-filter", "value"),
    Input("match-filter", "value"),
    Input("player-filter", "value"),
    Input("outcome-filter", "value"),
    Input("quality-filter", "value"),
    Input("minute-filter", "value"),
    Input("main-tabs", "value"),
)
def update_dashboard(team, match, player, outcome, quality, minute_range, active_tab):
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
            f"Current view: {total_shots:,} shots, {total_goals:,} goals and {total_xg:.2f} total xG. "
            f"Highest total xG in this selection: {best_team['team']} with {best_team['total_xg']:.2f} xG. "
            "Use the tabs to inspect volume/quality, pitch/time patterns, and key players or matches."
        )

    insight = panel(
        [
            html.Div("Current insight", style={"fontWeight": "900", "fontSize": "15px", "color": COLORS["navy"], "marginBottom": "6px"}),
            html.Div(insight_text, style={"fontSize": "14px", "lineHeight": "1.55", "color": COLORS["text"]}),
        ],
        style={"backgroundColor": COLORS["orange_soft"], "border": "1px solid #fed7aa"},
    )

    kpis = [
        metric_card("Shots", f"{total_shots:,}", "Volume", COLORS["blue"]),
        metric_card("Goals", f"{total_goals:,}", "Actual outcome", COLORS["green"]),
        metric_card("Total xG", f"{total_xg:.2f}", "Chance quality sum", COLORS["purple"]),
        metric_card("xG / Shot", f"{xg_per_shot:.3f}", "Average quality", "#f97316"),
        metric_card("Conversion", f"{conversion_rate:.1%}", "Goals / shots", COLORS["red"]),
    ]

    if active_tab == "overview":
        content = html.Div(
            [
                panel([section_title("1", "Volume vs quality", "Shows whether teams simply shoot often or actually create high-value chances."), dcc.Graph(figure=create_quality_figure(df))]),
                html.Div(style={"height": "16px"}),
                html.Div(
                    [
                        html.Div([panel([section_title("2", "Finishing efficiency", "Goals minus xG highlights over- and under-performance in finishing."), dcc.Graph(figure=create_efficiency_figure(df))])], style={"width": "49%", "display": "inline-block", "verticalAlign": "top"}),
                        html.Div([panel([section_title("3", "Chance quality mix", "Shows whether teams create mostly low, medium or high-quality chances."), dcc.Graph(figure=create_chance_quality_figure(df))])], style={"width": "49%", "display": "inline-block", "verticalAlign": "top", "marginLeft": "2%"}),
                    ]
                ),
            ]
        )
    elif active_tab == "pitch_time":
        content = html.Div(
            [
                html.Div([panel([section_title("1", "Shot locations", "The map explains where dangerous chances happen. Filter to a team or match for detailed reading."), dcc.Graph(figure=create_pitch_figure(df))])], style={"width": "58%", "display": "inline-block", "verticalAlign": "top"}),
                html.Div([panel([section_title("2", "Timing", "For one match this becomes a shot-by-shot timeline. For many matches it summarizes xG by phase."), dcc.Graph(figure=create_timeline_figure(df))])], style={"width": "40%", "display": "inline-block", "verticalAlign": "top", "marginLeft": "2%"}),
            ]
        )
    else:
        content = html.Div(
            [
                html.Div([panel([section_title("1", "Key players", "Identifies who generated the most dangerous shots in the selected data."), dcc.Graph(figure=create_player_figure(df))])], style={"width": "49%", "display": "inline-block", "verticalAlign": "top"}),
                html.Div([panel([section_title("2", "High-xG matches", "Shows which matches had the highest combined chance quality."), dcc.Graph(figure=create_match_figure(df))])], style={"width": "49%", "display": "inline-block", "verticalAlign": "top", "marginLeft": "2%"}),
            ]
        )

    return insight, kpis, content


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
