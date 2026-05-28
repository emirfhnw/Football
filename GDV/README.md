# GDV – Goal Build-up Analysis

This folder contains the GDV part of the football visualization project.

## Project topic

The project analyses how goals were created at the FIFA World Cup 2022. The main focus is on goal build-ups: whether goals were created through quick attacks with few completed passes or through longer passing sequences.

## Research question

How were goals created at the FIFA World Cup 2022: through quick attacks with few passes or through longer passing sequences?

## Dataset

The project uses StatsBomb Open Data for the FIFA World Cup 2022. The analysis is based on event data, especially goals, passes, shots, teams, players, timestamps, match information and event coordinates.

Important limitation: this is event data only. The project does not use tracking data and does not show off-ball movement.

## GDV focus

The GDV part focuses on static visualizations and their design rationale. The goal is to communicate the main patterns clearly before moving to the interactive IVI dashboard.

Main visual questions:

1. Which build-up type is most common before goals?
2. Do longer passing sequences also take more time?
3. Which teams scored after more direct or more patient build-ups?
4. Can selected goal sequences be explained visually?
5. How clear are the static figures for users?

## Folder structure

```text
GDV/
|-- README.md
|-- report/
|   |-- gdv_report_draft.md
|-- evaluation/
|   |-- gdv_evaluation_tasks.md
|   |-- gdv_evaluation_summary.md
|   |-- gdv_evaluation_analysis.md
|   |-- gdv_evaluation_results_template.csv
```

## Evaluation

The evaluation uses a small formative think-aloud test. Participants inspect the static figures and answer short interpretation tasks. The goal is not to prove a hypothesis statistically, but to check whether the figures are understandable and whether the design needs improvement.

## Final submission checklist for GDV

Before submission, the following items should be present:

- final GDV report as PDF
- final static figures included or referenced in the report
- evaluation tasks
- anonymised evaluation results or notes
- evaluation summary with design improvements
- clear references in APA style
- reproducible code or clear link to the preprocessing/analysis code

## Honest status

The GDV documentation and evaluation structure are prepared. The remaining critical task is to make sure the final figures are exported and referenced consistently in the final report PDF.
