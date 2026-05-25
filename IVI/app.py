from __future__ import annotations

import socket

from dash import ALL, Dash, Input, Output, State, callback_context, html, no_update
import dash_bootstrap_components as dbc

from src.data_loader import load_dashboard_data
from src.figures import build_up_distribution, passes_duration_scatter, team_build_up_profile
from src.layout import build_layout, goal_options, kpi_row
from src.metrics import dashboard_kpis, filter_goals, team_ranking
from src.pitch_plots import pitch_sequence_figure


goals_df, events_df, _team_df = load_dashboard_data()
DEFAULT_BUILD_UP = str(goals_df.iloc[0]["build_up_id"]) if not goals_df.empty else None

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="StatsBomb Attack Explorer",
)
server = app.server
app.layout = build_layout(goals_df)


def filtered_goals(teams=None, build_types=None):
    return filter_goals(goals_df, teams=teams, build_types=build_types)


def goal_sequence(goal_id: str | None):
    if not goal_id:
        return events_df.iloc[0:0].copy()
    return events_df[events_df["build_up_id"].astype(str).eq(str(goal_id))].copy()


def goal_row(goal_id: str | None):
    if not goal_id:
        return None
    match = goals_df[goals_df["build_up_id"].astype(str).eq(str(goal_id))]
    return None if match.empty else match.iloc[0]


def max_step(goal_id: str | None) -> int:
    sequence = goal_sequence(goal_id)
    return max(0, int(sequence["event_order"].max()) - 1) if not sequence.empty else 0


def total_steps(goal_id: str | None) -> int:
    sequence = goal_sequence(goal_id)
    return int(sequence["event_order"].max()) if not sequence.empty else 0


def current_event(goal_id: str | None, step: int):
    sequence = goal_sequence(goal_id)
    if sequence.empty:
        return None
    if step < 0:
        return sequence.iloc[-1]
    order = max(1, min(int(sequence["event_order"].max()), step + 1))
    match = sequence[sequence["event_order"].astype(int).eq(order)]
    return sequence.iloc[-1] if match.empty else match.iloc[0]


def overview_insight(goals):
    if goals.empty:
        return "No goals in the current dataset."
    kpis = dashboard_kpis(goals)
    corr = goals[["passes_before_goal", "attack_duration_seconds"]].corr().iloc[0, 1]
    relation = "Longer sequences also tended to take more time." if corr >= 0.35 else "Pass count and duration were not strongly aligned."
    return f"Most goals came from {str(kpis['most_common_type']).lower()}. {relation}"


def step_info(goal_id: str | None, step: int):
    row = goal_row(goal_id)
    event = current_event(goal_id, step)
    total = total_steps(goal_id)
    if row is None or event is None or total == 0:
        return html.Div("Select a goal to replay.", className="empty-state")

    is_full = step < 0
    step_label = f"Full sequence ({total} events)" if is_full else f"Step {min(step + 1, total)} of {total}"
    action = "Shot" if event["event_type"] == "Shot" else "Pass"
    if bool(event.get("is_assist", False)):
        action = "Final pass"
    recipient = str(event.get("recipient") or "").strip()
    action_line = action if not recipient else f"{action} to {recipient}"

    return html.Div(
        [
            html.Div(step_label, className="step-count"),
            html.Div(str(event["player"]), className="step-player"),
            html.Div(action_line, className="step-action"),
            html.Div(str(event["timestamp_label"]), className="step-time"),
            html.Div(
                [
                    info_pair("Team", row["team"]),
                    info_pair("Scorer", row["scorer"]),
                    info_pair("Passes", int(row["passes_before_goal"])),
                    info_pair("Type", row["build_up_type"]),
                ],
                className="step-meta",
            ),
        ]
    )


def info_pair(label, value):
    return html.Div([html.Span(label), html.Strong(value)], className="info-pair")


def mini_steps(goal_id: str | None, step: int):
    total = total_steps(goal_id)
    if total == 0:
        return html.Div("No events available.", className="empty-state")
    active_order = None if step < 0 else min(step + 1, total)
    buttons = []
    for order in range(1, total + 1):
        label = "Goal" if order == total else str(order)
        classes = ["mini-step"]
        if active_order == order:
            classes.append("active")
        if order == total:
            classes.append("goal-step")
        buttons.append(
            html.Button(
                label,
                id={"type": "step-jump", "index": order},
                n_clicks=0,
                type="button",
                className=" ".join(classes),
            )
        )
    return buttons


