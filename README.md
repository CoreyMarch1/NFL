# NFL Week 2 Composite Ratings Model

A preliminary team rating and game-projection system built on the Week 2 composite power
ratings (FPI, nfelo, Inpredictable, Unexpected Points, FTN DVOA, PFF; data via @SamHoppen).

## Contents

- `model/week2_ratings_model.py` — decomposes each team's composite rating into offense/defense
  splits, computes source-vs-composite correlation and divergence (feature importance proxy),
  and runs a 5,000-iteration Monte Carlo simulation for all 16 Week 2 matchups (spread, win
  probability, 68%/95% confidence intervals, and a confidence score).
- `model/week2_model_output.json` — the model's output, consumed directly by the dashboard.
- `dashboard/week2_dashboard.html` — interactive dashboard: team ratings, feature importance,
  per-matchup projections vs. available market lines, a validation check against the Thursday
  night result, and a ranked list of improvement levers.
  Published version: https://claude.ai/artifact/UAHh6VMKw8rtVcrH2KXoMZ

## Key modeling assumptions (v0)

- The source table reports only a single net composite rating per team, not separate
  offense/defense splits. Offense/defense are synthesized around a 22.5-pt league-average
  baseline, tilted by each team's Unexpected Points score as a pace/style proxy. This is the
  single biggest thing to replace with real data (see levers list in the dashboard).
- Home-field advantage is a flat 2.0 points league-wide.
- Simulation variance blends a 13.0-pt base NFL game-margin standard deviation with each
  team's cross-model "Std Dev" column (source disagreement) as an uncertainty inflator.
- The Week 1→2 momentum chart carries no numeric deltas, so momentum is encoded qualitatively
  (direction + rough magnitude) rather than as a simulation input.
- Full market lines (spread, total, moneyline) are sourced for all 16 Week 2 games and shown
  alongside each projection for comparison — the market is not yet blended into the simulation
  itself (see the dashboard's improvement levers for that).

Re-run the model with `python3 model/week2_ratings_model.py` (standard library only, no
external dependencies).
