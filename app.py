from __future__ import annotations

from dash import Dash, Input, Output, State, callback_context, dcc, html, no_update
import dash_bootstrap_components as dbc

from src.data_loader import load_dashboard_data
from src.figures import build_up_distribution, passes_duration_scatter, team_build_up_profile
from src.metrics import dashboard_kpis, filter_goals
from src.pitch_plots import pitch_sequence_figure, timeline_items
from src.utils import BUILD_UP_ORDER


goals_df, events_df, _team_df = load_dashboard_data()
DEFAULT_BUILD_UP = str(goals_df.iloc[0]["build_up_id"]) if not goals_df.empty else None

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Goal Build-up Analysis",
)
server = app.server


def options(values):
    return [{"label": str(value), "value": str(value)} for value in sorted(set(values)) if str(value)]


def goal_options(df):
    return [{"label": row["goal_label"], "value": str(row["build_up_id"])} for _, row in df.iterrows()]


def card(title: str, value: object, suffix: str = "") -> dbc.Col:
    return dbc.Col(
        html.Div(
            [
                html.Div(value, className="kpi-value"),
                html.Div([title, html.Span(suffix, className="kpi-suffix")], className="kpi-label"),
            ],
            className="kpi-card",
        ),
        xs=12,
        sm=6,
        lg=True,
    )


def header():
    return html.Header(
        [
            html.Div(
                [
                    html.H1("Goal Build-up Analysis"),
                    html.Div("FIFA World Cup 2022 · StatsBomb Event Data", className="subtitle"),
                ],
                className="header-title",
            ),
            html.Div(
                [
                    html.Nav(
                        [
                            html.A("Overview", href="#overview"),
                            html.A("Goal Explorer", href="#goal-explorer"),
                            html.A("Team Analysis", href="#team-analysis"),
                        ],
                        className="simple-nav",
                    ),
                    html.Div("Event data only · no tracking data", className="data-badge"),
                ],
                className="header-side",
            ),
        ],
        className="app-header",
    )


def kpi_row(kpis):
    return dbc.Row(
        [
            card("Goals analysed", kpis["total_goals"]),
            card("Avg passes before goal", kpis["avg_passes"]),
            card("Median passes before goal", kpis["median_passes"]),
            card("Avg attack duration", kpis["avg_duration"], "s"),
            card("Most common build-up", kpis["most_common_type"]),
        ],
        className="g-3",
    )


def filter_panel():
    return html.Div(
        [
            section_title("Filters"),
            form_field(
                "Team",
                dcc.Dropdown(
                    id="team-filter",
                    options=options(goals_df["team"]),
                    multi=True,
                    placeholder="All teams",
                    className="dash-dropdown",
                ),
            ),
            form_field(
                "Build-up type",
                dcc.Dropdown(
                    id="type-filter",
                    options=[{"label": item, "value": item} for item in BUILD_UP_ORDER],
                    multi=True,
                    placeholder="All types",
                    className="dash-dropdown",
                ),
            ),
            form_field(
                "Match",
                dcc.Dropdown(
                    id="match-filter",
                    options=options(goals_df["match_name"]),
                    multi=True,
                    placeholder="All matches",
                    className="dash-dropdown",
                ),
            ),
            dbc.Button("Reset filters", id="reset-button", color="light", className="button-reset"),
            html.Div(id="filter-feedback", className="selection-feedback"),
        ],
        className="side-card",
    )


def goal_selector():
    return html.Div(
        [
            section_title("Goal Selector"),
            dcc.Dropdown(
                id="goal-dropdown",
                options=goal_options(goals_df),
                value=DEFAULT_BUILD_UP,
                placeholder="Select a goal",
                className="dash-dropdown",
            ),
            html.Div("Select a goal or click a point in the scatterplot.", className="helper-text"),
        ],
        className="side-card",
    )


def goal_summary(goal_id: str | None):
    if not goal_id:
        return html.Div("No goal selected.", className="empty-state")
    match = goals_df[goals_df["build_up_id"].astype(str).eq(str(goal_id))]
    if match.empty:
        return html.Div("No goal selected.", className="empty-state")
    row = match.iloc[0]
    items = [
        ("Team", row["team"]),
        ("Minute", f"{int(row['minute'])}'"),
        ("Scorer", row["scorer"]),
        ("Passes before goal", int(row["passes_before_goal"])),
        ("Attack duration", f"{row['attack_duration_seconds']:.0f}s"),
        ("Build-up type", row["build_up_type"]),
    ]
    return html.Div([summary_item(label, value) for label, value in items], className="summary-grid")


def summary_item(label, value):
    return html.Div([html.Div(label, className="summary-label"), html.Div(value, className="summary-value")])


def timeline_panel(items):
    if not items:
        return html.Div("No sequence available.", className="empty-state")
    return html.Div(
        [
            html.Div(
                [
                    html.Div(item["step"], className="timeline-step"),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(item["action"], className="timeline-action"),
                                    html.Span(item["time"], className="timeline-time"),
                                ]
                            ),
                            html.Div(item["detail"], className="timeline-detail"),
                        ]
                    ),
                ],
                className="timeline-item active" if item["active"] else "timeline-item",
            )
            for item in items
        ],
        className="timeline-list",
    )


def section_title(text: str):
    return html.Div(text, className="section-title")


def form_field(label: str, component):
    return html.Div([html.Label(label), component], className="form-field")


