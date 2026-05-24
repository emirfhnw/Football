from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from .utils import PITCH_LENGTH, PITCH_WIDTH, normalize_attack_direction


PITCH_BG = "#0f3d2e"
PITCH_LINE = "rgba(240,253,244,0.62)"
PASS_COLOR = "#b7dcec"
ASSIST_COLOR = "#f59e0b"
SHOT_COLOR = "#ef4444"
NODE_COLOR = "#152235"
ACTIVE_COLOR = "#38bdf8"


def pitch_sequence_figure(
    events_df: pd.DataFrame,
    goals_df: pd.DataFrame,
    build_up_id: str | None,
    current_step: int | None = -1,
) -> go.Figure:
    if not build_up_id and not goals_df.empty:
        build_up_id = str(goals_df.iloc[0]["build_up_id"])

    goal = goals_df[goals_df["build_up_id"].astype(str).eq(str(build_up_id))]
    title = "No goal selected"
    if not goal.empty:
        row = goal.iloc[0]
        title = f"{row['team']} · {row['scorer']} vs {row['opponent']} · {int(row['minute'])}'"

    fig = base_pitch(title)
    sequence = events_df[events_df["build_up_id"].astype(str).eq(str(build_up_id))].copy()
    if sequence.empty:
        fig.add_annotation(
            text="No build-up sequence available for the current selection.",
            x=PITCH_LENGTH / 2,
            y=PITCH_WIDTH / 2,
            xref="x",
            yref="y",
            showarrow=False,
            font=dict(color="#cbd5e1", size=14),
        )
        return fig

    sequence = normalize_attack_direction(sequence, ["x", "y", "end_x", "end_y"])
    sequence["event_order"] = sequence["event_order"].astype(int)
    max_order = int(sequence["event_order"].max())
    active_order, visible_sequence = _visible_sequence(sequence, current_step, max_order)

    show_all = active_order is None
    _add_edges(fig, visible_sequence, active_order, show_all)
    _add_nodes(fig, visible_sequence, active_order, show_all)
    _add_active_label(fig, visible_sequence, active_order)
    _add_ball(fig, visible_sequence, active_order)
    _add_step_annotation(fig, active_order, max_order)
    return fig


def base_pitch(title: str = "") -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        title=dict(text=title, x=0.02, font=dict(size=15, color="#f8fafc")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=PITCH_BG,
        margin=dict(l=4, r=4, t=38, b=4),
        height=380,
        xaxis=dict(range=[0, PITCH_LENGTH], visible=False, fixedrange=True),
        yaxis=dict(range=[0, PITCH_WIDTH], visible=False, fixedrange=True, scaleanchor="x", scaleratio=1),
        showlegend=False,
        hoverlabel=dict(bgcolor="#111827", font=dict(color="#f8fafc")),
        shapes=_pitch_shapes(),
    )
    return fig


def _visible_sequence(sequence: pd.DataFrame, current_step: int | None, max_order: int) -> tuple[int | None, pd.DataFrame]:
    if current_step is None:
        current_step = -1
    current_step = int(current_step)
    if current_step < 0:
        return None, sequence
    active_order = max(1, min(max_order, current_step + 1))
    return active_order, sequence[sequence["event_order"] <= active_order]


def _add_edges(fig: go.Figure, sequence: pd.DataFrame, active_order: int | None, show_all: bool) -> None:
    for _, event in sequence.iterrows():
        order = int(event["event_order"])
        is_shot = event["event_type"] == "Shot"
        is_assist = bool(event.get("is_assist", False))
        is_current = active_order == order
        color = SHOT_COLOR if is_shot else ASSIST_COLOR if is_assist else PASS_COLOR
        if show_all:
            width = 3.5 if is_shot else 2.7 if is_assist else 0.65
            opacity = 1.0 if is_shot else 0.9 if is_assist else 0.16
        else:
            width = 3.2 if is_current or is_shot else 2.6 if is_assist else 1.0
            opacity = 1.0 if is_current or is_shot else 0.92 if is_assist else 0.26
        dash = "dash" if is_shot else "solid"
        fig.add_trace(
            go.Scatter(
                x=[event["x"], event["end_x"]],
                y=[event["y"], event["end_y"]],
                mode="lines",
                line=dict(color=color, width=width, dash=dash),
                opacity=opacity,
                hoverinfo="skip",
            )
        )
        fig.add_annotation(
            x=event["end_x"],
            y=event["end_y"],
            ax=event["x"],
            ay=event["y"],
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            arrowhead=3,
            arrowsize=1.1,
            arrowwidth=width,
            arrowcolor=color,
            opacity=opacity,
        )


