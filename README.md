# NFL Week 2 Composite Ratings Model

A preliminary team rating and game-projection system built on the Week 2 composite power
ratings (FPI, nfelo, Inpredictable, Unexpected Points, FTN DVOA, PFF; data via @SamHoppen).

## Contents

- `model/week2_ratings_model.py` — decomposes each team's composite rating into offense/defense
  splits, computes source-vs-composite correlation and divergence (feature importance proxy),
  blends each Week 2 starting QB's 2025 season form (passing + rushing combined) with their 2026
  Week 1 game into a capped points-per-game adjustment, shrinks the resulting margin toward the
  market line (weight grows as more weeks get validated), and runs a 5,000-iteration Monte Carlo
  simulation for all 16 Week 2 matchups at each stage — base, QB-adjusted, and market-blended
  (spread, win probability, 68%/95% confidence intervals, and a confidence score).
- `model/week2_model_output.json` — the model's output, consumed directly by the dashboard.
- `model/calibrate_market_blend.py` — grid-searches the in-sample MAE-minimizing blend weight on
  Week 2 (came out to 0.0, pure market — a small-sample overfit, not a real answer) to show why
  the main model uses a shrinkage formula instead. Re-run this once more weeks validate.
- `model/validate_week2.py` — scores the base, QB-adjusted, and market-blended projections
  against confirmed final results for all 16 Week 2 games (margin MAE, straight-up accuracy,
  total-points error, ATS record vs. market where the model diverged), alongside the same
  metrics for the closing market line as a benchmark. Output: `model/week2_validation_output.json`.
- `data/sis_qb_*.csv` — raw SIS DataHub QB tables: 2025 season and 2026 Week 1, passing and
  rushing, box score/rate/points-based variants, used to build the QB adjustment layer.
- `dashboard/week2_dashboard.html` — interactive dashboard: team ratings, feature importance, a
  QB report (tier, hot/cold trend vs. 2025 form, backup-starter flags), per-matchup projections
  vs. market lines, a full-slate validation scorecard against final results, and a ranked list
  of improvement levers.
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
- Full market lines (spread, total, moneyline) are sourced for all 16 Week 2 games. The model's
  own margin is now shrunk toward the market line before simulation, at
  `model_weight = validated_games/(validated_games+64)` capped at 0.5 — i.e. mostly market early,
  trusting the model more as validated weeks accumulate. With only Week 2 validated so far,
  that's 20% model / 80% market.
- Every Week 2 starter also started Week 1 (confirmed against the SIS data), so the composite
  ratings already reflect each team's current arm. The QB layer instead catches teams whose
  Week 1 form was likely a small-sample outlier relative to their 2025 baseline (partial
  regression toward that baseline, capped at ±1.2 pts/game) and flags the three teams
  (Falcons, Vikings, Seahawks) starting a QB clearly below their normal QB1.
- The QB value used for that regression combines passing AND rushing production (points above
  average, SIS DataHub). This matters most for mobile QBs: Mahomes' and Jackson's rushing pulls
  a mediocre Week 1 passing line back toward average, and Hurts' and Daniels' ground production
  is a real share of their overall value that passing-only stats would have missed entirely.

Re-run the model with `python3 model/week2_ratings_model.py` (standard library only, no
external dependencies).

## Week 2 validation (final)

All 16 games are complete. Scored against the model's own pre-game numbers, no hindsight refitting:

| | Margin MAE | Straight-up |
|---|---|---|
| Base model (no QB adj.) | 12.26 pt | 10/16 (62%) |
| QB-adjusted model | 12.03 pt | 10/16 (62%) |
| **Market-blended model** | **11.84 pt** | **11/16 (69%)** |
| Closing market line | 11.69 pt | 11/16 (69%) |

The market beat every model version on margin MAE. The QB adjustment nudged the model closer
to the market on which side actually covered (6/13 vs. 3/13 among games where model and market
diverged by ≥0.3 pt) without moving overall margin accuracy. The market blend (lever #1, built
after this validation) closes most of the remaining gap and matches the market's straight-up
rate — **but that's a calibration result, not an out-of-sample validation**: the blend weight
and the market line both came from this same 16-game week, so treat it as "the mechanism works
as intended," not "the model is now market-competitive." The honest test is Week 3.

The week was upset-heavy (Panthers 34–3 over the Falcons, Browns and Raiders winning outright as
6.5–8.5 pt road underdogs, Saints coming back to beat the Ravens), which no rating-based model
without injury/in-game context was going to catch — but the market didn't fully see those coming
either and still won out. The clearest, most actionable finding: point totals ran well over the
model's projections on the week's shootouts (Bills–Lions, Chiefs–Colts, Commanders–Cowboys all
landed 15–30 points above the model's total), consistent with lever #3 (true offense/defense
splits) being the more urgent fix. Run `python3 model/validate_week2.py` to reproduce.
