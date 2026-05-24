from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .metrics import team_ranking
from .utils import BUILD_UP_COLORS, BUILD_UP_ORDER


TEMPLATE = "plotly_dark"
PAPER = "rgba(0,0,0,0)"
PLOT = "rgba(15,23,42,0.6)"
GRID = "rgba(255,255,255,0.08)"
FONT = "#f8fafc"


def style_figure(fig: go.Figure, height: int = 360) -> go.Figure:
    fig.update_layout(
        template=TEMPLATE,
        title=None,
        paper_bgcolor=PAPER,
        plot_bgcolor=PLOT,
        font=dict(color=FONT, family="Inter, system-ui, Segoe UI, sans-serif"),
        margin=dict(l=20, r=20, t=18, b=30),
        height=height,
        hoverlabel=dict(bgcolor="#111827", font=dict(color="#f8fafc")),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text=""),
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID)
    return fig


def build_up_distribution(goals_df: pd.DataFrame) -> go.Figure:
    counts = goals_df["build_up_type"].astype(str).value_counts().reindex(BUILD_UP_ORDER, fill_value=0).reset_index()
    counts.columns = ["build_up_type", "goals"]
    fig = px.bar(
        counts,
        x="build_up_type",
        y="goals",
        color="build_up_type",
        color_discrete_map=BUILD_UP_COLORS,
        title="Build-up Type Distribution",
        text="goals",
    )
    fig.update_traces(textposition="outside", customdata=counts[["build_up_type"]])
    fig.update_layout(clickmode="event+select", xaxis_title="", yaxis_title="Goals", showlegend=False)
    return style_figure(fig, 350)


def team_build_up_profile(goals_df: pd.DataFrame) -> go.Figure:
    ranking = team_ranking(goals_df).head(12).sort_values("avg_passes")
    fig = px.bar(
        ranking,
        x="avg_passes",
        y="team",
        orientation="h",
        color_discrete_sequence=["#38bdf8"],
        title="Team Build-up Profile",
        hover_data={"team": True, "goals": True, "avg_passes": ":.1f", "avg_duration": ":.1f"},
    )
    fig.update_traces(marker_opacity=0.9)
    fig.update_layout(xaxis_title="Average completed passes before goal", yaxis_title="")
    return style_figure(fig, 350)


def passes_duration_scatter(goals_df: pd.DataFrame, selected_build_up_id: str | None = None) -> go.Figure:
    fig = px.scatter(
        goals_df,
        x="passes_before_goal",
        y="attack_duration_seconds",
        color="build_up_type",
        color_discrete_map=BUILD_UP_COLORS,
        title="Passes vs Attack Duration",
        hover_name="scorer",
        custom_data=["build_up_id", "team", "match_name", "minute", "build_up_type"],
    )
    fig.update_traces(
        marker=dict(size=9, opacity=0.82, line=dict(width=0.8, color="rgba(255,255,255,0.45)")),
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Team: %{customdata[1]}<br>"
            "Match: %{customdata[2]}<br>"
            "Minute: %{customdata[3]}'<br>"
            "Build-up: %{customdata[4]}<br>"
            "Passes: %{x}<br>"
            "Duration: %{y:.1f}s<extra></extra>"
        ),
    )
    if selected_build_up_id and selected_build_up_id in set(goals_df["build_up_id"].astype(str)):
        selected = goals_df[goals_df["build_up_id"].astype(str).eq(str(selected_build_up_id))]
        fig.add_trace(
            go.Scatter(
                x=selected["passes_before_goal"],
                y=selected["attack_duration_seconds"],
                mode="markers",
                marker=dict(size=20, color="rgba(255,255,255,0)", line=dict(width=2.5, color="#f8fafc")),
                name="Selected goal",
                hoverinfo="skip",
            )
        )
    fig.update_layout(xaxis_title="Completed passes before goal", yaxis_title="Attack duration (seconds)")
    return style_figure(fig, 350)


def finishing_progress_chart(team_df: pd.DataFrame, selected_teams: list[str] | None = None) -> go.Figure:
    plot_df = team_df.copy()
    if selected_teams:
        plot_df["selection"] = plot_df["team"].where(plot_df["team"].isin(selected_teams), "Other teams")
        color_map = {team: "#38bdf8" for team in selected_teams}
        color_map["Other teams"] = "rgba(148,163,184,0.35)"
        color_arg = "selection"
    else:
        plot_df["selection"] = "All teams"
        color_map = {"All teams": "#38bdf8"}
        color_arg = "selection"
    fig = px.scatter(
        plot_df,
        x="finishing_efficiency",
        y="tournament_progress_score",
        size=plot_df["goals"].clip(lower=1),
        color=color_arg,
        color_discrete_map=color_map,
        title="Finishing Efficiency vs Tournament Progress",
        hover_name="team",
        custom_data=["tournament_stage", "shots", "goals", "avg_passes_before_goal", "avg_attack_duration", "selection"],
    )
    fig.update_traces(
        marker=dict(opacity=0.82, line=dict(width=0.8, color="rgba(255,255,255,0.45)")),
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Stage: %{customdata[0]}<br>"
            "Shots: %{customdata[1]:.0f}<br>"
            "Goals: %{customdata[2]:.0f}<br>"
            "Finishing: %{x:.1%}<br>"
            "Definition: goals / shots<br>"
            "Avg passes: %{customdata[3]:.1f}<br>"
            "Avg duration: %{customdata[4]:.1f}s<extra></extra>"
        ),
    )
    fig.update_layout(
        xaxis_title="Goals / shots",
        yaxis_title="Stage reached",
        yaxis=dict(
            tickmode="array",
            tickvals=[1, 2, 3, 4, 5, 6, 7],
            ticktext=["Group", "R16", "QF", "SF", "3rd", "Final", "Winner"],
        ),
        showlegend=bool(selected_teams),
    )
    return style_figure(fig, 350)
