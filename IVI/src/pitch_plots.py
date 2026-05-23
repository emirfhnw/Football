from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from .utils import BUILD_UP_COLORS, PITCH_LENGTH, PITCH_WIDTH, normalize_attack_direction


PITCH_BG = "#16382f"
PITCH_LINE = "rgba(235,255,247,0.62)"


def base_pitch(title: str = "") -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        title=dict(text=title, x=0.02, font=dict(size=15, color="#f8fafc")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=PITCH_BG,
        margin=dict(l=8, r=8, t=42, b=8),
        height=560,
        xaxis=dict(range=[0, PITCH_LENGTH], visible=False, fixedrange=True),
        yaxis=dict(range=[0, PITCH_WIDTH], visible=False, fixedrange=True, scaleanchor="x", scaleratio=1),
        showlegend=False,
        hoverlabel=dict(bgcolor="#0f172a", font=dict(color="#f8fafc")),
        shapes=_pitch_shapes(),
    )
    return fig


def _pitch_shapes() -> list[dict]:
    return [
        _rect(0, 0, PITCH_LENGTH, PITCH_WIDTH),
        _line(PITCH_LENGTH / 2, 0, PITCH_LENGTH / 2, PITCH_WIDTH),
        _circle(PITCH_LENGTH / 2, PITCH_WIDTH / 2, 10),
        _rect(0, 18, 18, 62),
        _rect(PITCH_LENGTH - 18, 18, PITCH_LENGTH, 62),
        _rect(0, 30, 6, 50),
        _rect(PITCH_LENGTH - 6, 30, PITCH_LENGTH, 50),
        _circle(12, 40, 0.8),
        _circle(PITCH_LENGTH - 12, 40, 0.8),
        _line(PITCH_LENGTH, 36, PITCH_LENGTH, 44, width=5, color="#fbbf24"),
    ]


def _rect(x0, y0, x1, y1, color=PITCH_LINE, width=1.3) -> dict:
    return dict(type="rect", x0=x0, y0=y0, x1=x1, y1=y1, line=dict(color=color, width=width))


def _line(x0, y0, x1, y1, width=1.3, color=PITCH_LINE) -> dict:
    return dict(type="line", x0=x0, y0=y0, x1=x1, y1=y1, line=dict(color=color, width=width))


def _circle(x, y, r, color=PITCH_LINE, width=1.2) -> dict:
    return dict(type="circle", x0=x - r, y0=y - r, x1=x + r, y1=y + r, line=dict(color=color, width=width))


def pitch_sequence_figure(
    events_df: pd.DataFrame,
    goals_df: pd.DataFrame,
    build_up_id: str | None,
    active_step: int | None = None,
) -> go.Figure:
    if not build_up_id and not goals_df.empty:
        build_up_id = str(goals_df.iloc[0]["build_up_id"])
    goal = goals_df[goals_df["build_up_id"].astype(str).eq(str(build_up_id))]
    title = "Select a goal build-up"
    if not goal.empty:
        row = goal.iloc[0]
        title = f"{row['team']} goal: {row['scorer']} vs {row['opponent']} ({int(row['minute'])}')"

    fig = base_pitch(title)
    if not build_up_id:
        return fig

    sequence = events_df[events_df["build_up_id"].astype(str).eq(str(build_up_id))].copy()
    if sequence.empty:
        return fig

    sequence = normalize_attack_direction(sequence, ["x", "y", "end_x", "end_y"])
    max_order = int(sequence["event_order"].max())
    if active_step is None or active_step < 1:
        visible_sequence = sequence
    else:
        visible_sequence = sequence[sequence["event_order"] <= active_step]

    passes = visible_sequence[visible_sequence["event_type"].eq("Pass")]
    shots = visible_sequence[visible_sequence["event_type"].eq("Shot")]
    for _, event in passes.iterrows():
        is_last_pass = bool(event.get("is_assist", False))
        color = "#f59e0b" if is_last_pass else "#9bd3ee"
        width = 3.0 if is_last_pass else 1.9
        label = "Last pass / assist" if is_last_pass else "Pass"
        _add_arrow(fig, event["x"], event["y"], event["end_x"], event["end_y"], color, width, label, event)

    for _, event in shots.iterrows():
        _add_arrow(fig, event["x"], event["y"], event["end_x"], event["end_y"], "#f97316", 3.4, "Shot", event)
        fig.add_trace(
            go.Scatter(
                x=[event["end_x"]],
                y=[event["end_y"]],
                mode="markers",
                marker=dict(size=13, color="#f59e0b", symbol="circle", line=dict(width=1.5, color="#fff7ed")),
                name="Goal",
                hovertemplate="Goal<extra></extra>",
            )
        )

    fig.add_trace(
        go.Scatter(
            x=visible_sequence["x"],
            y=visible_sequence["y"],
            mode="markers",
            marker=dict(
                size=10,
                color=[
                    "#f59e0b" if bool(v) else "#f97316" if t == "Shot" else "#d8eef7"
                    for v, t in zip(visible_sequence.get("is_assist", False), visible_sequence["event_type"])
                ],
                line=dict(width=1.0, color="#0f172a"),
            ),
            name="Event start",
            text=visible_sequence["player"],
            customdata=visible_sequence[["event_order", "event_type", "recipient", "timestamp_label", "pass_outcome"]],
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Step %{customdata[0]}: %{customdata[1]}<br>"
                "Recipient: %{customdata[2]}<br>"
                "Time: %{customdata[3]}<br>"
                "Outcome: %{customdata[4]}<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        annotations=list(fig.layout.annotations or [])
        + [
            dict(
                text=f"Step {min(active_step or max_order, max_order)} / {max_order}",
                x=0,
                y=83,
                xref="x",
                yref="y",
                showarrow=False,
                font=dict(color="#cbd5e1", size=12),
                align="left",
            )
        ]
    )
    return fig


def _add_arrow(fig: go.Figure, x0, y0, x1, y1, color: str, width: float, name: str, event: pd.Series) -> None:
    fig.add_annotation(
        x=x1,
        y=y1,
        ax=x0,
        ay=y0,
        xref="x",
        yref="y",
        axref="x",
        ayref="y",
        showarrow=True,
        arrowhead=3,
        arrowsize=1.3,
        arrowwidth=width,
        arrowcolor=color,
        opacity=0.9,
    )
    fig.add_trace(
        go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode="lines",
            line=dict(color=color, width=max(width - 0.6, 1)),
            name=name,
            hoverinfo="skip",
            showlegend=False,
        )
    )


def timeline_items(events_df: pd.DataFrame, build_up_id: str | None, active_step: int | None = None) -> list[dict]:
    if not build_up_id:
        return []
    sequence = events_df[events_df["build_up_id"].astype(str).eq(str(build_up_id))].copy()
    items = []
    for _, event in sequence.iterrows():
        step = int(event["event_order"])
        action = "Goal shot" if event["event_type"] == "Shot" else "Pass"
        detail = event["player"]
        if event.get("recipient"):
            detail += f" to {event['recipient']}"
        items.append(
            {
                "step": step,
                "time": event["timestamp_label"],
                "action": action,
                "detail": detail,
                "active": active_step == step,
            }
        )
    return items
