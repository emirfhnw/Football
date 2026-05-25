from __future__ import annotations

from dash import dcc, html
import dash_bootstrap_components as dbc

from .utils import BUILD_UP_ORDER


GRAPH_CONFIG = {"displayModeBar": False, "displaylogo": False, "responsive": True}


def options(values):
    return [{"label": str(value), "value": str(value)} for value in sorted(set(values)) if str(value)]


def goal_options(goals_df):
    return [{"label": row["goal_label"], "value": str(row["build_up_id"])} for _, row in goals_df.iterrows()]


def card(children, class_name: str = ""):
    return html.Div(children, className=f"panel {class_name}".strip())


def section_title(title: str, subtitle: str | None = None):
    return html.Div(
        [
            html.Div(title, className="section-title"),
            html.Div(subtitle, className="section-subtitle") if subtitle else None,
        ],
        className="section-heading",
    )


def app_header():
    return html.Header(
        [
            html.Div(
                [
                    html.Div("StatsBomb Attack Explorer", className="app-title"),
                    html.Div(
                        "Interactive coach dashboard for attacking patterns, goal build-ups and team styles",
                        className="app-subtitle"
                    ),
                ]
            ),
            html.Div("Event data only · ball actions, no off-ball tracking", className="data-note"),
        ],
        className="app-header",
    )

def kpi_card(label: str, value: object, suffix: str = ""):
    return html.Div(
        [
            html.Div([html.Span(value), html.Span(suffix, className="kpi-suffix")], className="kpi-value"),
            html.Div(label, className="kpi-label"),
        ],
        className="kpi-card",
    )


def kpi_row(kpis):
    cards = [
        ("Goals analysed", kpis["total_goals"], ""),
        ("Avg passes before goal", kpis["avg_passes"], ""),
        ("Avg attack duration", kpis["avg_duration"], "s"),
        ("Most common type", kpis["most_common_type"], ""),
    ]
    return html.Div([kpi_card(label, value, suffix) for label, value, suffix in cards], className="kpi-row")

def form_field(label: str, component):
    return html.Div([html.Label(label), component], className="form-field")


def replay_filters(goals_df):
    return card(
        [
            html.Div(
                [
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
                        "Build-up Type",
                        dcc.Dropdown(
                            id="type-filter",
                            options=[{"label": item, "value": item} for item in BUILD_UP_ORDER],
                            multi=True,
                            placeholder="All build-up types",
                            className="dash-dropdown",
                        ),
                    ),
                    form_field(
                        "Goal",
                        dcc.Dropdown(
                            id="goal-dropdown",
                            options=goal_options(goals_df),
                            value=str(goals_df.iloc[0]["build_up_id"]) if not goals_df.empty else None,
                            placeholder="Select a goal",
                            className="dash-dropdown goal-select",
                        ),
                    ),
                    dbc.Button("Reset", id="reset-button", color="primary", outline=True, className="reset-button"),
                ],
                className="filter-strip",
            ),
            html.Div(id="filter-feedback", className="filter-feedback"),
        ],
        "filter-panel",
    )


def overview_tab():
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("Coach question", className="hero-label"),
                            html.Div(
                                "Which attacking patterns from professional football can a coach turn into simple training ideas?",
                                className="hero-title"
                            ),
                            html.Div(
                                "Use the dashboard to compare goal build-ups, inspect passing sequences and identify teams that attack more directly or more patiently.",
                                className="hero-text"
                            ),
                        ],
                        className="hero-card",
                    ),
                    html.Div(id="overview-kpis"),
                ],
                className="overview-top",
            ),
            html.Div(
                [
                    card(
                        [
                            section_title(
                                "Goal build-up types",
                                "How often do goals come from quick, medium or longer attacking sequences?"
                            ),
                            dcc.Graph(id="overview-build-up-chart", config=GRAPH_CONFIG, className="chart-graph"),
                        ],
                        "chart-panel",
                    ),
                    card(
                        [
                            section_title(
                                "Passes vs duration",
                                "Do attacks with more completed passes also take more time?"
                            ),
                            dcc.Graph(id="overview-scatter-chart", config=GRAPH_CONFIG, className="chart-graph"),
                        ],
                        "chart-panel",
                    ),
                ],
                className="overview-grid",
            ),
            html.Div(id="overview-insight", className="insight-text"),
        ],
        className="tab-page overview-page",
    )

