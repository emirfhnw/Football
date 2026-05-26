from __future__ import annotations

from dash import dcc, html
import dash_bootstrap_components as dbc

from .utils import BUILD_UP_ORDER


GRAPH_CONFIG = {"displayModeBar": False, "displaylogo": False, "responsive": True}


def options(values):
    return [{"label": str(value), "value": str(value)} for value in sorted(set(values)) if str(value)]


def goal_options(goals_df):
    if goals_df is None or goals_df.empty:
        return []

    out = []

    for _, row in goals_df.iterrows():
        build_up_id = str(row.get("build_up_id", ""))

        if "goal_label" in goals_df.columns and str(row.get("goal_label", "")).strip():
            label = row["goal_label"]
        else:
            team = str(row.get("team", "Unknown team"))
            scorer = str(row.get("scorer", "Unknown scorer"))
            minute = row.get("minute", "")
            opponent = str(row.get("opponent", "")).strip()

            if opponent:
                label = f"{team} - {scorer} ({minute}') vs {opponent}"
            else:
                label = f"{team} - {scorer} ({minute}')"

        out.append({"label": label, "value": build_up_id})

    return out

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
                        "Interactive dashboard for coaches: compare attacking styles, inspect goal build-ups and discuss training ideas",
                        className="app-subtitle",
                    ),
                ]
            ),
            html.Div("StatsBomb event data · ball actions only", className="data-note"),
        ],
        className="app-header",
    )

def data_source_panel(competition_options):
    return card(
        [
            html.Div(
                [
                    form_field(
                        "Competition / Season",
                        dcc.Dropdown(
                            id="competition-season-filter",
                            options=competition_options,
                            value=None,
                            placeholder="Choose competition / season",
                            clearable=False,
                            className="dash-dropdown",
                        ),
                    ),
                    form_field(
                        "Match",
                        dcc.Dropdown(
                            id="match-filter",
                            options=[],
                            value=None,
                            clearable=False,
                            placeholder="Select match",
                            className="dash-dropdown",
                        ),
                    ),
                    form_field(
                        "Team",
                        dcc.Dropdown(
                            id="team-scope-filter",
                            options=[{"label": "All teams", "value": "ALL"}],
                            value="ALL",
                            clearable=False,
                            className="dash-dropdown",
                        ),
                    ),
                    dbc.Button(
                        "Load",
                        id="load-match-button",
                        color="primary",
                        className="load-button",
                    ),
                ],
                className="data-source-grid",
            ),
            html.Div(
                "Select a competition, match and team, then press Load. The analysis appears only after a selection is loaded.",
                id="data-load-feedback",
                className="filter-feedback",
            ),
        ],
        "filter-panel",
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
                            options=[],
                            multi=True,
                            placeholder="All teams",
                            className="dash-dropdown",
                        ),
                    ),
                    form_field(
                        "Build-up Type",
                        dcc.Dropdown(
                            id="type-filter",
                            options=[],
                            multi=True,
                            placeholder="All build-up types",
                            className="dash-dropdown",
                        ),
                    ),
                    form_field(
                        "Goal",
                        dcc.Dropdown(
                            id="goal-dropdown",
                            options=[],
                            value=None,
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
                                "How do professional teams create goals, and which attacking ideas could be useful for amateur training?",
                                className="hero-title",
                            ),
                            html.Div(
                                "This dashboard is designed from a trainer perspective. Instead of only counting goals, it helps to inspect how attacks develop before a goal: how many passes are involved, how long the attack takes and how different teams build up their chances.",
                                className="hero-text",
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
                                "After loading a selection, this shows whether goals come from quick, medium or longer attacking sequences."
                            ),
                            dcc.Graph(id="overview-build-up-chart", config=GRAPH_CONFIG, className="chart-graph"),
                        ],
                        "chart-panel",
                    ),
                    card(
                        [
                            section_title(
                                "Passes vs duration",
                                "After loading a selection, this shows how completed passes relate to attack duration."
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
            dbc.Button("Play", id="play-button", color="success"),
            dbc.Button("Pause", id="pause-button", color="warning", outline=True),
            dbc.Button("Next", id="step-next", color="primary"),
            dbc.Button("Show full", id="step-all", color="light", outline=True),
            dbc.Button("Reset", id="step-reset", color="light", outline=True),

            html.Div(
                [
                    html.Label("Speed"),
                    dcc.Slider(
                        id="replay-speed",
                        min=300,
                        max=1500,
                        step=100,
                        value=800,
                        marks={
                            300: "fast",
                            800: "normal",
                            1500: "slow",
                        },
                        tooltip={"placement": "bottom", "always_visible": False},
                    ),
                ],
                className="speed-control",
            ),
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
                                "Load a match and play one goal sequence. Use it as a concrete example, not as statistical proof."
                            ),
                            dcc.Graph(id="pitch-graph", config=GRAPH_CONFIG, className="pitch-graph"),
                            pitch_legend(),
                        ],
                        "pitch-panel",
                    ),
                    card(
                        [
                            html.Div(
                                [
                                    html.Div("Coach focus", className="coach-focus-label"),
                                    html.Div(
                                        "Watch how the ball moves before the goal.",
                                        className="coach-focus-title",
                                    ),
                                    html.Div(
                                        "The replay is useful for discussing simple training points: first forward pass, support after the pass, timing of the final pass and the finish. It does not show off-ball runs, because the data only contains recorded events.",
                                        className="coach-focus-text",
                                    ),
                                ],
                                className="coach-focus-box",
                            ),
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
                                "After loading a selection, compare how teams score: direct attacks, patient build-up and finishing efficiency."
                            ),
                            dcc.Graph(id="team-chart", config=GRAPH_CONFIG, className="team-graph"),
                        ],
                        "team-chart-panel",
                    ),
                    card(
                        [
                            section_title(
                                "Style comparison",
                                "Direct teams, patient teams and efficient finishers in one view."
                            ),
                            html.Div(id="top-teams-table"),
                        ],
                        "top-table-panel",
                    ),
                ],
                className="team-grid",
            ),
            html.Div(
                "Coach interpretation: The dashboard does not rank one tactic as the best. It helps to compare different attacking styles. Some teams score after short sequences, others after longer possession phases. For training, this can support discussions about quick forward play, controlled build-up and finishing quality.",
                className="insight-text",
            ),
        ],
        className="tab-page team-page",
    )

def build_layout(goals_df, competition_options=None):
    return html.Div(
        [
            dcc.Store(id="selected-build-up", data=None),
            dcc.Store(id="step-store", data=0),
            dcc.Store(id="is-playing", data=False),
            dcc.Interval(id="replay-interval", interval=800, n_intervals=0, disabled=True),
            app_header(),
            data_source_panel(competition_options or []),
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