def top_team_table(goals):
    ranking = team_ranking(goals).head(5)
    if ranking.empty:
        return html.Div("No team data available.", className="empty-state")
    rows = [
        html.Tr(
            [
                html.Td(row["team"]),
                html.Td(int(row["goals"])),
                html.Td(f"{row['avg_passes']:.1f}"),
                html.Td(f"{row['avg_duration']:.0f}s"),
            ]
        )
        for _, row in ranking.iterrows()
    ]
    return html.Table(
        [
            html.Thead(html.Tr([html.Th("Team"), html.Th("Goals"), html.Th("Avg passes"), html.Th("Avg duration")])),
            html.Tbody(rows),
        ],
        className="team-table",
    )


@app.callback(
    Output("overview-kpis", "children"),
    Output("overview-build-up-chart", "figure"),
    Output("overview-scatter-chart", "figure"),
    Output("overview-insight", "children"),
    Input("selected-build-up", "data"),
)
def render_overview(selected_goal):
    return (
        kpi_row(dashboard_kpis(goals_df)),
        build_up_distribution(goals_df),
        passes_duration_scatter(goals_df, None),
        overview_insight(goals_df),
    )


@app.callback(
    Output("team-filter", "value"),
    Output("type-filter", "value"),
    Input("reset-button", "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(_clicks):
    return [], []


@app.callback(
    Output("goal-dropdown", "options"),
    Output("goal-dropdown", "value"),
    Output("filter-feedback", "children"),
    Input("team-filter", "value"),
    Input("type-filter", "value"),
    Input("selected-build-up", "data"),
)
def update_goal_options(teams, build_types, selected_goal):
    goals = filtered_goals(teams, build_types)
    options = goal_options(goals)
    valid = {option["value"] for option in options}
    value = selected_goal if selected_goal in valid else (options[0]["value"] if options else None)
    return options, value, f"{len(goals)} goals in selection"


@app.callback(
    Output("selected-build-up", "data"),
    Output("step-store", "data", allow_duplicate=True),
    Input("goal-dropdown", "value"),
    Input("overview-scatter-chart", "clickData"),
    prevent_initial_call=True,
)
def select_goal(goal_id, scatter_click):
    trigger = callback_context.triggered_id
    if trigger == "overview-scatter-chart" and scatter_click:
        return str(scatter_click["points"][0]["customdata"][0]), 0
    if trigger == "goal-dropdown":
        return (str(goal_id) if goal_id else None), 0
    return no_update, no_update


@app.callback(
    Output("step-store", "data"),
    Input("step-prev", "n_clicks"),
    Input("step-next", "n_clicks"),
    Input("step-all", "n_clicks"),
    Input("step-reset", "n_clicks"),
    Input({"type": "step-jump", "index": ALL}, "n_clicks"),
    State("step-store", "data"),
    State("selected-build-up", "data"),
    prevent_initial_call=True,
)
def update_step(prev, next_, show_all, reset, jumps, current_step, goal_id):
    if not goal_id:
        return 0
    trigger = callback_context.triggered_id
    current_step = int(current_step if current_step is not None else 0)
    if isinstance(trigger, dict) and trigger.get("type") == "step-jump":
        return max(0, int(trigger["index"]) - 1)
    if trigger == "step-all":
        return -1
    if trigger == "step-reset":
        return 0
    if trigger == "step-prev":
        return max(0, current_step - 1)
    if trigger == "step-next":
        return min(max_step(goal_id), current_step + 1)
    return current_step


@app.callback(
    Output("pitch-graph", "figure"),
    Output("step-info", "children"),
    Output("mini-steps", "children"),
    Output("step-prev", "disabled"),
    Output("step-next", "disabled"),
    Output("step-all", "disabled"),
    Output("step-reset", "disabled"),
    Input("selected-build-up", "data"),
    Input("step-store", "data"),
)
def render_replay(goal_id, step):
    step = int(step if step is not None else 0)
    total = total_steps(goal_id)
    no_goal = not goal_id or total == 0
    showing_all = step < 0
    return (
        pitch_sequence_figure(events_df, goals_df, goal_id, step),
        step_info(goal_id, step),
        mini_steps(goal_id, step),
        no_goal or showing_all or step <= 0,
        no_goal or showing_all or step >= max_step(goal_id),
        no_goal or showing_all,
        no_goal or (step == 0 and not showing_all),
    )


@app.callback(
    Output("team-chart", "figure"),
    Output("top-teams-table", "children"),
    Input("main-tabs", "value"),
)
def render_team_comparison(_tab):
    return team_build_up_profile(goals_df), top_team_table(goals_df)


if __name__ == "__main__":
    def available_port(preferred: int = 8050, fallback: int = 8051) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            return preferred if probe.connect_ex(("127.0.0.1", preferred)) != 0 else fallback

    app.run(
        debug=False,
        dev_tools_ui=False,
        dev_tools_props_check=False,
        port=available_port(),
    )
