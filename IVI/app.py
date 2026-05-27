from __future__ import annotations

import socket

import plotly.graph_objects as go
from dash import ALL, Dash, Input, Output, State, callback_context, html, no_update
import dash_bootstrap_components as dbc

from src.statsbomb_explorer import (
    competition_options,
    match_options,
    build_match_goal_tables,
    team_tournament_summary,
)
from src.data_loader import load_dashboard_data
from src.figures import build_up_distribution, passes_duration_scatter, team_build_up_profile
from src.layout import build_layout, goal_options, kpi_row
from src.metrics import (
    dashboard_kpis,
    direct_team_ranking,
    patient_team_ranking,
    efficient_team_ranking,
)
from src.pitch_plots import pitch_sequence_figure


# Load only the schema at startup.
# The dashboard starts empty and only loads real data after clicking Load.
_initial_goals_df, _initial_events_df, _team_df = load_dashboard_data()
goals_df = _initial_goals_df.iloc[0:0].copy()
events_df = _initial_events_df.iloc[0:0].copy()
tournament_goals_df = _initial_goals_df.iloc[0:0].copy()

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Coach Attack Explorer",
)
server = app.server
app.layout = build_layout(goals_df, competition_options())


def empty_figure(message: str = "Load a tournament to start."):
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


def selected_goals(selected_team=None, selected_build_type=None):
    if goals_df.empty:
        return goals_df.iloc[0:0].copy()

    out = goals_df.copy()

    if selected_team:
        out = out[out["team"].astype(str).eq(str(selected_team))]

    if selected_build_type:
        out = out[out["build_up_type"].astype(str).eq(str(selected_build_type))]

    return out.copy()


def goal_sequence(goal_id: str | None):
    if not goal_id or events_df.empty:
        return events_df.iloc[0:0].copy()
    return events_df[events_df["build_up_id"].astype(str).eq(str(goal_id))].copy()


def goal_row(goal_id: str | None):
    if not goal_id or goals_df.empty:
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


def info_pair(label, value):
    return html.Div([html.Span(label), html.Strong(value)], className="info-pair")


def coach_takeaway(goals):
    if goals.empty:
        return html.Div(
            [
                html.Div("Coach takeaway", className="takeaway-title"),
                html.Div("Load a tournament first.", className="takeaway-text"),
            ]
        )

    kpis = dashboard_kpis(goals)
    n_goals = len(goals)
    avg_passes = float(kpis["avg_passes"])
    avg_duration = float(kpis["avg_duration"])

    if avg_passes <= 3:
        style_note = "Current style: direct attacking."
        training_note = "Training idea: quick forward play, early support runs and fast finishing."
    elif avg_passes <= 6:
        style_note = "Current style: balanced attacking."
        training_note = "Training idea: short combinations, support after the pass and timing of the final pass."
    else:
        style_note = "Current style: patient build-up."
        training_note = "Training idea: keeping possession under pressure and recognising when to speed up."

    return html.Div(
        [
            html.Div("Coach takeaway", className="takeaway-title"),
            html.Div(f"{n_goals} goal build-ups are selected.", className="takeaway-text"),
            html.Div(
                f"{style_note} Average: {avg_passes:.1f} completed passes and {avg_duration:.0f} seconds before the goal.",
                className="takeaway-highlight",
            ),
            html.Div(training_note, className="takeaway-text"),
        ]
    )


def overview_insight(goals):
    if goals.empty:
        return "Load a tournament and optionally choose one team."

    kpis = dashboard_kpis(goals)
    return (
        f"The current selection contains {kpis['total_goals']} goal build-ups. "
        f"Average completed passes before the goal: {kpis['avg_passes']}. "
        f"Average attack duration: {kpis['avg_duration']} seconds. "
        f"Most common build-up type: {kpis['most_common_type']}."
    )