def _add_nodes(fig: go.Figure, sequence: pd.DataFrame, active_order: int | None, show_all: bool) -> None:
    min_order = int(sequence["event_order"].min())
    max_order = int(sequence["event_order"].max())
    long_sequence = max_order > 15
    colors = []
    sizes = []
    border_colors = []
    border_widths = []
    labels = []
    for row in sequence.itertuples():
        order = int(row.event_order)
        is_active = active_order == order
        is_start = order == min_order
        is_final = order == max_order
        is_assist = bool(row.is_assist)
        is_shot = row.event_type == "Shot"

        colors.append(ACTIVE_COLOR if is_active else NODE_COLOR)
        if show_all:
            sizes.append(19 if is_final or is_shot else 15 if is_start or is_assist else 8)
            border_colors.append(SHOT_COLOR if is_shot else ASSIST_COLOR if is_assist else ACTIVE_COLOR if is_final else "#dbeafe" if is_start else "rgba(219,234,254,0.55)")
            border_widths.append(2.8 if is_final or is_shot else 2.0 if is_start or is_assist else 0.9)
            labels.append(str(order) if (is_start or is_assist or is_shot or is_final or not long_sequence and order % 2 == 1) else "")
        else:
            sizes.append(27 if is_active else 17 if is_assist or is_shot else 13)
            border_colors.append(ACTIVE_COLOR if is_active else ASSIST_COLOR if is_assist else SHOT_COLOR if is_shot else "#dbeafe")
            border_widths.append(4.2 if is_active else 1.4)
            labels.append(str(order))

    fig.add_trace(
        go.Scatter(
            x=sequence["x"],
            y=sequence["y"],
            mode="markers+text",
            marker=dict(size=sizes, color=colors, line=dict(width=border_widths, color=border_colors)),
            text=labels,
            textfont=dict(size=8 if show_all else 10, color="rgba(248,250,252,0.72)" if show_all else "#f8fafc", family="Inter, sans-serif"),
            textposition="middle center",
            customdata=sequence[["event_type", "player", "recipient", "timestamp_label", "pass_outcome"]],
            hovertemplate=(
                "<b>%{customdata[1]}</b><br>"
                "Event: %{customdata[0]}<br>"
                "Recipient: %{customdata[2]}<br>"
                "Time: %{customdata[3]}<br>"
                "Outcome: %{customdata[4]}<extra></extra>"
            ),
        )
    )


def _add_active_label(fig: go.Figure, sequence: pd.DataFrame, active_order: int | None) -> None:
    if sequence.empty:
        return
    if active_order is not None:
        active = sequence[sequence["event_order"].eq(active_order)].iloc[-1]
        player = str(active["player"])
        label = player if len(player) <= 18 else player[:17] + "..."
        fig.add_annotation(
            text=label,
            x=active["x"],
            y=min(PITCH_WIDTH - 2, active["y"] + 5),
            xref="x",
            yref="y",
            showarrow=False,
            font=dict(color="#f8fafc", size=11),
            bgcolor="rgba(15,23,42,0.72)",
            bordercolor="rgba(56,189,248,0.55)",
            borderpad=3,
        )

    goals = sequence[sequence["is_goal"].astype(bool)]
    if not goals.empty:
        goal = goals.iloc[-1]
        fig.add_trace(
            go.Scatter(
                x=[goal["end_x"]],
                y=[goal["end_y"]],
                mode="markers",
                marker=dict(size=22, color=ASSIST_COLOR, symbol="star", line=dict(width=2.0, color="#fff7ed")),
                hovertemplate="Goal<extra></extra>",
            )
        )
        fig.add_annotation(
            text="Goal",
            x=goal["end_x"],
            y=min(PITCH_WIDTH - 2, goal["end_y"] + 4),
            xref="x",
            yref="y",
            showarrow=False,
            font=dict(color="#fff7ed", size=11),
            bgcolor="rgba(15,23,42,0.72)",
            bordercolor="rgba(245,158,11,0.75)",
            borderpad=3,
        )


