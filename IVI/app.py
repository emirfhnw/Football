from __future__ import annotations

import socket

import plotly.graph_objects as go
from src.statsbomb_explorer import (
    competition_options,
    match_options,
    team_options,
    build_match_goal_tables,
    parse_match_value,
)
from dash import ALL, Dash, Input, Output, State, callback_context, html, no_update
import dash_bootstrap_components as dbc

from src.data_loader import load_dashboard_data
from src.figures import build_up_distribution, passes_duration_scatter, team_build_up_profile
from src.layout import build_layout, goal_options, kpi_row, options
from src.metrics import (
    dashboard_kpis,
    filter_goals,
    direct_team_ranking,
    patient_team_ranking,
    efficient_team_ranking,
)
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
app.layout = build_layout(goals_df, competition_options())


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
        return "No goal build-ups are available for the current selection."

    kpis = dashboard_kpis(goals)
    avg_passes = kpis["avg_passes"]
    avg_duration = kpis["avg_duration"]
    most_common = str(kpis["most_common_type"])

    if avg_passes <= 3:
        style_text = "The selected goals mainly come from direct attacks with only a few completed passes."
    elif avg_passes <= 6:
        style_text = "The selected goals mostly come from medium-length attacks, where teams combine a few passes before finishing."
    else:
        style_text = "The selected goals tend to come from longer build-up sequences with more patient possession."

    return (
        f"{style_text} On average, the goals include {avg_passes} completed passes "
        f"and last about {avg_duration} seconds. The most common build-up type is '{most_common}'. "
        "For a coach, this is useful as a starting point for discussing whether a team attacks directly, patiently or somewhere in between."
    )

def empty_figure(message: str = "Load a selection to start the analysis."):
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=16, color="#94a3b8"),
        align="center",
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.6)",
        margin=dict(l=20, r=20, t=20, b=20),
        height=350,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig


def welcome_cards():
    return html.Div(
        [
            html.Div(
                [
                    html.Div("1", className="welcome-step-number"),
                    html.Div("Choose competition", className="welcome-step-title"),
                    html.Div("Start with a competition and season from StatsBomb data.", className="welcome-step-text"),
                ],
                className="welcome-step",
            ),
            html.Div(
                [
                    html.Div("2", className="welcome-step-number"),
                    html.Div("Select match and team", className="welcome-step-title"),
                    html.Div("Load one match or focus on one team in that match.", className="welcome-step-text"),
                ],
                className="welcome-step",
            ),
            html.Div(
                [
                    html.Div("3", className="welcome-step-number"),
                    html.Div("Analyse the attack", className="welcome-step-title"),
                    html.Div("Use charts, team profile and replay to inspect goal build-ups.", className="welcome-step-text"),
                ],
                className="welcome-step",
            ),
        ],
        className="welcome-steps",
    )

@app.callback(
    Output("match-filter", "options"),
    Output("match-filter", "value"),
    Input("competition-season-filter", "value"),
)
def update_match_dropdown(competition_season_value):
    options = match_options(competition_season_value)
    value = options[0]["value"] if options else None
    return options, value


@app.callback(
    Output("team-scope-filter", "options"),
    Output("team-scope-filter", "value"),
    Input("match-filter", "value"),
)
def update_team_scope(match_value):
    options = team_options(match_value) if match_value else [{"label": "All teams", "value": "ALL"}]
    return options, "ALL"


@app.callback(
    Output("selected-build-up", "data", allow_duplicate=True),
    Output("step-store", "data", allow_duplicate=True),
    Output("team-filter", "value", allow_duplicate=True),
    Output("type-filter", "value", allow_duplicate=True),
    Output("data-load-feedback", "children"),
    Input("load-match-button", "n_clicks"),
    State("match-filter", "value"),
    State("team-scope-filter", "value"),
    prevent_initial_call=True,
)
def load_selected_match(_clicks, match_value, team_scope):
    global goals_df, events_df, _team_df

    if not match_value:
        return no_update, no_update, no_update, no_update, "Please select a match first."

    try:
        new_goals, new_events, new_team = build_match_goal_tables(match_value, team_scope or "ALL")
    except Exception as exc:
        return no_update, no_update, no_update, no_update, f"Could not load selection: {exc}"

    goals_df = new_goals
    events_df = new_events
    _team_df = new_team

    if goals_df.empty:
        return None, 0, [], [], "Selection loaded, but no goals were found for the selected team."

    first_goal = str(goals_df.iloc[0]["build_up_id"])

    try:
        _competition_id, _season_id, match_id = parse_match_value(match_value)
        feedback = f"Loaded selection: match {match_id}, {len(goals_df)} goal build-ups available."
    except Exception:
        feedback = f"Loaded selection: {len(goals_df)} goal build-ups available."

    return first_goal, 0, [], [], feedback

