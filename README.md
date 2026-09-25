# NFL Composite Ratings Model

A team rating and game-projection system built on the weekly composite power ratings (FPI,
nfelo, Inpredictable, Unexpected Points, FTN DVOA, PFF; data via @SamHoppen). Now on **Week 3
(v0.4)** — Week 2 files are kept alongside as the validated baseline everything since has been
checked against.

## Contents (current: Week 3)

- `model/week3_ratings_model.py` — decomposes each team's composite rating into a **real**
  offense/defense split (SIS DataHub run-defense + pass-defense data; offense is the residual of
  the vendor's own composite = offense − defense identity), blends each Week 3 starting QB's 2025
  season form with their 2026 season-to-date into a capped points-per-game adjustment, shrinks
  the resulting margin toward the market line (weight grows as more weeks get validated), and
  runs a 5,000-iteration Monte Carlo simulation for all 15 active Week 3 matchups at each stage —
  base, QB-adjusted, and market-blended (spread, win probability, 68%/95% confidence intervals,
  a confidence score).
- `model/week3_model_output.json` — the model's output, consumed directly by the dashboard.
- `model/parse_injuries.py` — parses the full-league injury report (`data/nfl_injuries_*.docx`)
  into structured per-team data, filtered to positions that plausibly move a line (QB, RB, WR,
  TE, OT/OG/C, CB). The docx text extraction had captured the whole report twice (an exact
  duplicate second half); Washington, alphabetically last, had no anchor to stop its slice at and
  absorbed the entire second copy (159 "injuries" instead of 4) — fixed by detecting and dropping
  the duplicate before parsing.
- `model/tier_injuries.py` — ranks each team's RB/WR/TE room by real 2025 season value (receiving
  + rushing PAA) and tags the injury feed with a depth-chart tier (`WR1`, `RB2`, ...) instead of a
  bare position; a player who's changed teams since 2025 gets their prior-team value slotted into
  the new roster (flagged with a trailing `*`). Reference data only so far — see the levers list
  in the dashboard (§07).
- `data/sis_team_*def*.csv`, `sis_team_passrush_*.csv` — raw SIS DataHub team run-defense and
  pass-defense tables (2025 season + 2026 through Week 2), used to build the real off/def split.
  Pass-rush data is collected but intentionally **not** summed into the defense total — a
  sack/pressure event already shows up in pass-defense's own EPA-allowed number for that play,
  so adding both would double-count.
- `data/sis_qb_2026_thru_wk2_*.csv` — QB passing tables through Week 2 (season-to-date), replacing
  the Week-1-only files used for Week 2.
- `data/sis_rushing_2026_thru_wk2.csv` — per-player rushing value (SIS DataHub) through Week 2,
  now feeding the `QB_2026_YTD` rush columns that were held at zero last build — the "passing-only"
  QB gap from the previous version of this README is closed.
- `data/sis_receiving_2025.csv`, `data/sis_receiving_2026_thru_wk2.csv` — per-player receiving
  value (SIS DataHub), full 2025 season and 2026 season-to-date.
- `data/sis_rushing_2025.csv` — real full 2025 season rushing value, replacing an earlier upload
  that turned out to be a byte-for-byte duplicate of the 2026-to-date file. Together with the
  receiving tables, this now drives the injury report's depth-chart tiers (§06); it isn't a point
  adjustment in the simulation yet — see the levers list in the dashboard (§07).
- `dashboard/week3_dashboard.html` — interactive dashboard: team ratings (real off/def split),
  feature importance, a QB report, per-matchup projections vs. market lines, validation (Week 2's
  full scorecard + an early Week 3 read), an injury report, and ranked improvement levers.
  Published version: https://claude.ai/artifact/UAHh6VMKw8rtVcrH2KXoMZ

Prior week's files (`model/week2_*`, `dashboard/week2_dashboard.html`, `model/calibrate_market_blend.py`,
`model/validate_week2.py`) are kept as-is — they're the validated history the Week 3 build was calibrated against.

## What changed this week

- **Real offense/defense split** (previously a synthetic 50/50-plus-tilt heuristic). This also
  surfaced a real bug: the total-points formula summed both teams' offenses in isolation and
  never referenced either team's defense at all, which was very likely the main driver of Week
  2's systematic total-points underprediction (Bills–Lions projected 49, actual 72; see Week 2
  validation below). Fixed alongside the split — Week 2's total-points MAE improves from ~12.0 to
  ~10.1 pts under the corrected formula (re-run, not a new prediction).
- **QB data refreshed to season-to-date** (2 games) instead of Week 1 only — passing and rushing
  both now (rushing was passing-only in the first Week 3 build; the rushing table arrived after).
- **Real lineup churn handled**: Atlanta gets Michael Penix Jr. back (from Cooper Rush), Minnesota
  starts Kyler Murray, and injuries push Washington (Jayden Daniels, elbow), Seattle (Sam Darnold),
  and the Giants (Jaxson Dart, IR) to backups.
- **Full-league injury report** parsed and referenced (dashboard §06) — not yet a calibrated
  point adjustment; see levers list for what that needs. Also fixed a duplicate-data bug in the
  parser (Washington was showing 159 "injuries" instead of 4 — see `model/parse_injuries.py`
  above) and added depth-chart tiers (WR1, RB2, ...) from real 2025 season value.

## Key modeling assumptions

- Home-field advantage is a flat 2.0 points league-wide.
- Simulation variance blends a 13.0-pt base NFL game-margin standard deviation with each team's
  cross-model "Std Dev" column (source disagreement) as an uncertainty inflator.
- The Week-to-week composite momentum chart carries no numeric deltas, so momentum is encoded
  qualitatively (direction + rough magnitude) rather than as a simulation input.
- The model's own margin is shrunk toward the market line before simulation, at
  `model_weight = validated_games/(validated_games+64)` capped at 0.5 — i.e. mostly market early,
  trusting the model more as validated weeks accumulate. With only Week 2 validated so far,
  that's 20% model / 80% market.
- The QB adjustment is a capped (±1.2 pt/game), recency-weighted partial regression toward each
  starter's 2025 baseline (passing + rushing where both years' data exist), not a hot/cold
  overcorrection.
- Defense per team blends 2025 season value (17 games) with 2026 value through Week 2, weighted
  more heavily toward the current season than the QB blend to reflect year-over-year roster
  turnover (`DEF_RECENCY_BOOST = 6` vs. `RECENCY_BOOST = 5` for QBs — both tunable, not fit).

Re-run the model with `python3 model/week3_ratings_model.py` (standard library only, no external
dependencies).

## Week 2 validation (final, unchanged from last week)

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
either and still won out. Run `python3 model/validate_week2.py` to reproduce.

## Week 3 so far

Thursday's game is final: **Falcons 35, Packers 14**. The model (run with Cooper Rush still the
presumed Falcons QB, since Penix's return wasn't yet reflected pre-kickoff) favored Green Bay by
6 — Michael Penix Jr.'s return plus a 194-yard, 2-TD game from Bijan Robinson blew that out by 27
points. One data point, and exactly the kind of in-game swing (a QB return, a breakout rushing
day) a rating-based model has no way to see coming. The other 15 games haven't kicked off yet.
