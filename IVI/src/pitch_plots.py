import pandas as pd
import plotly.graph_objects as go


PITCH_X = 120
PITCH_Y = 80


def _get(row, names, default=None):
    for name in names:
        if name in row and pd.notna(row[name]):
            return row[name]
    return default


def _add_pitch_base(fig):

    fig.add_annotation(x=20, y=5, text="Build-up", showarrow=False, font=dict(size=12, color="rgba(255,255,255,0.88)"))
    fig.add_annotation(x=60, y=5, text="Progression", showarrow=False, font=dict(size=12, color="rgba(255,255,255,0.88)"))
    fig.add_annotation(x=100, y=5, text="Final third", showarrow=False, font=dict(size=12, color="rgba(255,255,255,0.88)"))

    line = "rgba(226,232,240,0.75)"
    soft = "rgba(226,232,240,0.55)"

    shapes = [
        dict(type="rect", x0=0, y0=0, x1=120, y1=80, line=dict(width=0), fillcolor="#0b6b45", layer="below"),

        dict(type="rect", x0=0, y0=0, x1=40, y1=80, line=dict(width=0), fillcolor="rgba(255,255,255,0.035)", layer="below"),
        dict(type="rect", x0=40, y0=0, x1=80, y1=80, line=dict(width=0), fillcolor="rgba(255,255,255,0.000)", layer="below"),
        dict(type="rect", x0=80, y0=0, x1=120, y1=80, line=dict(width=0), fillcolor="rgba(255,255,255,0.055)", layer="below"),

        dict(type="rect", x0=0, y0=0, x1=120, y1=80, line=dict(color=line, width=2), fillcolor="rgba(0,0,0,0)"),
        dict(type="line", x0=60, y0=0, x1=60, y1=80, line=dict(color="rgba(255,255,255,0.90)", width=2)),

        dict(type="line", x0=40, y0=0, x1=40, y1=80, line=dict(color="rgba(255,255,255,0.40)", width=1.5, dash="dash")),
        dict(type="line", x0=80, y0=0, x1=80, y1=80, line=dict(color="rgba(255,255,255,0.40)", width=1.5, dash="dash")),

        dict(type="rect", x0=0, y0=18, x1=18, y1=62, line=dict(color=soft, width=1), fillcolor="rgba(0,0,0,0)"),
        dict(type="rect", x0=102, y0=18, x1=120, y1=62, line=dict(color=soft, width=1), fillcolor="rgba(0,0,0,0)"),

        dict(type="rect", x0=0, y0=30, x1=6, y1=50, line=dict(color=soft, width=1), fillcolor="rgba(0,0,0,0)"),
        dict(type="rect", x0=114, y0=30, x1=120, y1=50, line=dict(color=soft, width=1), fillcolor="rgba(0,0,0,0)"),

        dict(type="line", x0=0, y0=36, x1=0, y1=44, line=dict(color="#f59e0b", width=5)),
        dict(type="line", x0=120, y0=36, x1=120, y1=44, line=dict(color="#f59e0b", width=5)),
    ]

    fig.update_layout(shapes=shapes)

    fig.add_shape(
        type="circle",
        x0=50,
        y0=30,
        x1=70,
        y1=50,
        line=dict(color=soft, width=1),
    )

    fig.add_trace(
        go.Scatter(
            x=[12, 108],
            y=[40, 40],
            mode="markers",
            marker=dict(size=5, color=soft),
            hoverinfo="skip",
            showlegend=False,
        )
    )


def _finalize_pitch(fig, height=560):
    fig.update_xaxes(range=[0, 120], visible=False, fixedrange=True, constrain="domain")
    fig.update_yaxes(range=[80, 0], visible=False, fixedrange=True, scaleanchor="x", scaleratio=1)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#064e3b",
        margin=dict(l=0, r=0, t=0, b=0),
        height=height,
        autosize=True,
        showlegend=False,
        hovermode=False,
    )


def _empty_pitch(message="No build-up sequence available for the current selection."):
    fig = go.Figure()
    _add_pitch_base(fig)
    fig.add_annotation(
        x=60,
        y=40,
        text=message,
        showarrow=False,
        font=dict(size=16, color="white"),
    )
    _finalize_pitch(fig)
    return fig