@app.callback(
    Output("team-filter", "options"),
    Output("type-filter", "options"),
    Input("selected-build-up", "data"),
)
def refresh_replay_filter_options(selected_goal):
    if not selected_goal or goals_df.empty:
        return [], []

    team_options_local = options(goals_df["team"])
    type_options_local = [
        {"label": item, "value": item}
        for item in sorted(goals_df["build_up_type"].astype(str).dropna().unique())
    ]

    return team_options_local, type_options_local

def step_info(goal_id: str | None, step: int):
    row = goal_row(goal_id)
    event = current_event(goal_id, step)
    total = total_steps(goal_id)

    if row is None or event is None or total == 0:
        return html.Div("Load a match and select a goal to replay.", className="empty-state")

    is_full = step < 0
    step_label = f"Full sequence ({total} events)" if is_full else f"Step {min(step + 1, total)} of {total}"

    event_type = str(event.get("event_type", "Action"))
    recipient = str(event.get("recipient") or "").strip()
    player = str(event.get("player") or "Unknown player")
    timestamp = str(event.get("timestamp_label") or "")

    if event_type == "Shot":
        action_line = "Shot / finish"
        coach_note = "Training cue: look at how the attack creates the final shooting situation."
    elif bool(event.get("is_assist", False)):
        action_line = "Final pass" if not recipient else f"Final pass to {recipient}"
        coach_note = "Training cue: focus on the last pass before the finish and the timing of the receiver."
    elif event_type == "Pass":
        action_line = "Pass" if not recipient else f"Pass to {recipient}"
        coach_note = "Training cue: check whether the pass moves the attack forward or keeps possession."
    else:
        action_line = event_type
        coach_note = "Training cue: use this event to discuss the next attacking decision."

    passes = int(row["passes_before_goal"])
    duration = float(row["attack_duration_seconds"])

    if passes <= 2:
        style_note = "Very direct goal sequence."
    elif passes <= 6:
        style_note = "Medium-length build-up before the goal."
    else:
        style_note = "Patient build-up with many completed passes."

    return html.Div(
        [
            html.Div(step_label, className="step-count"),
            html.Div(player, className="step-player"),
            html.Div(action_line, className="step-action"),
            html.Div(timestamp, className="step-time"),

            html.Div(
                [
                    info_pair("Team", row["team"]),
                    info_pair("Scorer", row["scorer"]),
                    info_pair("Completed passes", passes),
                    info_pair("Duration", f"{duration:.0f}s"),
                    info_pair("Build-up style", row["build_up_type"]),
                ],
                className="step-meta",
            ),

            html.Div(
                [
                    html.Div("Coach interpretation", className="coach-note-title"),
                    html.Div(style_note, className="coach-note-text"),
                    html.Div(coach_note, className="coach-note-text"),
                ],
                className="coach-note-box",
            ),
        ]
    )

def info_pair(label, value):
    return html.Div([html.Span(label), html.Strong(value)], className="info-pair")


def mini_steps(goal_id: str | None, step: int):
    total = total_steps(goal_id)
    if total == 0:
        return html.Div("No events available yet.", className="empty-state")
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


def ranking_table(df, columns):
    if df.empty:
        return html.Div("No team data available.", className="empty-state")

    header = html.Thead(html.Tr([html.Th(label) for label, _ in columns]))

    rows = []
    for _, row in df.iterrows():
        cells = []
        for _, col in columns:
            value = row[col]

            if col in ["avg_passes", "avg_duration", "total_xg", "avg_xg", "goals_minus_xg"]:
                if col == "avg_duration":
                    value = f"{value:.0f}s"
                elif col in ["total_xg", "avg_xg", "goals_minus_xg"]:
                    value = f"{value:.2f}"
                else:
                    value = f"{value:.1f}"
            elif col == "goals":
                value = int(value)

            cells.append(html.Td(value))

        rows.append(html.Tr(cells))

    return html.Table(
        [header, html.Tbody(rows)],
        className="team-table",
    )