def team_info_card(summary, goals):
    selected_team = summary.get("team", "All teams")

    if selected_team == "All teams":
        return html.Div(
            [
                html.Div("Select one team", className="mini-table-title"),
                html.Div(
                    "After loading a tournament, choose one team above the replay to see matches, results and goal-build-up tendencies.",
                    className="mini-table-subtitle",
                ),
            ],
            className="team-info-card team-info-empty",
        )

    team_goals = goals[goals["team"].astype(str).eq(selected_team)].copy()

    if not team_goals.empty:
        avg_passes = team_goals["passes_before_goal"].mean()
        avg_duration = team_goals["attack_duration_seconds"].mean()
        common_style = team_goals["build_up_type"].mode().iloc[0]
    else:
        avg_passes = 0
        avg_duration = 0
        common_style = "No goals loaded"

    if goals.empty:
        rank_text = "Not ranked"
    else:
        team_rank_df = (
            goals.groupby("team", as_index=False)
            .agg(goals=("build_up_id", "nunique"), avg_passes=("passes_before_goal", "mean"))
            .sort_values("avg_passes", ascending=True)
            .reset_index(drop=True)
        )
        if selected_team in set(team_rank_df["team"]):
            rank = int(team_rank_df.index[team_rank_df["team"].eq(selected_team)][0]) + 1
            rank_text = f"{rank} of {len(team_rank_df)} teams by directness"
        else:
            rank_text = "Not ranked"

    rows = []
    for match in summary.get("matches", []):
        rows.append(
            html.Tr(
                [
                    html.Td(str(match.get("date", ""))),
                    html.Td(str(match.get("stage", ""))),
                    html.Td(str(match.get("match", ""))),
                    html.Td(str(match.get("result", ""))),
                ]
            )
        )

    return html.Div(
        [
            html.Div(
                [
                    html.Div("Selected team", className="mini-table-title"),
                    html.Div(summary.get("summary", ""), className="mini-table-subtitle"),
                    html.Div(
                        [
                            info_pair("Team", selected_team),
                            info_pair("Goals analysed", len(team_goals)),
                            info_pair("Formation", summary.get("formation", "Not available")),
                            info_pair("Directness rank", rank_text),
                            info_pair("Avg passes before goal", f"{avg_passes:.1f}"),
                            info_pair("Avg attack duration", f"{avg_duration:.0f}s"),
                            info_pair("Most common goal style", common_style),
                        ],
                        className="step-meta",
                    ),
                ],
                className="team-info-summary",
            ),
            html.Div(
                [
                    html.Div("Matches in tournament", className="mini-table-title"),
                    html.Table(
                        [
                            html.Thead(
                                html.Tr(
                                    [
                                        html.Th("Date"),
                                        html.Th("Stage"),
                                        html.Th("Match"),
                                        html.Th("Result"),
                                    ]
                                )
                            ),
                            html.Tbody(rows),
                        ],
                        className="team-table compact-match-table",
                    ),
                ],
                className="team-info-matches",
            ),
        ],
        className="team-info-card",
    )


def step_info(goal_id: str | None, step: int):
    row = goal_row(goal_id)
    event = current_event(goal_id, step)
    total = total_steps(goal_id)

    if row is None or event is None or total == 0:
        return html.Div("Load a tournament and select a goal to replay.", className="empty-state")

    is_full = step < 0
    step_label = f"Full sequence ({total} events)" if is_full else f"Step {min(step + 1, total)} of {total}"

    event_type = str(event.get("event_type", "Action"))
    recipient = str(event.get("recipient") or "").strip()
    player = str(event.get("player") or "Unknown player")
    timestamp = str(event.get("timestamp_label") or "")

    if event_type == "Shot":
        action_line = "Shot / finish"
    elif bool(event.get("is_assist", False)):
        action_line = "Final pass" if not recipient else f"Final pass to {recipient}"
    elif event_type == "Pass":
        action_line = "Pass" if not recipient else f"Pass to {recipient}"
    elif event_type == "Carry":
        action_line = "Carry"
    else:
        action_line = event_type

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
                    info_pair("Completed passes", int(row["passes_before_goal"])),
                    info_pair("Duration", f"{float(row['attack_duration_seconds']):.0f}s"),
                    info_pair("Build-up style", row["build_up_type"]),
                ],
                className="step-meta",
            ),
        ]
    )


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

    return html.Table([header, html.Tbody(rows)], className="team-table")


