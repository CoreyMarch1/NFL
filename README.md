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
  into structured per-team data, filtered to positions that plausibly move a line (QB, RB, WR, TE,
  OT, OG, C, CB, S, LB, DE, DT). The docx text extraction had captured the whole report twice (an
  exact duplicate second half); Washington, alphabetically last, had no anchor to stop its slice at
  and absorbed the entire second copy (159 "injuries" instead of 4) — fixed by detecting and
  dropping the duplicate before parsing.
- `model/tier_injuries.py` — ranks each team's room at every non-QB notable position by real 2025
  season **usage** (targets for WR/TE, rush attempts + targets for RB, snaps for OT/OG/C, combined
  run-defense/pass-rush/coverage snaps for CB/S/LB/DE/DT) and tags the injury feed with a
  depth-chart tier (`WR1`, `DE2`, ...) instead of a bare position. Deliberately sorts on usage, not
  PAA: PAA is an efficiency stat, and an inefficient starter (a 278-carry RB1 having a bad season)
  would rank below a highly-efficient backup on PAA alone — exactly backwards for a "who's the
  starter" read. A player who's changed teams since 2025 gets their prior-team usage slotted into
  the new roster (flagged with a trailing `*`); a jet-sweep WR with a few garbage rush attempts and
  no receiving record is kept out of the RB group by cross-checking position against the 2026
  receiving file and the injury report's own listed position. Reference data only so far — see the
  levers list in the dashboard (§07).
- `model/convert_snap_counts.py` → `data/nfl_snap_counts_2026_thru_wk2.csv` — per-player,
  per-game snap counts for 2026 Weeks 1-2 (a one-time ingestion script; needs `openpyxl` to read
  the source `.xlsx`, unlike everything else here, which stays standard-library-only). This is the
  games-played/usage denominator the injury lever has been missing — see "Injury point-adjustment:
  blocked on data completeness, not methodology" below for why it isn't wired in yet. `TeamId` and
  `PositionId` in the source file are numeric codes with no legend; both were reverse-engineered by
  cross-referencing player names already known from the other SIS files (>90% agreement per code)
  and spot-checked against a clean, independent ground truth (current 2026 rosters) before trusting
  them — an initial check against stale 2025-season team labels looked alarming (26% "wrong team"),
  but that turned out to be an error in the check, not the data: most of those were real 2025→2026
  trades the stale reference didn't know about.
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
  that turned out to be a byte-for-byte duplicate of the 2026-to-date file.
- `data/sis_blocking_2025.csv`, `sis_blocking_2026_thru_wk2.csv` — per-player offensive-line value
  (SIS DataHub), used to rank each team's OT/OG/C room. The season file repeats the same three
  column names (season total, then pass-block and run-block splits), so `tier_injuries.py` reads it
  positionally rather than by header name to avoid silently picking up the wrong "Snaps" column.
- `data/sis_player_passdef_2025.csv`, `sis_player_rundef_2025.csv`, `sis_player_passrush_2025.csv`
  (plus their 2026-to-date counterparts) — per-player pass-coverage, run-defense, and pass-rush
  value. A defender's snaps split cleanly across these three tables by play type (run play, pass
  play he rushed, pass play he covered), so summing whichever of the three a player appears in
  gives a real total-snaps usage figure for CB/S/LB/DE/DT, not a double count.
- Together, the receiving/rushing/blocking/pass-defense/run-defense/pass-rush tables now drive
  every non-QB tier in the injury report (§06); it isn't a point adjustment in the simulation yet —
  see the levers list in the dashboard (§07).
- `dashboard/week3_dashboard.html` — interactive dashboard: team ratings (real off/def split),
  feature importance, a QB report, per-matchup projections vs. market lines, validation (Week 2's
  full scorecard + an early Week 3 read), an injury report, and ranked improvement levers.
  Published version: https://claude.ai/artifact/UAHh6VMKw8rtVcrH2KXoMZ

Prior week's files (`model/week2_*`, `dashboard/week2_dashboard.html`, `model/calibrate_market_blend.py`,
`model/calibrate_qb_layer.py`, `model/validate_week2.py`) are kept as-is — they're the validated
history the Week 3 build was calibrated against.

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
  above) and added depth-chart tiers (WR1, RB2, ...) from real 2025 season usage (targets/rush
  attempts, not PAA — see `model/tier_injuries.py` above for why value and role aren't the same
  thing here).