def pitch_legend():
    return html.Div(
        [
            html.Span([html.I(className="legend-swatch pass"), "Pass"]),
            html.Span([html.I(className="legend-swatch final-pass"), "Final pass"]),
            html.Span([html.I(className="legend-swatch shot"), "Shot"]),
            html.Span([html.I(className="legend-swatch goal"), "Goal"]),
            html.Span([html.I(className="legend-swatch current"), "Current"]),
        ],
        className="pitch-legend",
    )


def replay_controls():
    return html.Div(
        [
            dbc.Button("Previous", id="step-prev", color="secondary", outline=True),
            dbc.Button("Next", id="step-next", color="primary"),
            dbc.Button("Show full sequence", id="step-all", color="light", outline=True),
            dbc.Button("Reset replay", id="step-reset", color="light", outline=True),
        ],
        className="replay-controls",
    )


def goal_replay_tab(goals_df):
    return html.Div(
        [
            replay_filters(goals_df),
            html.Div(
                [
                    card(
                        [
                            section_title(
                                "Attack Replay",
                                "Inspect one goal sequence step by step. This is useful as an example, not as statistical proof."
                            ),
                            dcc.Graph(id="pitch-graph", config=GRAPH_CONFIG, className="pitch-graph"),
                            pitch_legend(),
                        ],
                        "pitch-panel",
                    ),
                    card(
                        [
                            html.Div(id="step-info", className="step-info"),
                            replay_controls(),
                            html.Div("Jump to event", className="mini-label"),
                            html.Div(id="mini-steps", className="mini-steps"),
                        ],
                        "replay-side",
                    ),
                ],
                className="replay-grid",
            ),
        ],
        className="tab-page replay-page",
    )


def team_comparison_tab():
    return html.Div(
        [
            html.Div(
                [
                    card(
                        [
                            section_title(
                                "Team attacking profile",
                                "Teams sorted by average completed passes before goals."
                            ),
                            dcc.Graph(id="team-chart", config=GRAPH_CONFIG, className="team-graph"),
                        ],
                        "team-chart-panel",
                    ),
                    card(
                        [
                            section_title(
                                "Most patient teams",
                                "These teams used the longest passing sequences before goals."
                            ),
                            html.Div(id="top-teams-table"),
                        ],
                        "top-table-panel",
                    ),
                ],
                className="team-grid",
            ),
            html.Div(
                "Coach interpretation: A high average does not automatically mean better attacking quality. It mainly shows whether a team tends to reach goals through patient build-up or more direct attacks.",
                className="insight-text",
            ),
        ],
        className="tab-page team-page",
    )

def build_layout(goals_df):
    return html.Div(
        [
            dcc.Store(id="selected-build-up", data=str(goals_df.iloc[0]["build_up_id"]) if not goals_df.empty else None),
            dcc.Store(id="step-store", data=0),
            app_header(),
            dcc.Tabs(
                id="main-tabs",
                value="overview",
                className="main-tabs",
                children=[
                    dcc.Tab(label="Coach Overview", value="overview", className="main-tab", selected_className="main-tab-selected", children=overview_tab()),
                    dcc.Tab(label="Attack Replay", value="replay", className="main-tab", selected_className="main-tab-selected", children=goal_replay_tab(goals_df)),
                    dcc.Tab(label="Team Profile", value="teams", className="main-tab", selected_className="main-tab-selected", children=team_comparison_tab()),                ],
            ),
        ],
        className="app-shell",
    )