def top_team_table(goals):
    direct = direct_team_ranking(goals).head(5)
    patient = patient_team_ranking(goals).head(5)
    efficient = efficient_team_ranking(goals).head(5)

    return html.Div(
        [
            html.Div(
                [
                    html.Div("Most direct teams", className="mini-table-title"),
                    html.Div(
                        "Lowest average number of completed passes before goals.",
                        className="mini-table-subtitle"
                    ),
                    ranking_table(
                        direct,
                        [
                            ("Team", "team"),
                            ("Goals", "goals"),
                            ("Avg passes", "avg_passes"),
                            ("Avg duration", "avg_duration"),
                        ],
                    ),
                ],
                className="ranking-block",
            ),
            html.Div(
                [
                    html.Div("Most patient teams", className="mini-table-title"),
                    html.Div(
                        "Highest average number of completed passes before goals.",
                        className="mini-table-subtitle"
                    ),
                    ranking_table(
                        patient,
                        [
                            ("Team", "team"),
                            ("Goals", "goals"),
                            ("Avg passes", "avg_passes"),
                            ("Avg duration", "avg_duration"),
                        ],
                    ),
                ],
                className="ranking-block",
            ),
            html.Div(
                [
                    html.Div("Most efficient finishers", className="mini-table-title"),
                    html.Div(
                        "Teams with the biggest positive difference between goals and xG.",
                        className="mini-table-subtitle"
                    ),
                    ranking_table(
                        efficient,
                        [
                            ("Team", "team"),
                            ("Goals", "goals"),
                            ("Total xG", "total_xg"),
                            ("G-xG", "goals_minus_xg"),
                        ],
                    ),
                ],
                className="ranking-block",
            ),
        ],
        className="ranking-grid",
    )

@app.callback(
    Output("overview-kpis", "children"),
    Output("overview-build-up-chart", "figure"),
    Output("overview-scatter-chart", "figure"),
    Output("overview-insight", "children"),
    Input("selected-build-up", "data"),
)
def render_overview(selected_goal):
    if not selected_goal or goals_df.empty:
        return (
            welcome_cards(),
            empty_figure("Choose a competition, match and team above. Then click 'Load'."),
            empty_figure("After loading a match, this chart shows passes before goals and attack duration."),
            "Start by loading a selection. The dashboard will then show goal build-ups for the selected match or team.",
        )

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
    if not selected_goal or goals_df.empty:
        return [], None, "Load a selection first."

    goals = filtered_goals(teams, build_types)
    options_list = goal_options(goals)
    valid = {option["value"] for option in options_list}
    value = selected_goal if selected_goal in valid else (options_list[0]["value"] if options_list else None)
    return options_list, value, f"{len(goals)} goals in selection"


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
    Output("is-playing", "data"),
    Output("replay-interval", "disabled"),
    Input("play-button", "n_clicks"),
    Input("pause-button", "n_clicks"),
    Input("step-reset", "n_clicks"),
    Input("step-all", "n_clicks"),
    State("selected-build-up", "data"),
    prevent_initial_call=True,
)
def toggle_play(play_clicks, pause_clicks, reset_clicks, show_all_clicks, goal_id):
    if not goal_id:
        return False, True

    trigger = callback_context.triggered_id

    if trigger == "play-button":
        return True, False
    if trigger in ["pause-button", "step-reset", "step-all"]:
        return False, True

    return no_update, no_update

@app.callback(
    Output("replay-interval", "interval"),
    Input("replay-speed", "value"),
)
def update_replay_speed(speed):
    return int(speed or 800)
@app.callback(
    Output("step-store", "data"),
    Input("step-prev", "n_clicks"),
    Input("step-next", "n_clicks"),
    Input("step-all", "n_clicks"),
    Input("step-reset", "n_clicks"),
    Input("replay-interval", "n_intervals"),
    Input({"type": "step-jump", "index": ALL}, "n_clicks"),
    State("step-store", "data"),
    State("selected-build-up", "data"),
    State("is-playing", "data"),
    prevent_initial_call=True,
)
def update_step(prev, next_, show_all, reset, interval_tick, jumps, current_step, goal_id, is_playing):
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

    if trigger == "replay-interval":
        if not is_playing:
            return current_step
        if current_step < 0:
            return 0
        next_step = current_step + 1
        if next_step > max_step(goal_id):
            return 0
        return next_step

    return current_step

@app.callback(
    Output("pitch-graph", "figure"),
    Output("step-info", "children"),
    Output("mini-steps", "children"),
    Output("step-prev", "disabled"),
    Output("step-next", "disabled"),
    Output("step-all", "disabled"),
    Output("step-reset", "disabled"),
    Output("play-button", "disabled"),
    Output("pause-button", "disabled"),
    Input("selected-build-up", "data"),
    Input("step-store", "data"),
    State("is-playing", "data"),
)
def render_replay(goal_id, step, is_playing):
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
        no_goal or bool(is_playing),
        no_goal or not bool(is_playing),
    )


@app.callback(
    Output("team-chart", "figure"),
    Output("top-teams-table", "children"),
    Input("main-tabs", "value"),
    Input("selected-build-up", "data"),
)
def render_team_comparison(_tab, selected_goal):
    if not selected_goal or goals_df.empty:
        return (
            empty_figure("Load a match first to compare attacking styles."),
            html.Div("No team profile available yet. Load a selection first.", className="empty-state"),
        )

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