def pitch_sequence_figure(events_df, goals_df, goal_id, step):
    if events_df is None or events_df.empty or not goal_id:
        return _empty_pitch()

    sequence = events_df[events_df["build_up_id"].astype(str).eq(str(goal_id))].copy()

    if sequence.empty:
        return _empty_pitch()

    if "event_order" in sequence.columns:
        sequence = sequence.sort_values("event_order")

    if step is None:
        step = 0

    if step < 0:
        visible = sequence.copy()
    else:
        visible = sequence.iloc[: int(step) + 1].copy()

    if visible.empty:
        return _empty_pitch()

    fig = go.Figure()
    _add_pitch_base(fig)

    xs = []
    ys = []
    labels = []

    for idx, row in visible.iterrows():
        x = _get(row, ["x", "start_x", "location_x"])
        y = _get(row, ["y", "start_y", "location_y"])
        end_x = _get(row, ["end_x", "pass_end_x", "carry_end_x", "shot_end_x"])
        end_y = _get(row, ["end_y", "pass_end_y", "carry_end_y", "shot_end_y"])

        if x is None or y is None:
            continue

        event_order = int(_get(row, ["event_order"], len(xs) + 1))
        event_type = str(_get(row, ["event_type", "type"], "Action"))
        player = str(_get(row, ["player", "player_name"], ""))

        xs.append(float(x))
        ys.append(float(y))
        labels.append(str(event_order))

        if end_x is not None and end_y is not None:
            color = "rgba(148,163,184,0.65)"
            width = 2

            if "shot" in event_type.lower():
                color = "rgba(250,204,21,0.98)"
                width = 4
            elif "pass" in event_type.lower():
                color = "rgba(56,189,248,0.75)"
                width = 2
            elif "carry" in event_type.lower():
                color = "rgba(34,197,94,0.75)"
                width = 2

            fig.add_annotation(
                x=float(end_x),
                y=float(end_y),
                ax=float(x),
                ay=float(y),
                xref="x",
                yref="y",
                axref="x",
                ayref="y",
                showarrow=True,
                arrowhead=3,
                arrowsize=1.2,
                arrowwidth=width,
                arrowcolor=color,
                opacity=0.95,
            )

        is_current = idx == visible.index[-1]
        if is_current and player:
            fig.add_annotation(
                x=float(x),
                y=float(y) - 4,
                text=player[:24],
                showarrow=False,
                bgcolor="rgba(15,23,42,0.88)",
                bordercolor="rgba(56,189,248,0.8)",
                borderwidth=1,
                font=dict(size=11, color="white"),
            )

    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="markers+text",
            text=labels,
            textposition="middle center",
            marker=dict(
                size=17,
                color="rgba(15,23,42,0.95)",
                line=dict(color="rgba(226,232,240,0.9)", width=2),
            ),
            textfont=dict(color="white", size=10),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    current = visible.iloc[-1]
    cx = _get(current, ["x", "start_x", "location_x"])
    cy = _get(current, ["y", "start_y", "location_y"])

    if cx is not None and cy is not None:
        fig.add_trace(
            go.Scatter(
                x=[float(cx)],
                y=[float(cy)],
                mode="markers",
                marker=dict(
                    size=32,
                    color="rgba(14,165,233,0.85)",
                    line=dict(color="white", width=2),
                ),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    final = sequence.iloc[-1]
    gx = _get(final, ["end_x", "shot_end_x", "x"], 120)
    gy = _get(final, ["end_y", "shot_end_y", "y"], 40)

    if gx is not None and gy is not None:
        fig.add_trace(
            go.Scatter(
                x=[float(gx)],
                y=[float(gy)],
                mode="markers+text",
                text=["Goal"],
                textposition="top center",
                marker=dict(
                    size=26,
                    symbol="star",
                    color="#f59e0b",
                    line=dict(color="white", width=1),
                ),
                textfont=dict(color="white", size=11),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    _finalize_pitch(fig)
    return fig