def top_team_table(goals):
    if goals.empty:
        return html.Div("No team profile available yet. Load a tournament first.", className="empty-state")

    direct = direct_team_ranking(goals).head(5)
    patient = patient_team_ranking(goals).head(5)
    efficient = efficient_team_ranking(goals).head(5)

    return html.Div(
        [
            html.Div(
                [
                    html.Div("Most direct teams", className="mini-table-title"),
                    html.Div("Lowest average completed passes before goals.", className="mini-table-subtitle"),
                    ranking_table(direct, [("Team", "team"), ("Goals", "goals"), ("Avg passes", "avg_passes"), ("Avg duration", "avg_duration")]),
                ],
                className="ranking-block",
            ),
            html.Div(
                [
                    html.Div("Most patient teams", className="mini-table-title"),
                    html.Div("Highest average completed passes before goals.", className="mini-table-subtitle"),
                    ranking_table(patient, [("Team", "team"), ("Goals", "goals"), ("Avg passes", "avg_passes"), ("Avg duration", "avg_duration")]),
                ],
                className="ranking-block",
            ),
            html.Div(
                [
                    html.Div("Most efficient finishers", className="mini-table-title"),
                    html.Div("Largest positive difference between goals and xG.", className="mini-table-subtitle"),
                    ranking_table(efficient, [("Team", "team"), ("Goals", "goals"), ("Total xG", "total_xg"), ("G-xG", "goals_minus_xg")]),
                ],
                className="ranking-block",
            ),
        ],
        className="ranking-grid",
    )


@app.callback(
    Output("match-filter", "options"),
    Output("match-filter", "value"),
    Input("competition-season-filter", "value"),
)
def update_match_dropdown(competition_season_value):
    options_list = match_options(competition_season_value)
    value = options_list[0]["value"] if options_list else None
    return options_list, value


@app.callback(
    Output("selected-build-up", "data", allow_duplicate=True),
    Output("step-store", "data", allow_duplicate=True),
    Output("team-filter", "options", allow_duplicate=True),
    Output("team-filter", "value", allow_duplicate=True),
    Output("type-filter", "options", allow_duplicate=True),
    Output("type-filter", "value", allow_duplicate=True),
    Output("goal-dropdown", "options", allow_duplicate=True),
    Output("goal-dropdown", "value", allow_duplicate=True),
    Output("data-load-feedback", "children"),
    Output("filter-feedback", "children", allow_duplicate=True),
    Input("load-match-button", "n_clicks"),
    State("match-filter", "value"),
    prevent_initial_call=True,
)
def load_selected_match(_clicks, match_value):
    global goals_df, events_df, _team_df, tournament_goals_df

    if not match_value:
        return (
            None, 0, [], None, [], None, [], None,
            "Please select a tournament first.",
            "Load a tournament first.",
        )

    try:
        new_goals, new_events, new_team = build_match_goal_tables(match_value, "ALL")

        parts = str(match_value).split("|")
        tournament_match_value = f"{parts[0]}|{parts[1]}|ALL"
        tournament_goals, _unused_events, _unused_team = build_match_goal_tables(tournament_match_value, "ALL")
    except Exception as exc:
        return (
            None, 0, [], None, [], None, [], None,
            f"Could not load selection: {exc}",
            "Loading failed.",
        )

    goals_df = new_goals.copy()
    events_df = new_events.copy()
    _team_df = new_team.copy()
    tournament_goals_df = tournament_goals.copy()

    if goals_df.empty:
        return (
            None, 0, [], None, [], None, [], None,
            "Selection loaded, but no non-penalty goal build-ups were found.",
            "No goals available.",
        )

    team_options_local = [
        {"label": team, "value": team}
        for team in sorted(goals_df["team"].dropna().astype(str).unique())
    ]

    type_options_local = [
        {"label": item, "value": item}
        for item in sorted(goals_df["build_up_type"].dropna().astype(str).unique())
    ]

    goal_dropdown_options = goal_options(goals_df)
    first_goal = goal_dropdown_options[0]["value"] if goal_dropdown_options else None

    return (
        first_goal,
        0,
        team_options_local,
        None,
        type_options_local,
        None,
        goal_dropdown_options,
        first_goal,
        f"Loaded selection: {len(goals_df)} goal build-ups available. Now choose one team for replay and team-specific plots.",
        f"{len(goals_df)} goals in selection",
    )


