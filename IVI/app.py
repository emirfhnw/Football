from __future__ import annotations

import socket

import plotly.graph_objects as go
from dash import ALL, Dash, Input, Output, State, callback_context, html, no_update
import dash_bootstrap_components as dbc

from pathlib import Path
import pandas as pd

from src.data_loader import load_dashboard_data
from src.figures import build_up_distribution, passes_duration_scatter, team_build_up_profile
from src.layout import build_layout, goal_options
from src.pitch_plots import pitch_sequence_figure


BASE_DIR = Path(__file__).resolve().parent
SELECTED_TOURNAMENTS_FILE = BASE_DIR / "data" / "raw" / "selected_tournaments.csv"

_all_goals_df, _all_events_df, _team_df = load_dashboard_data()

goals_df = _all_goals_df.iloc[0:0].copy()
events_df = _all_events_df.iloc[0:0].copy()
team_df = _team_df.copy()
tournament_goals_df = goals_df.copy()


def load_selected_tournaments():
    if SELECTED_TOURNAMENTS_FILE.exists():
        tournaments = pd.read_csv(SELECTED_TOURNAMENTS_FILE)
    else:
        tournaments = pd.DataFrame(
            [
                {
                    "label": "FIFA World Cup - 2022",
                    "competition_id": 43,
                    "season_id": 106,
                    "value": "43|106|ALL",
                }
            ]
        )

    tournaments = tournaments.dropna(subset=["label", "value"]).copy()

    return [
        {
            "label": str(row["label"]),
            "value": str(row["value"]),
        }
        for _, row in tournaments.iterrows()
    ]

def filter_local_data_by_tournament(tournament_value):
    goals = _all_goals_df.copy()
    events = _all_events_df.copy()

    # Wenn die processed CSVs eine Turnier-Spalte haben,
    # filtern wir nach dem ausgewählten Turnier.
    if "competition_value" in goals.columns:
        filtered_goals = goals[
            goals["competition_value"].astype(str).eq(str(tournament_value))
        ].copy()

        if not filtered_goals.empty:
            goals = filtered_goals

    if "competition_value" in events.columns:
        filtered_events = events[
            events["competition_value"].astype(str).eq(str(tournament_value))
        ].copy()

        if not filtered_events.empty:
            events = filtered_events

    return goals, events

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    prevent_initial_callbacks="initial_duplicate",
    title="Coach Attack Explorer",
)
server = app.server
app.layout = build_layout(
    goals_df,
    load_selected_tournaments(),
)


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