def _add_ball(fig: go.Figure, sequence: pd.DataFrame, active_order: int | None) -> None:
    if sequence.empty:
        return
    active = sequence.iloc[-1] if active_order is None else sequence[sequence["event_order"].eq(active_order)].iloc[-1]
    fig.add_trace(
        go.Scatter(
            x=[active["end_x"]],
            y=[active["end_y"]],
            mode="markers",
            marker=dict(size=10, color="#ffffff", line=dict(width=2, color="#111827")),
            hovertemplate="Ball position<extra></extra>",
        )
    )


def _add_step_annotation(fig: go.Figure, active_order: int | None, max_order: int) -> None:
    text = f"Showing all {max_order} events" if active_order is None else f"Step {active_order} / {max_order}"
    fig.add_annotation(
        text=text,
        x=1.5,
        y=82.5,
        xref="x",
        yref="y",
        showarrow=False,
        font=dict(color="#cbd5e1", size=12),
        align="left",
    )


def _pitch_shapes() -> list[dict]:
    return [
        _rect(0, 0, PITCH_LENGTH, PITCH_WIDTH),
        _line(PITCH_LENGTH / 2, 0, PITCH_LENGTH / 2, PITCH_WIDTH),
        _circle(PITCH_LENGTH / 2, PITCH_WIDTH / 2, 10),
        _rect(0, 18, 18, 62),
        _rect(PITCH_LENGTH - 18, 18, PITCH_LENGTH, 62),
        _rect(0, 30, 6, 50),
        _rect(PITCH_LENGTH - 6, 30, PITCH_LENGTH, 50),
        _circle(12, 40, 0.75),
        _circle(PITCH_LENGTH - 12, 40, 0.75),
        _line(PITCH_LENGTH, 36, PITCH_LENGTH, 44, width=4, color=ASSIST_COLOR),
    ]


def _rect(x0, y0, x1, y1, color=PITCH_LINE, width=1.2) -> dict:
    return dict(type="rect", x0=x0, y0=y0, x1=x1, y1=y1, line=dict(color=color, width=width))


def _line(x0, y0, x1, y1, width=1.2, color=PITCH_LINE) -> dict:
    return dict(type="line", x0=x0, y0=y0, x1=x1, y1=y1, line=dict(color=color, width=width))


def _circle(x, y, r, color=PITCH_LINE, width=1.1) -> dict:
    return dict(type="circle", x0=x - r, y0=y - r, x1=x + r, y1=y + r, line=dict(color=color, width=width))


def timeline_items(events_df: pd.DataFrame, build_up_id: str | None, current_step: int | None = -1) -> list[dict]:
    if not build_up_id:
        return []
    sequence = events_df[events_df["build_up_id"].astype(str).eq(str(build_up_id))].copy()
    if sequence.empty:
        return []
    max_order = int(sequence["event_order"].max())
    active_order = None if current_step is None or int(current_step) < 0 else max(1, min(max_order, int(current_step) + 1))
    items = []
    for _, event in sequence.iterrows():
        step = int(event["event_order"])
        action = "Shot" if event["event_type"] == "Shot" else "Pass"
        if bool(event.get("is_assist", False)):
            action = "Final pass"
        detail = event["player"]
        if event.get("recipient"):
            detail += f" to {event['recipient']}"
        items.append(
            {
                "step": step,
                "time": event["timestamp_label"],
                "action": action,
                "detail": detail,
                "active": active_order == step,
            }
        )
    return items