@app.callback(
    Output("team-tournament-info", "children"),
    Input("team-filter", "value"),
    Input("match-filter", "value"),
    Input("selected-build-up", "data"),
)
def render_team_tournament_info(selected_team, match_value, selected_goal):
    if goals_df.empty:
        return html.Div(
            "Load a tournament first. Then select one team to see tournament information.",
            className="empty-state",
        )

    if not selected_team:
        return team_info_card(
            {
                "team": "All teams",
                "matches": [],
                "formation": "Select a team",
                "summary": "Select one team in the replay filter to see formation, matches and results.",
            },
            tournament_goals_df,
        )

    summary = team_tournament_summary(match_value, selected_team)
    return team_info_card(summary, tournament_goals_df)


@app.callback(
    Output("overview-kpis", "children"),
    Output("overview-build-up-chart", "figure"),
    Output("overview-scatter-chart", "figure"),
    Output("coach-takeaway", "children"),
    Output("overview-insight", "children"),
    Input("selected-build-up", "data"),
    Input("team-filter", "value"),
    Input("type-filter", "value"),
)
def render_overview(selected_goal, selected_team, selected_build_type):
    if goals_df.empty:
        empty_goals = goals_df.iloc[0:0]
        return (
            html.Div("Load a tournament to see the overview.", className="empty-state"),
            empty_figure("Choose a tournament and click Load."),
            empty_figure("After loading, this chart shows whether attacks are direct or patient."),
            coach_takeaway(empty_goals),
            "Start by loading a tournament.",
        )

    plot_goals = selected_goals(selected_team, selected_build_type)

    if plot_goals.empty:
        return (
            html.Div("No goals match the selected filters.", className="empty-state"),
            empty_figure("No goals for this team and build-up type."),
            empty_figure("No goals for this team and build-up type."),
            coach_takeaway(plot_goals),
            "No goals match the selected filters.",
        )

    return (
        kpi_row(dashboard_kpis(plot_goals)),
        build_up_distribution(plot_goals),
        passes_duration_scatter(plot_goals, selected_goal),
        coach_takeaway(plot_goals),
        overview_insight(plot_goals),
    )


@app.callback(
    Output("team-filter", "value", allow_duplicate=True),
    Output("type-filter", "value", allow_duplicate=True),
    Input("reset-button", "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(_clicks):
    return None, None


@app.callback(
    Output("goal-dropdown", "options", allow_duplicate=True),
    Output("goal-dropdown", "value", allow_duplicate=True),
    Output("filter-feedback", "children", allow_duplicate=True),
    Input("team-filter", "value"),
    Input("type-filter", "value"),
    State("selected-build-up", "data"),
    prevent_initial_call=True,
)
def update_goal_options(selected_team, selected_build_type, selected_goal):
    if goals_df.empty:
        return [], None, "Load a tournament first."

    goals = selected_goals(selected_team, selected_build_type)

    if goals.empty:
        return [], None, "No goals match this team and build-up type. Reset the build-up type or choose another team."

    options_list = goal_options(goals)
    valid_values = {option["value"] for option in options_list}
    value = selected_goal if selected_goal in valid_values else options_list[0]["value"]

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
    Input("selected-build-up", "data"),
    Input("team-filter", "value"),
)
def render_team_comparison(selected_goal, selected_team):
    if tournament_goals_df.empty:
        return (
            empty_figure("Load a tournament first to compare attacking styles."),
            html.Div("No team profile available yet. Load a tournament first.", className="empty-state"),
        )

    return (
        team_build_up_profile(tournament_goals_df, selected_team),
        top_team_table(tournament_goals_df),
    )


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
