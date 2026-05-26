from __future__ import annotations

from dash import dcc, html
import dash_bootstrap_components as dbc


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
            label = f"{team} - {scorer} ({minute}')"
            if opponent:
                label += f" vs {opponent}"

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


def form_field(label: str, component):
    return html.Div([html.Label(label), component], className="form-field")


def app_header():
    return html.Header(
        [
            html.Div(
                [
                    html.Div("Coach Attack Explorer", className="app-title"),
                    html.Div(
                        "Tournament dashboard for comparing direct and patient goal attacks",
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
                        "Tournament",
                        dcc.Dropdown(
                            id="competition-season-filter",
                            options=competition_options,
                            value=None,
                            placeholder="Choose tournament / season",
                            clearable=False,
                            className="dash-dropdown",
                        ),
                    ),
                    form_field(
                        "Analysis scope",
                        dcc.Dropdown(
                            id="match-filter",
                            options=[],
                            value=None,
                            clearable=False,
                            placeholder="All matches in tournament",
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
                className="data-source-grid final-source-grid",
            ),
            html.Div(
                "Recommended workflow: choose a full tournament, keep 'All matches in this tournament', then select a team in the replay filter below.",
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


def replay_filters(goals_df):
    return card(
        [
            html.Div(
                [
                    form_field(
                        "Team for replay and team info",
                        dcc.Dropdown(
                        id="team-filter",
                            options=[],
                            multi=False,
                            placeholder="Choose one team",
                            className="dash-dropdown",
                        ),

                    ),
                    form_field(
                        "Build-up type",
                        dcc.Dropdown(
                            id="type-filter",
                            options=[],
                            multi=False,
                            placeholder="All build-up types",
                            className="dash-dropdown",
                        ),
                    ),
                    form_field(
                        "Goal example",
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
        "filter-panel replay-filter-panel",
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
                        marks={300: "fast", 800: "normal", 1500: "slow"},
                        tooltip={"placement": "bottom", "always_visible": False},
                    ),
                ],
                className="speed-control",
            ),
        ],
        className="replay-controls",
    )


def attack_replay_section(goals_df):
    return html.Div(
        [
            replay_filters(goals_df),
            html.Div(
                [
                    card(
                        [
                            section_title(
                                "1. Attack Replay",
                                "Select one team and one goal example, then play the sequence step by step.",
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
            card(
                [
                    section_title(
                        "2. Team tournament information",
                        "Shown when exactly one team is selected in the replay filter.",
                    ),
                    html.Div(id="team-tournament-info"),
                ],
                "team-info-panel",
            ),
        ],
        className="one-page-section replay-page",
    )


def overview_section():
    return html.Div(
        [
            section_title(
                "3. Tournament overview",
                "These plots describe all loaded goals in the selected tournament or scope.",
            ),
            html.Div(id="overview-kpis"),
            html.Div(
                [
                    card(
                        [
                            section_title("Goal build-up types", "Direct, medium and patient goal attacks."),
                            dcc.Graph(id="overview-build-up-chart", config=GRAPH_CONFIG, className="chart-graph"),
                        ],
                        "chart-panel",
                    ),
                    card(
                        [
                            section_title("Passes vs duration", "Relationship between completed passes and attack duration."),
                            dcc.Graph(id="overview-scatter-chart", config=GRAPH_CONFIG, className="chart-graph"),
                        ],
                        "chart-panel",
                    ),
                ],
                className="overview-grid",
            ),
            html.Div(id="coach-takeaway", className="coach-takeaway"),
            html.Div(id="overview-insight", className="insight-text"),
        ],
        className="one-page-section overview-page",
    )


def team_profile_section():
    return html.Div(
        [
            section_title(
                "4. Team profile and tournament comparison",
                "Compare which teams score after shorter or longer attacking sequences.",
            ),
            html.Div(
                [
                    card(
                        [
                            section_title(
                                "Team goal style map",
                                "Compare direct and patient scoring styles. The selected team is highlighted in orange."
                            ),
                            dcc.Graph(id="team-chart", config=GRAPH_CONFIG, className="team-graph"),
                        ],
                        "team-chart-panel",
                    ),
                    card(
                        [
                            section_title("Style ranking", "Most direct, most patient and most efficient teams."),
                            html.Div(id="top-teams-table"),
                        ],
                        "top-table-panel",
                    ),
                ],
                className="team-grid",
            ),
            html.Div(
                "Interpretation: This does not prove which tactic is best. It shows tendencies that can be used for coaching discussion and replay selection.",
                className="insight-text",
            ),
        ],
        className="one-page-section team-page",
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
            attack_replay_section(goals_df),
            overview_section(),
            team_profile_section(),
        ],
        className="app-shell one-page-shell",
    )
