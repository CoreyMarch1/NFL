# NFL Composite Ratings Model

A team rating and game-projection system built on the weekly composite power ratings (FPI,
nfelo, Inpredictable, Unexpected Points, FTN DVOA, PFF; data via @SamHoppen). Now on **Week 5
(partial update)** — composite ratings (with an Oct 7 Inpredictable refresh), the off/def split
(Oct 7 dGPF), schedule, QB starters, and all 15 market lines are fresh; QB performance stats and
injuries are carried forward and flagged (see below). Weeks 2–4 files are kept alongside as the validated history everything since has
been checked against.

## Contents (current: Week 5 — partial update)

- `model/week5_ratings_model.py` → `model/week5_model_output.json` — the Week 4 pipeline on the
  **fresh Week 5 composite** (via @SamHoppen; transcription checksummed — every team's composite
  and sd reproduce from its six sources) and the **Week 5 slate** (15 games; Chiefs and Panthers on
  bye). The composite's Inpredictable input is refreshed to Inpredictable's **Oct 7** betting-market
  GPF (`data/inpredictable_gpf_2026-10-07.csv`; checksummed: oGPF + dGPF = GPF for all 32 teams,
  every rank column consistent, league W-L balances at 64–64), the same in-place swap as Week 4.
  It's newer than the composite's own column: its two biggest gaps from it are the Ravens (−2.9,
  Huntley starting) and Commanders (+1.3, Daniels back), so the refresh is how the market's read of
  this week's QB changes reaches the ratings — the QB layer gives both changed starters a neutral
  0.0, so nothing is double-counted. Biggest composite move: Ravens −0.5. The off/def split uses the
  same Oct 7 dGPF.
  **Starters are user-confirmed for Week 5**, with two changes from Week 4: Baltimore to backup
  Tyler Huntley (which explains the Ravens' −3.5 composite move) and Jayden Daniels back for
  Washington. Buffalo and Detroit weren't on the list and keep Allen and Goff. **Returning starters
  get a neutral 0.0 QB adjustment** (`RETURNING_STARTERS`): the adjustment regresses a starter's
  recent form toward his 2025 baseline on the premise that the team rating already contains that
  form, which fails once the rating has been built on the backup's games. Applied mechanically it
  would have marked Washington *down* 1.13 pts for Daniels' return. The Bears' +6.6 move in their
  betting-market Inpredictable rating has no starter change behind it (Bagent still starts) and is
  unexplained — the Oct 7 data confirms the market really did move them from 24th to 7th. Carried
  forward and flagged: QB performance numbers (through Week 2) and injuries (Week 3 report; the dashboard drops
  any QB entry that's now a confirmed starter, i.e. Daniels). **Market lines** (user-supplied
  sportsbook screenshots) cover all 15 games and are blended at `VALIDATED_GAMES = 46` →
  46/(46+64) ≈ 42% model / 58% market. Six games show a pure-model gap of 2+ pts vs. the market.
  The biggest is Broncos @ Chargers (model Chargers by 0.6, market Broncos by 3.5 — possibly the
  flat 2-pt home field overrating the Chargers' shared stadium). **Two of the next three are this
  week's QB changes**: Giants @ Commanders (model Giants by 0.2, market Washington by 3.5 —
  Daniels back) and Ravens @ Falcons (model Falcons by 0.9, market by 3.5 — Huntley starting).
  Both changed starters get a neutral 0.0 QB adjustment, so the market's read reaches the model
  only via Inpredictable's one-sixth share of the composite: honest given the data, but it means
  the model systematically under-reacts to QB changes. Fixing that needs per-QB value data for
  backups. Bears @ Packers (model Packers by 0.5, market Bears by 2.5) has no starter change behind
  it. Model totals sit within 1.5 pts of the market's on average. The dashboard's "Model vs. market ≥ 2 pts" filter now uses the pure-model
  gap; it used the blended gap, which the 58% market weight keeps under ~1.7, so it never fired.
- `dashboard/week5_dashboard.html` — the Week 4 dashboard rebuilt on Week 5 output, with §05 still
  showing the Week 4 scorecard as the most recent completed validation.
  Published version: https://claude.ai/artifact/EPi2dgTdiLaeRHsW5Dbkzs

## Week 4 build (partial update)

- `model/week4_ratings_model.py` → `model/week4_model_output.json` — same pipeline as the Week 3
  build (below), run on **fresh Week 4 composite ratings** (via @SamHoppen), the **fresh Week 4
  schedule** (15 active matchups; Pittsburgh @ Cleveland already played Thursday 10/1 and is
  excluded, since its result wasn't available this session), and **real, user-confirmed Week 4
  starters** — three changes from Week 3: Chicago (Tyson Bagent), Tampa Bay (Jalon Daniels, a
  backup/rookie starting for an injured Baker Mayfield), and Seattle (Sam Darnold, back from
  injury and no longer a backup). None of those three have a 2025 or 2026 production record, so
  their QB adjustment falls back to 0.0 rather than a fabricated number. **Real market lines**
  (spread/total/moneyline, user-supplied sportsbook screenshots) are wired in for 11 of the 15
  games, blended at `31/(31+64)` ≈ 33% model / 67% market — the other 4 (Washington–Indianapolis,
  Chicago–NY Jets, Cincinnati–Jacksonville, Tampa Bay–Green Bay) have no line sourced and run on
  the pure model view. **Inpredictable's betting-market ratings** (Oct 4) feed in two ways — see
  "Inpredictable betting-market ratings" below. What's still a **deliberate, flagged gap**: every
  QB's underlying performance numbers are still through Week 2, and the injury adjustments reuse
  `week3_injury_adjustments.json` unchanged. This was an explicit user-requested tradeoff (ship a
  partial update now, on gameday, rather than wait for fresh data, then layer in real starters,
  lines, and ratings as they came in) — see the model file's own header comment for the itemized
  fresh-vs-stale breakdown.
- `data/inpredictable_gpf_2026-10-04.csv` — Inpredictable's NFL Betting Market Rankings as of Oct
  4, 2026, transcribed from a user-supplied screenshot. Includes GPF, oGPF, dGPF, record, playoff
  odds, and past/future strength of schedule. Transcription is checksummed: oGPF + dGPF = GPF
  within rounding for all 32 teams, and every rank column agrees with its values.
- `model/compare_def_split.py` — reproduces the off/def split comparison and the composite-refresh
  bound check described below.
- `model/validate_week4.py` → `model/week4_validation_output.json` — scores the Week 4 projections
  (as committed before kickoff) against final scores, compares against the market on the 11 lined
  games only, and tests each off/def split against actual totals. See "Week 4 validation" below.
- `model/validate_week3.py` → `model/week3_validation_output.json` — scores all four Week 3 model
  stages against final scores (via user-supplied ESPN scoreboard screenshots). See "Week 3
  validation" below.
- `dashboard/week4_dashboard.html` — same dashboard as Week 3's, rebuilt against the Week 4 output,
  with every section that relies on stale inputs (QB report, injury report) explicitly labeled as
  carried-forward rather than silently reused. Trend is computed directly from the Week 3→4
  composite change. §05 now shows Week 3's real 15-game validation (see below) instead of Week 2's.
  Published version: https://claude.ai/artifact/XH7aRoAQyNMrGQXsB4RiFS

## Inpredictable betting-market ratings (Week 4)

Inpredictable's GPF ("Generic Points Favored") is what a team would be favored by against a
league-average opponent on a neutral field, backed out of betting lines. oGPF/dGPF split it into
offense and defense. **Inpredictable is already one of the composite's six sources**, so it isn't
added as a seventh input, which would double-count it. It's used two ways instead:

1. **Composite refresh.** The published composite reproduces exactly as the plain mean of its six
   sources (sd = sample sd), and the composite's Inpredictable column is the same metric as GPF
   (r = 0.98), just an older snapshot. So the model swaps in the Oct 4 GPF and recomputes the
   mean. Each team moves by a sixth of its Inpredictable change, at most ~0.3 pts (biggest: Jets,
   Bears, Saints down; Texans, Cowboys up). `comp_published` is kept in the output for comparison.
2. **Offense/defense split.** Defense = league average − dGPF; offense stays the residual of
   composite = offense − defense. This replaces the SIS DataHub run/pass-defense split, which was
   stuck at Week 2 data. Against the 11 real Week 4 market totals:

   | Split | Total-points MAE vs. market |
   |---|---|
   | SIS run+pass defense (thru Wk2) | 4.62 pt |
   | No split at all | 4.17 pt |
   | **Inpredictable dGPF** | **1.02 pt** |

   The stale SIS split was worse than no split at all. **Caveat:** dGPF is itself built from
   betting markets, so agreeing with market totals is partly circular. It shows consistency with
   the market, not proven accuracy, and actual Week 4 totals are the real test. The split only
   affects projected totals; spreads come from the composite.

Not used as model inputs: playoff odds (an output of the same ratings, not new information) and
past/future strength of schedule. The composite's sources already adjust for opponent strength,
and the survivor tool works from the actual schedule rather than an SOS summary. Both are kept
in the CSV.

## Week 3 build (v0.4, full update)

- `model/week3_ratings_model.py` — decomposes each team's composite rating into a **real**
  offense/defense split (SIS DataHub run-defense + pass-defense data; offense is the residual of
  the vendor's own composite = offense − defense identity), blends each Week 3 starting QB's 2025
  season form with their 2026 season-to-date into a capped points-per-game adjustment, applies the
  non-QB injury point adjustment (`model/injury_point_adjustment.py`'s output), shrinks the
  resulting margin toward the market line (weight grows as more weeks get validated), and runs a
  5,000-iteration Monte Carlo simulation for all 15 active Week 3 matchups at each stage — base,
  QB-adjusted, injury-adjusted, and market-blended (spread, win probability, 68%/95% confidence
  intervals, a confidence score).
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
  receiving file and the injury report's own listed position.
- `model/injury_point_adjustment.py` → `model/week3_injury_adjustments.json` — prices every tiered
  injury into a real per-team offense/defense point adjustment, fed into `week3_ratings_model.py`'s
  simulation alongside the QB layer. See "Injury point-adjustment (implemented)" below.
- `model/convert_snap_counts.py` → `data/nfl_snap_counts_2026_thru_wk2.csv` — per-player,
  per-game snap counts for 2026 Weeks 1-2 (a one-time ingestion script; needs `openpyxl` to read
  the source `.xlsx`, unlike everything else here, which stays standard-library-only). This is the
  games-played/usage denominator the injury lever needed — see "Injury point-adjustment
  (implemented)" below for how it's used. `TeamId` and `PositionId` in the source file are numeric
  codes with no legend; both were reverse-engineered by
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
- **Full-league injury report** parsed, tiered, and now priced into a real point adjustment
  (dashboard §06, feeding the simulation alongside the QB layer) — see "Injury point-adjustment
  (implemented)" below. Also fixed a duplicate-data bug in the parser (Washington was showing 159
  "injuries" instead of 4 — see `model/parse_injuries.py` above) and added depth-chart tiers (WR1,
  RB2, ...) from real 2025 season usage (targets/rush attempts, not PAA — see
  `model/tier_injuries.py` above for why value and role aren't the same thing here).

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

## Injury point-adjustment (implemented)

`model/injury_point_adjustment.py` turns every §06 injury with a depth-chart tier into an actual
point adjustment, now applied inside the simulation alongside the QB layer. This closes the lever
flagged as open since the tiering was first built.

**What resolved the earlier "missing data" concern:** `Run_Defense_2026` and `Pass_Rush_2026` being
capped at exactly 200 rows, and `Rushing_2026` at 93, isn't a truncation bug — per SIS, a player
absent from all three genuinely hasn't had a meaningful 2026 impact. Myles Garrett (traded to the
Rams in the offseason, played Week 1, then got hurt with negligible stats) confirmed this: he's
correctly absent, not incorrectly cut off. The methodology treats "no 2026 record" as
**replacement-level (0.0)**, not "unknown" — which is the right prior for someone who hasn't been
a real factor this season, whether hurt, suspended, or just buried on the depth chart.

**Method**, mirroring the QB layer's PAA-per-game logic:
1. For each tagged injury, find the next **healthy** player *below* them on the same 2025-usage
   depth chart (§06's tier order) — not the team's best available player at that position overall.
   An early version of this compared a hurt RB3 against the team's actual starting RB1 (who's
   unaffected and already playing); fixed by searching downward from the injured player's own
   rank, and tracking already-assigned replacements so simultaneous injuries at the same position
   don't double up on the same fill-in.
2. Price the swap as the gap in 2026-to-date points-per-game (2026 PAA total ÷ real games played,
   from the new snap-count file) between the injured player and their replacement.
3. Cap each player-swap at ±1.0 pt, then cap the summed offense-side and defense-side adjustment
   per team at ±2.0 pt each — smaller than the QB layer's ±1.2 cap since these are secondary
   players on a noisier 2-game sample.
4. Feed the result into `simulate()` exactly like `qb_adj`: an offense-side adjustment moves a
   team's own scoring, a defense-side adjustment moves their points allowed, and both flow through
   to margin, total, and the market blend consistently (the math is `model_margin = (ho−hd)−(ao−ad)
   + HFA`, so anything added to `ho`/`hd` has to enter the margin formula the same way — this is
   spelled out in the `simulate()` docstring-comment now).

**The load-bearing assumption, worth stating plainly:** treating an unproven/absent backup as
league-average (0.0) is generous for many real backups and can make an injury to a *below-average*
starter look like a net positive (their replacement, presumed average, looks better than they did)
— this happened for a couple of teams in the Week 3 output and is a real property of the method,
not a bug. Re-examine once a real replacement-level baseline (rather than 0.0) is available.

Re-run `python3 model/injury_point_adjustment.py` after `tier_injuries.py` any time the injury
report or 2026-to-date value files change, then re-run `week3_ratings_model.py` to pick it up.

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

## Week 3 final

Thursday's game: **Falcons 35, Packers 14**. The model (run with Cooper Rush still the presumed
Falcons QB, since Penix's return wasn't yet reflected pre-kickoff) favored Green Bay by 6 —
Michael Penix Jr.'s return plus a 194-yard, 2-TD game from Bijan Robinson blew that out by 27
points, exactly the kind of in-game swing (a QB return, a breakout rushing day) a rating-based
model has no way to see coming. It was never in `MATCHUPS` (already final before the Week 3 build
ran), so it isn't part of the 15-game scorecard below.

## Week 3 validation (final, 15/15)

`model/validate_week3.py`, scored against final scores the user supplied via ESPN scoreboard
screenshots:

| | Margin MAE | Straight-up |
|---|---|---|
| Base model (no QB/injury adj.) | 7.31 pt | 7/15 (47%) |
| QB-adjusted model | 7.27 pt | 7/15 (47%) |
| QB+injury-adjusted model | **7.01 pt** | **8/15 (53%)** |
| Market-blended model | 7.13 pt | 8/15 (53%) |
| Closing market line | 7.27 pt | 8/15 (53%) |

Every model stage matched or trailed a coin flip on straight-up picks, same as the market. Margin
MAE (7.0–7.3 pt) looks better than Week 2's (11.8–12.3 pt), but that's **not evidence of
improvement** — it's one 15-game week against one 16-game week, and the lower MAE here is mostly
driven by having fewer extreme misses in aggregate, not better-calibrated typical games. The
QB+injury-adjusted stage edged out every other stage on both measures, a small, plausible signal
in favor of those two levers (not yet a proven one with a 15-game sample).

The week's real story is two blowouts the model had nowhere close: the model favored **Chicago by
only 4.1** over Philadelphia (actual: Bears 27, Eagles 7, a 20-pt margin) and **Jacksonville by
only 2.6** over New England (actual: Jaguars 35, Patriots 6, a 29-pt margin). Both were
straight-up hits — the model had the right side — but the two margin misses (24.1 pt and 26.4 pt)
account for more than a third of the week's total error between them, which is exactly the
failure mode a composite-rating model with no in-game context will keep having: it can't see a
blowout coming, only a lean.

`VALIDATED_GAMES` (feeding the market-blend weight, lever #1) is now **31** (16 from Week 2 + 15
from Week 3), moving the blend weight to `31/(31+64)` ≈ 33% model / 67% market for whenever a
future week has market lines to blend against — Week 4 itself has none sourced, so this has no
effect on this week's output, just keeps the constant honest for Week 5 onward.

## Week 4 validation (final, 15/15)

`model/validate_week4.py`, scored against final scores the user supplied via ESPN scoreboard
screenshots. The projections scored are exactly the ones committed before the first kickoff (Oct 4,
9:05 AM ET, ahead of the 9:30 London game) — the Week 4 model was not rerun or retuned first.
Thursday's Browns 27, Steelers 24 isn't scored (already final before the build ran). Four games
had no market line, so market comparisons use only the other 11:

| 11 games with a line | Margin MAE | Straight-up | Total-points MAE |
|---|---|---|---|
| Base model | **7.15 pt** | **7/11** | 10.45 pt |
| QB+injury-adjusted | 7.43 pt | 7/11 | 10.55 pt |
| Market-blended (33% model) | 7.55 pt | 6/11 | 10.47 pt |
| Closing market | 7.59 pt | 6/11 | **9.95 pt** |

Across all 15 games the market-blended model scored 7.30 pt MAE and 9/15 straight-up (base model:
7.12, 10/15). The biggest miss was one the market shared exactly: **Falcons 45, Saints 24**, with
both the model and the line at Saints −2.5 (23.5 pt error). Blending toward the market made the
model slightly worse this week after helping in Week 3 — noise at this sample size, not a reason
to retune.

**Weeks 3–4 combined (26 out-of-sample games with a line):** every model stage lands at 7.2–7.3 pt
margin MAE vs. 7.40 for the closing market, and 14–15 of 26 straight-up vs. 14 for the market.
Market-level, no demonstrated edge, and far too few games to separate the two.

**The real test of the Inpredictable off/def split.** Week 4 switched to dGPF because it matched
the *market's* totals far better (1.0 vs. 4.6 pt) — a partly circular check. Against **actual**
totals:

| Split | All 15 games | 11 lined games | Bias |
|---|---|---|---|
| Inpredictable dGPF | **9.50 pt** | 10.46 pt | −2.5 |
| SIS run+pass defense (thru Wk2) | 10.06 pt | 10.63 pt | −1.6 |
| No split | 10.71 pt | 12.10 pt | −2.5 |
| Market total | — | **9.95 pt** | |

The switch helped, but modestly — the market-totals check overstated the gain — and the market's
own totals still did better. Every split ran low: Week 4 scored more than projected (Falcons–Saints
69, Cowboys–Texans 64, Cardinals–Giants 60). Totals remain the model's weakest output; candidates
for the Week 5 build are a higher league-scoring baseline than `AVG_PTS = 22.5` or blending the
market total into projected totals the same way the spread is already blended into margins.

**For the Week 5 build:** `VALIDATED_GAMES` should be 46 (16 + 15 + 15), moving the market-blend
weight to 46/(46+64) ≈ 42% model / 58% market. (Week 4's own model keeps 31 — changing it now would
retroactively alter the projections that were just scored.)

## Secondary tool: Survivor pool roadmap

A separate, full-season tool for NFL survivor pools (pick one team per week to win outright; the
same team can never be picked twice; one loss or tie and you're out). Given three picks already
spent and won — Jacksonville Jaguars (Week 1), San Francisco 49ers (Week 2), and Kansas City Chiefs
(Week 3, beat Miami 24–10) — it recommends which of the remaining 29 teams to pick in each of
Weeks 4–18. **Current Week 4 pick: Minnesota Vikings vs. Miami (77.6%)**, with an estimated 2.1%
chance of surviving all of Weeks 4–18.

- `model/survivor_model.py` → `model/survivor_plan.json` — for every future matchup, blends this
  week's composite rating (from `week{CURRENT_WEEK}_ratings_model.py`, now including the Oct 4
  Inpredictable refresh) with each team's 2026 season win total (a September sportsbook consensus,
  researched separately) 50/50. The current week itself uses the fully-built weekly model instead
  (market lines where sourced, QB and injury adjustments — strictly more information than the blend
  has for any other week); a game that's already been played (Week 4's Thursday Steelers–Browns)
  isn't offered. Advancing a week means bumping `CURRENT_WEEK` and adding the last pick to
  `ALREADY_USED`. Then, instead of greedily taking the best team each week, solves a
  weeks-by-teams assignment problem (`scipy.optimize.linear_sum_assignment`) that picks one
  distinct team per week to maximize the *product* of every remaining week's win probability at once — the
  correct objective for "maximize the odds of surviving the whole season," and the reason a team
  can look like a strong pick in one week's alternatives while the plan actually saves them for a
  tougher week later. Needs `scipy`, unlike the weekly model.