def team_info_card(summary, goals):
    selected_team = summary.get("team", "All teams")

    if selected_team == "All teams":
        return html.Div(
            [
                html.Div("Select one team", className="mini-table-title"),
                html.Div(
                    "Choose one team above the replay to see its goal build-up profile.",
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
            .agg(
                goals=("build_up_id", "nunique"),
                avg_passes=("passes_before_goal", "mean"),
            )
            .sort_values("avg_passes", ascending=True)
            .reset_index(drop=True)
        )

        if selected_team in set(team_rank_df["team"]):
            rank = int(team_rank_df.index[team_rank_df["team"].eq(selected_team)][0]) + 1
            rank_text = f"{rank} of {len(team_rank_df)} teams by directness"
        else:
            rank_text = "Not ranked"

    goal_rows = []

    for _, row in team_goals.head(8).iterrows():
        minute = row.get("minute", row.get("goal_minute", ""))
        scorer = row.get("scorer", "")
        passes = row.get("passes_before_goal", "")
        style = row.get("build_up_type", "")

        try:
            minute = f"{int(float(minute))}'" if str(minute) != "" else ""
        except Exception:
            minute = str(minute)

        goal_rows.append(
            html.Tr(
                [
                    html.Td(str(minute)),
                    html.Td(str(scorer)),
                    html.Td(str(passes)),
                    html.Td(str(style)),
                ]
            )
        )

    if not goal_rows:
        goal_rows = [
            html.Tr(
                [
                    html.Td("No goals"),
                    html.Td("-"),
                    html.Td("-"),
                    html.Td("-"),
                ]
            )
        ]

    return html.Div(
        [
            html.Div(
                [
                    html.Div("Selected team", className="mini-table-title"),
                    html.Div(
                        f"{selected_team} is analysed using the locally prepared goal build-up data.",
                        className="mini-table-subtitle",
                    ),
                    html.Div(
                        [
                            info_pair("Team", selected_team),
                            info_pair("Goals analysed", len(team_goals)),
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
                    html.Div("Analysed goal examples", className="mini-table-title"),
                    html.Div(
                        "Goal build-ups available for the selected team in this tournament.",
                        className="mini-table-subtitle",
                    ),
                    html.Table(
                        [
                            html.Thead(
                                html.Tr(
                                    [
                                        html.Th("Minute"),
                                        html.Th("Scorer"),
                                        html.Th("Passes"),
                                        html.Th("Style"),
                                    ]
                                )
                            ),
                            html.Tbody(goal_rows),
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


def top_team_table(goals, selected_team=None):
    if goals.empty:
        return html.Div(
            "No team ranking available yet. Choose a tournament first.",
            className="empty-state",
        )

    stage_col = None
    for col in ["stage", "competition_stage", "match_stage", "round"]:
        if col in goals.columns:
            stage_col = col
            break

    stage_order = {
        "Group Stage": 1,
        "Round of 16": 2,
        "Quarter-finals": 3,
        "Semi-finals": 4,
        "3rd Place Final": 5,
        "Final": 6,
    }

    def classify_style(avg_passes):
        if avg_passes <= 3:
            return "Direct"
        if avg_passes <= 6:
            return "Balanced"
        return "Patient"

    def best_stage(team_df):
        if stage_col is None or team_df.empty:
            return "Not available"

        stages = team_df[stage_col].dropna().astype(str).unique().tolist()

        if not stages:
            return "Not available"

        stages = sorted(
            stages,
            key=lambda item: stage_order.get(item, 0),
            reverse=True,
        )

        return stages[0]

    ranking = (
        goals.groupby("team", as_index=False)
        .agg(
            goals=("build_up_id", "nunique"),
            avg_passes=("passes_before_goal", "mean"),
            avg_duration=("attack_duration_seconds", "mean"),
        )
        .sort_values("avg_passes", ascending=True)
        .reset_index(drop=True)
    )

    ranking["directness_rank"] = ranking.index + 1

    rows = []

    # Show compact ranking. Keep selected team visible even if outside top 18.
    visible_ranking = ranking.head(18).copy()

    if selected_team and selected_team in set(ranking["team"]):
        selected_row = ranking[ranking["team"].eq(selected_team)]

        if not selected_row.empty and selected_team not in set(visible_ranking["team"]):
            visible_ranking = pd.concat([visible_ranking, selected_row], ignore_index=True)

    for _, row in visible_ranking.iterrows():
        team_name = str(row["team"])
        team_goals = goals[goals["team"].astype(str).eq(team_name)].copy()

        avg_passes = float(row["avg_passes"])
        style = classify_style(avg_passes)
        finish = best_stage(team_goals)

        row_class = "selected-ranking-row" if selected_team and team_name == selected_team else ""

        rows.append(
            html.Tr(
                [
                    html.Td(int(row["directness_rank"])),
                    html.Td(team_name),
                    html.Td(finish),
                    html.Td(int(row["goals"])),
                    html.Td(f"{avg_passes:.1f}"),
                    html.Td(f"{float(row['avg_duration']):.0f}s"),
                    html.Td(style),
                ],
                className=row_class,
            )
        )

    selected_note = ""

    if selected_team and selected_team in set(ranking["team"]):
        selected_row = ranking[ranking["team"].eq(selected_team)].iloc[0]
        selected_team_goals = goals[goals["team"].astype(str).eq(str(selected_team))]
        selected_finish = best_stage(selected_team_goals)

        selected_note = (
            f"{selected_team} is directness rank {int(selected_row['directness_rank'])} "
            f"of {len(ranking)} teams and reached: {selected_finish}."
        )

    return html.Div(
        [
            html.Div(
                "Lower rank means fewer completed passes before goals. The finish column shows how far the team reached.",
                className="mini-table-subtitle",
            ),
            html.Div(selected_note, className="mini-table-subtitle selected-ranking-note") if selected_note else html.Div(),
            html.Table(
                [
                    html.Thead(
                        html.Tr(
                            [
                                html.Th("Rank"),
                                html.Th("Team"),
                                html.Th("Finish"),
                                html.Th("Goals"),
                                html.Th("Avg passes"),
                                html.Th("Avg duration"),
                                html.Th("Style"),
                            ]
                        )
                    ),
                    html.Tbody(rows),
                ],
                className="team-table compact-match-table ranking-table",
            ),
        ],
        className="ranking-grid",
    )

@app.callback(
    Output("match-filter", "options"),
    Output("match-filter", "value"),
    Input("competition-season-filter", "value"),
)
def update_match_dropdown(competition_value):
    if not competition_value:
        return [], None

    return [
        {
            "label": "All matches in this tournament",
            "value": competition_value,
        }
    ], competition_value

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
    Input("match-filter", "value"),
    Input("load-match-button", "n_clicks"),
    prevent_initial_call=False,
)
def load_selected_match(match_value, _clicks):
    global goals_df, events_df, team_df, tournament_goals_df

    if not match_value:
        return (
            None,
            0,
            [],
            None,
            [],
            None,
            [],
            None,
            "Please choose a tournament first.",
            "No tournament selected.",
        )

    goals_df, events_df = filter_local_data_by_tournament(match_value)
    team_df = _team_df.copy()
    tournament_goals_df = goals_df.copy()

    if goals_df.empty:
        return (
            None,
            0,
            [],
            None,
            [],
            None,
            [],
            None,
            "No local goal data found for this tournament.",
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
        f"Loaded tournament data: {len(goals_df)} goal build-ups available.",
        f"{len(goals_df)} goals in selection",
    )

@app.callback(
    Output("overview-build-up-chart", "figure"),
    Output("overview-scatter-chart", "figure"),
    Input("selected-build-up", "data"),
    Input("team-filter", "value"),
    Input("type-filter", "value"),
)
def render_overview(selected_goal, selected_team, selected_build_type):
    if goals_df.empty:
        return (
            empty_figure("Choose a tournament first."),
            empty_figure("After loading, this chart shows whether attacks are direct or patient."),
        )

    plot_goals = selected_goals(selected_team, selected_build_type)

    if plot_goals.empty:
        return (
            empty_figure("No goals for this team and build-up type."),
            empty_figure("No goals for this team and build-up type."),
        )

    return (
        build_up_distribution(plot_goals),
        passes_duration_scatter(plot_goals, selected_goal),
    )

@app.callback(
    Output("team-tournament-info", "children"),
    Input("team-filter", "value"),
    Input("selected-build-up", "data"),
)
def render_team_tournament_info(selected_team, selected_goal):
    if goals_df.empty:
        return html.Div(
            "Load the local CSV data first.",
            className="empty-state",
        )

    if not selected_team:
        return team_info_card(
            {
                "team": "All teams",
                "matches": [],
                "formation": "Select a team",
                "summary": "Select one team in the replay filter to see team information.",
            },
            tournament_goals_df,
        )

    summary = {
        "team": selected_team,
        "matches": [],
        "formation": "Not available",
        "summary": f"{selected_team} is analysed using the locally prepared goal build-up data.",
    }

    return team_info_card(summary, tournament_goals_df)


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
    return (
        team_build_up_profile(tournament_goals_df, selected_team),
        top_team_table(tournament_goals_df, selected_team),
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
