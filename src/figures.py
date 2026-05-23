from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .metrics import team_ranking
from .utils import BUILD_UP_COLORS, BUILD_UP_ORDER


TEMPLATE = "plotly_dark"
PAPER = "rgba(0,0,0,0)"
PLOT = "#101823"
GRID = "rgba(148,163,184,0.14)"
FONT = "#e5edf7"


def style_figure(fig: go.Figure, height: int = 360) -> go.Figure:
    fig.update_layout(
        template=TEMPLATE,
        paper_bgcolor=PAPER,
        plot_bgcolor=PLOT,
        font=dict(color=FONT, family="Inter, Segoe UI, Arial, sans-serif"),
        margin=dict(l=34, r=18, t=54, b=42),
        height=height,
        hoverlabel=dict(bgcolor="#111827", font=dict(color="#f8fafc")),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
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
    return style_figure(fig, 330)


def team_build_up_profile(goals_df: pd.DataFrame) -> go.Figure:
    ranking = team_ranking(goals_df).head(18).sort_values("avg_passes")
    fig = px.bar(
        ranking,
        x="avg_passes",
        y="team",
        orientation="h",
        color_discrete_sequence=["#38bdf8"],
        title="Team Build-up Profile",
        hover_data={"team": True, "goals": True, "avg_passes": ":.1f", "avg_duration": ":.1f"},
    )
    fig.update_traces(marker_opacity=0.88)
    fig.update_layout(xaxis_title="Average completed passes before goal", yaxis_title="")
    return style_figure(fig, 430)


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
        marker=dict(size=10, opacity=0.82, line=dict(width=0.8, color="rgba(255,255,255,0.45)")),
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
    return style_figure(fig, 430)