- `data/nfl_2026_schedule.csv` — the full 2026 regular-season schedule (converted from the
  uploaded `.xlsx`), every team's opponent and home/away for all 18 weeks.
- `dashboard/survivor_roadmap.html` — the published roadmap: a week-by-week pick with a
  confidence tier, alternatives on request, a "close calls to watch" list (weeks below "Very
  Safe"), a **pick finder** (choose any team, see every remaining week they play ranked best
  matchup first — each row shows whether the current plan already uses that team that week, or
  which team it uses instead, with a button to slot them in), and the same transparency about
  assumptions and blind spots as the main dashboard. Every week's pick can be **overridden** from
  its own dropdown: the rest of the season re-optimizes live around the forced pick (a client-side
  port of the same assignment-problem solver used to build the plan), and a **reset** button
  restores the original optimal plan exactly, with no re-solve. A **save** button stores the
  current set of overrides — persisted in the artifact's own database, so it's there next time
  anyone opens the link — and a saved-paths list lets you reload or delete them later. Saved paths
  show survival odds recomputed under the current ratings, not the number stored when saved, and
  any override for a week that's passed (or a team no longer playable that week) is dropped on load.
  Published version: https://claude.ai/artifact/YDVPUeuoXnxhY1JqgCawok

**Week 4 update.** Four picks changed from the Week 3 plan: Week 4 Bears → Vikings (Chicago is
starting backup Tyson Bagent and its rating dropped), Week 5 Bengals → Cowboys, Week 8 Cowboys →
Steelers, Week 12 Vikings → Bengals. Every week in the new plan clears 71%; the old plan's weakest
spot (Vikings vs. Falcons, Week 12, 66.7%) is gone. Weeks 4–18 survival moved from 2.09% to 2.13%.
Robustness check: the weekly model's Week 4 win probabilities run 2–5 points below what the
moneylines imply, so the plan was re-run with Week 4 priced straight off no-vig moneylines — same
Week 4 pick and no other week changed. Using the Ravens this week instead (82% vs. Tennessee) costs
the season overall (2.0% vs. 2.1%), since the plan saves them for Week 16 against Cleveland; they'd
only be worth spending now if their Week 4 win probability were about 8 points higher.

**What this can't see:** weekly injury reports, starter changes, and market-line movement for any
week past the current one — the composite rating is held static at this week's snapshot for the
whole season rather than re-derived weekly. Re-run `survivor_model.py` each week as the picture
updates; the assignment re-optimizes the *remaining* weeks around whatever's actually true by then,
which is why the plan is a living document, not a one-time answer.