## QB layer calibration attempt (against Week 2, no change made)

`model/calibrate_qb_layer.py` grid-searches the QB layer's five hand-picked constants
(`REG_WEIGHT`, `RECENCY_BOOST`, `STABILIZE_CAP`, `TEAM_CHANGE_DISCOUNT`, `QB_ADJ_CAP`) against
Week 2's 16 actual results — 3,360 combinations, scored on margin MAE and straight-up accuracy.
Two findings, neither of which changed the production constants:

- **`RECENCY_BOOST` and `STABILIZE_CAP` don't affect any prediction.** They only shape
  `blended_paa` — the number behind each QB's Elite/Average/Replacement-Level tier badge on the
  dashboard. The actual `qb_adj` fed into the simulation is `REG_WEIGHT × (2025 per-game PAA −
  this game's PAA)`, capped, which never references either constant. So of the five "tunable"
  constants the README used to list together, only three (`REG_WEIGHT`, `TEAM_CHANGE_DISCOUNT`,
  `QB_ADJ_CAP`) actually move a spread; the other two are display-only. Worth deciding deliberately
  whether `qb_adj` *should* use the recency-weighted blend instead of the raw hot/cold gap — that's
  a real design question, not something this calibration pass should just decide by fitting 16
  games.
- **The achievable MAE range across all 3,360 combinations is 11.96–12.24 pts** — a 0.28-pt spread,
  against a baseline MAE around 12.1. That's noise, not signal: the QB adjustment is capped small
  (≤1.2 pt/game by default) and mostly nets out across 16 games, so there's nothing in this sample
  that distinguishes the current constants from most of the grid. The current values (`REG_WEIGHT
  =0.11`, `TEAM_CHANGE_DISCOUNT=0.5`, `QB_ADJ_CAP=1.2`) sit in the middle of that flat range, not
  meaningfully worse than the in-sample "best" — which itself is driven almost entirely by a single
  game (Cooper Rush, the only team-change case in Week 2) and isn't a real answer, the same
  small-sample-overfit caveat `calibrate_market_blend.py` already documents for the blend weight.

No constants were changed. Re-run `python3 model/calibrate_qb_layer.py` once Week 3 (or more
weeks) are validated — a wider actual sample, and more team-change cases than just one, is what
would make this exercise trustworthy rather than descriptive.

## Injury point-adjustment: blocked on data completeness, not methodology

The snap-count file supplies exactly the missing piece flagged in every earlier version of this
README: real games-played and per-game usage, finally letting a season-total PAA gap convert into
a per-game point value the way the QB layer already works. The methodology is ready. It isn't
wired in because the data isn't complete enough to trust yet:

- `data/sis_player_rundef_2026_thru_wk2.csv` and `sis_player_passrush_2026_thru_wk2.csv` are both
  capped at exactly 200 rows, and `sis_rushing_2026_thru_wk2.csv` at 93 — round numbers that look
  like an export limit, not a natural stats cutoff (the rushing file's minimum is 5 attempts through
  2 games, far below what a starting back would have). Real, unambiguous starters are missing
  entirely from the 2026-to-date files as a result: Myles Garrett, Micah Parsons, and Josh Jacobs
  all have zero 2026 record in any of these tables, despite obviously playing every week.
- Checked against the 59 injury entries §06 already tags with a depth-chart tier, only **14 (24%)**
  have any 2026-to-date value record to compute a real per-game number from. Building the
  adjustment now would silently skip three-quarters of tagged injuries, and the misses aren't
  random — they skew toward exactly the highest-snap, most-established players, which is backwards
  for a lever whose whole point is pricing a real starter going down.

Needed to unblock: complete (non-truncated) `Run_Defense_2026`, `Pass_Rush_2026`, and confirmation
that `Rushing_2026` covers every back with real carries, not just the top ~93 by some other sort.
Once that lands, `qb_adj`-style per-game point values for CB/S/LB/DE/DT/RB are a mechanical
extension of code that already exists (`tier_injuries.py`'s tiering + this file's games-played) —
this is a data gap, not an engineering one.

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