app.layout = html.Div(
    [
        dcc.Store(id="selected-build-up", data=DEFAULT_BUILD_UP),
        dcc.Store(id="step-store", data=0),
        dbc.Container(
            [
                header(),
                html.Section(id="overview", children=[html.Div(id="kpi-row")], className="overview-section"),
                html.Section(
                    id="goal-explorer",
                    children=[
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    section_title("Selected Goal Build-up"),
                                                    html.Div("Completed passes and final shot from the same possession.", className="helper-text"),
                                                ],
                                                className="panel-heading",
                                            ),
                                            dcc.Graph(id="pitch-graph", config={"displayModeBar": False}),
                                            html.Div(
                                                [
                                                    dbc.Button("Previous", id="step-prev", color="secondary", className="step-button"),
                                                    dbc.Button("Next event", id="step-next", color="primary", className="step-button"),
                                                    dbc.Button("Show all", id="step-all", color="light", className="step-button"),
                                                ],
                                                className="step-controls",
                                            ),
                                        ],
                                        className="main-card pitch-card",
                                    ),
                                    lg=8,
                                ),
                                dbc.Col(
                                    [
                                        filter_panel(),
                                        goal_selector(),
                                        html.Div([section_title("Goal Summary"), html.Div(id="goal-summary")], className="side-card"),
                                        html.Div([section_title("Event Timeline"), html.Div(id="timeline-panel")], className="side-card timeline-card"),
                                    ],
                                    lg=4,
                                ),
                            ],
                            className="g-4",
                        )
                    ],
                    className="section-block",
                ),
                html.Section(
                    id="team-analysis",
                    children=[
                        html.Div(
                            [
                                section_title("Analysis"),
                                html.Div("Overview first, then click a goal for details on demand.", className="helper-text"),
                            ],
                            className="panel-heading",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(dcc.Graph(id="bar-chart", config={"displayModeBar": False}), lg=4),
                                dbc.Col(dcc.Graph(id="team-chart", config={"displayModeBar": False}), lg=8),
                            ],
                            className="g-4",
                        ),
                        dbc.Row(
                            [dbc.Col(dcc.Graph(id="scatter-chart", config={"displayModeBar": False}), lg=12)],
                            className="g-4",
                        ),
                    ],
                    className="section-block main-card",
                ),
            ],
            fluid=True,
            className="page-container",
        ),
    ]
)


def current_filtered_goals(teams, build_types, matches):
    return filter_goals(goals_df, teams=teams, build_types=build_types, matches=matches)


@app.callback(
    Output("team-filter", "value"),
    Output("type-filter", "value"),
    Output("match-filter", "value"),
    Input("reset-button", "n_clicks"),
    Input("bar-chart", "clickData"),
    prevent_initial_call=True,
)
def update_filters(reset_clicks, bar_click):
    trigger = callback_context.triggered_id
    if trigger == "reset-button":
        return [], [], []
    if trigger == "bar-chart" and bar_click:
        build_type = bar_click["points"][0].get("x")
        return no_update, [build_type], no_update
    return no_update, no_update, no_update


@app.callback(
    Output("goal-dropdown", "options"),
    Output("filter-feedback", "children"),
    Input("team-filter", "value"),
    Input("type-filter", "value"),
    Input("match-filter", "value"),
)
def update_goal_options(teams, build_types, matches):
    filtered = current_filtered_goals(teams, build_types, matches)
    return goal_options(filtered), f"{len(filtered)} goals in current selection"


@app.callback(
    Output("selected-build-up", "data"),
    Output("step-store", "data", allow_duplicate=True),
    Input("goal-dropdown", "value"),
    Input("scatter-chart", "clickData"),
    prevent_initial_call=True,
)
def select_goal(goal_id, scatter_click):
    trigger = callback_context.triggered_id
    if trigger == "scatter-chart" and scatter_click:
        return str(scatter_click["points"][0]["customdata"][0]), 0
    if trigger == "goal-dropdown" and goal_id:
        return str(goal_id), 0
    return no_update, no_update


@app.callback(
    Output("step-store", "data"),
    Input("step-prev", "n_clicks"),
    Input("step-next", "n_clicks"),
    Input("step-all", "n_clicks"),
    State("step-store", "data"),
    State("selected-build-up", "data"),
    prevent_initial_call=True,
)
def update_step(prev_clicks, next_clicks, all_clicks, current_step, goal_id):
    if not goal_id:
        return 0
    trigger = callback_context.triggered_id
    current_step = int(current_step or 0)
    max_step = int(events_df[events_df["build_up_id"].astype(str).eq(str(goal_id))]["event_order"].max())
    if trigger == "step-all":
        return 0
    if trigger == "step-prev":
        return max(0, current_step - 1)
    if trigger == "step-next":
        return 1 if current_step == 0 else min(max_step, current_step + 1)
    return current_step


@app.callback(
    Output("kpi-row", "children"),
    Output("bar-chart", "figure"),
    Output("team-chart", "figure"),
    Output("scatter-chart", "figure"),
    Output("pitch-graph", "figure"),
    Output("goal-summary", "children"),
    Output("timeline-panel", "children"),
    Input("team-filter", "value"),
    Input("type-filter", "value"),
    Input("match-filter", "value"),
    Input("selected-build-up", "data"),
    Input("step-store", "data"),
)
def render_dashboard(teams, build_types, matches, selected_goal, step):
    filtered = current_filtered_goals(teams, build_types, matches)
    selected_goal = selected_goal or (str(filtered.iloc[0]["build_up_id"]) if not filtered.empty else DEFAULT_BUILD_UP)
    active_step = int(step or 0) or None

    return (
        kpi_row(dashboard_kpis(filtered)),
        build_up_distribution(filtered),
        team_build_up_profile(filtered),
        passes_duration_scatter(filtered, selected_goal),
        pitch_sequence_figure(events_df, goals_df, selected_goal, active_step),
        goal_summary(selected_goal),
        timeline_panel(timeline_items(events_df, selected_goal, active_step)),
    )


if __name__ == "__main__":
    app.run(debug=True)
