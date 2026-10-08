import csv, importlib.util, json, math, os, sys
from scipy.optimize import linear_sum_assignment
from scipy.stats import norm

HERE = os.path.dirname(os.path.abspath(__file__))

# --- Reuse the live composite ratings (this week's build) as the season-long team-strength half
# of the blend. It's a single-week snapshot, not a preseason projection, but it's the most
# current, validated signal this project has, and the user chose to blend it with market win
# totals rather than either alone.
CURRENT_WEEK = 5   # the next week to pick; its probabilities come from that week's full model

spec = importlib.util.spec_from_file_location("ratings_model", os.path.join(HERE, f"week{CURRENT_WEEK}_ratings_model.py"))
rm = importlib.util.module_from_spec(spec)
_stdout = sys.stdout
sys.stdout = open(os.devnull, "w")
spec.loader.exec_module(rm)
sys.stdout = _stdout

COMP = {t: rm.TEAMS[t]["comp"] for t in rm.TEAMS}
HFA = rm.HFA
BASE_MARGIN_SD = rm.BASE_MARGIN_SD

# --- 2026 season win totals (market consensus), used as the second half of the blend. A
# season-long number smooths out the single-week noise a composite snapshot can carry, and
# reflects information (roster construction, schedule strength as the market sees it) the
# composite alone doesn't capture the same way.
SEASON_WIN_TOTALS = {
    "Baltimore Ravens": 11.5, "Los Angeles Rams": 11.5,
    "Buffalo Bills": 10.5, "Cincinnati Bengals": 10.5, "Kansas City Chiefs": 10.5,
    "Philadelphia Eagles": 10.5, "Seattle Seahawks": 10.5, "Detroit Lions": 10.5,
    "San Francisco 49ers": 10.5,
    "New England Patriots": 9.5, "Green Bay Packers": 9.5, "Los Angeles Chargers": 9.5,
    "Houston Texans": 9.5, "Chicago Bears": 9.5, "Dallas Cowboys": 9.5, "Denver Broncos": 9.5,
    "Jacksonville Jaguars": 8.5, "Pittsburgh Steelers": 8.5, "Minnesota Vikings": 8.5,
    "Indianapolis Colts": 7.5, "New York Giants": 7.5, "Washington Commanders": 7.5,
    "Tampa Bay Buccaneers": 7.5, "Atlanta Falcons": 7.5, "New Orleans Saints": 7.5,
    "Tennessee Titans": 6.5, "Carolina Panthers": 6.5,
    "New York Jets": 5.5, "Las Vegas Raiders": 5.5, "Cleveland Browns": 5.5,
    "Miami Dolphins": 4.5, "Arizona Cardinals": 4.5,
}
# Consensus of DraftKings/FanDuel/BetMGM/Fanatics as reported by FOX Sports, CBS Sports, ESPN,
# SI Betting, and Yahoo Sports; current as of mid-to-late September 2026 (post-Week 2/3 line
# movement, not the original February open). Sums to exactly 272 = 32 x 8.5, the season's total
# game count, confirming internal consistency across sources.

def load_schedule():
    games_by_week = {}
    with open(os.path.join(HERE, "..", "data", "nfl_2026_schedule.csv")) as f:
        for row in csv.DictReader(f):
            week = int(row["Week"])
            games_by_week.setdefault(week, []).append(
                dict(away=row["AwayTeam"], home=row["HomeTeam"], date=row["Date"]))
    return games_by_week

def p_win_composite(team, opp, is_home):
    margin = COMP[team] - COMP[opp] + (HFA if is_home else -HFA)
    sd = math.sqrt(BASE_MARGIN_SD**2)  # team-level SD term (UNCERTAINTY_K*(hsd+asd)) omitted --
    # no per-game QB/injury read exists this far out, so this is the base-rate uncertainty only.
    return norm.cdf(margin / sd)

# Bradley-Terry-style strength from a season win total: solve for a rating r_team such that,
# averaged against a league-average opponent (rating 0) at a neutral site, the corresponding
# win probability implies win_total/17 wins across a 17-game season. Uses the same margin/SD
# scale as the composite model so the two probabilities are on a comparable footing before
# averaging.
def rating_from_win_total(win_total, games=17):
    win_rate = min(0.97, max(0.03, win_total / games))
    z = norm.ppf(win_rate)
    return z * BASE_MARGIN_SD  # invert p = norm.cdf(rating/SD) at a neutral site

def p_win_markettotal(team, opp, is_home):
    if team not in SEASON_WIN_TOTALS or opp not in SEASON_WIN_TOTALS:
        return None
    r_team = rating_from_win_total(SEASON_WIN_TOTALS[team])
    r_opp = rating_from_win_total(SEASON_WIN_TOTALS[opp])
    margin = r_team - r_opp + (HFA if is_home else -HFA)
    return norm.cdf(margin / BASE_MARGIN_SD)

def blended_win_prob(team, opp, is_home):
    p_comp = p_win_composite(team, opp, is_home)
    p_mkt = p_win_markettotal(team, opp, is_home)
    if p_mkt is None:
        return p_comp, p_comp, None
    return (p_comp + p_mkt) / 2, p_comp, p_mkt

ALREADY_USED = {1: "Jacksonville Jaguars", 2: "San Francisco 49ers", 3: "Kansas City Chiefs", 4: "Minnesota Vikings"}
ALL_TEAMS = sorted(COMP.keys())

def tier(p):
    return "Very Safe" if p >= 0.80 else "Safe" if p >= 0.68 else "Moderate" if p >= 0.55 else "Risky"

def load_current_week_overrides():
    # The current week already has a fully-built model (market lines where sourced, QB adjustment,
    # injury point-adjustment) -- use its win probabilities instead of the coarse season-long blend
    # for that one week, since it's strictly more information than a composite+win-total estimate.
    # A game that's already been played (e.g. a Thursday game) isn't in the weekly model's slate,
    # so neither team is offered as a pick that week.
    try:
        with open(os.path.join(HERE, f"week{CURRENT_WEEK}_model_output.json")) as f:
            d = json.load(f)
    except FileNotFoundError:
        return {}
    overrides = {}
    for r in d["results_market_blended"]:
        overrides[r["home"]] = dict(opponent=r["away"], is_home=True, p_blend=r["win_home"] / 100,
                                     p_comp=None, p_mkt=None, source="weekly_model")
        overrides[r["away"]] = dict(opponent=r["home"], is_home=False, p_blend=r["win_away"] / 100,
                                     p_comp=None, p_mkt=None, source="weekly_model")
    return overrides

def build_week_options(games_by_week):
    # week -> {team: dict(opponent, is_home, p_blend, p_comp, p_mkt)}
    options = {}
    current_overrides = load_current_week_overrides()
    for wk, games in games_by_week.items():
        if wk == CURRENT_WEEK and current_overrides:
            options[wk] = current_overrides
            continue
        opts = {}
        for g in games:
            pb_h, pc_h, pm_h = blended_win_prob(g["home"], g["away"], True)
            pb_a, pc_a, pm_a = blended_win_prob(g["away"], g["home"], False)
            opts[g["home"]] = dict(opponent=g["away"], is_home=True, p_blend=pb_h, p_comp=pc_h, p_mkt=pm_h, source="composite+wintotal")
            opts[g["away"]] = dict(opponent=g["home"], is_home=False, p_blend=pb_a, p_comp=pc_a, p_mkt=pm_a, source="composite+wintotal")
        options[wk] = opts
    return options

def load_ownership():
    # Projected pool ownership for the current week (survivor_ownership.py), or None if missing.
    try:
        with open(os.path.join(HERE, f"survivor_ownership_week{CURRENT_WEEK}.json")) as f:
            d = json.load(f)
    except FileNotFoundError:
        return None
    return {t: v["share"] for t, v in d["projection"].items()} if d.get("week") == CURRENT_WEEK else None

def equity_multipliers(week_options, own):
    # If you pick team t and it wins, the share of the pool still alive is o_t + sum_{u!=t} o_u * p_u
    # (everyone on t survives with you; everyone else survives at their own team's win probability).
    # Your slice of the pool grows by 1 / that, so a win on a lightly-owned pick in a week where the
    # chalk might fall is worth more than the same win alongside most of the field.
    field = sum(o * week_options[u]["p_blend"] for u, o in own.items() if u in week_options)
    return {t: 1.0 / (field + own.get(t, 0.0) * (1 - week_options[t]["p_blend"])) for t in week_options}

def optimize(start_week=CURRENT_WEEK, end_week=18, mode="survival"):
    # mode="survival": maximize the probability of surviving every remaining week.
    # mode="ownership": same, except the current week is valued by p x equity multiplier -- expected
    # growth in your share of the pool -- using projected ownership. Only the current week can be
    # adjusted: ownership can't be projected further out, so later weeks stay pure survival, which is
    # also what keeps the plan saving strong teams for the weeks that need them.
    games_by_week = load_schedule()
    options = build_week_options(games_by_week)
    used_already = set(ALREADY_USED.values())
    available_teams = [t for t in ALL_TEAMS if t not in used_already]
    weeks = list(range(start_week, end_week + 1))
    own = load_ownership()
    mult = equity_multipliers(options[CURRENT_WEEK], own) if own else {}
    if mode == "ownership" and not own:
        raise ValueError(f"ownership mode needs survivor_ownership_week{CURRENT_WEEK}.json")

    INFEASIBLE = 1e6
    cost = [[INFEASIBLE] * len(available_teams) for _ in weeks]
    for i, wk in enumerate(weeks):
        for j, team in enumerate(available_teams):
            if team in options.get(wk, {}):
                p = options[wk][team]["p_blend"]
                cost[i][j] = -math.log(max(p, 1e-6))
                if mode == "ownership" and wk == CURRENT_WEEK:
                    cost[i][j] -= math.log(mult[team])

    row_ind, col_ind = linear_sum_assignment(cost)
    plan = []
    for i, j in sorted(zip(row_ind, col_ind)):
        wk = weeks[i]
        team = available_teams[j]
        c = cost[i][j]
        if c >= INFEASIBLE:
            plan.append(dict(week=wk, team=None, error="no feasible team found"))
            continue
        info = options[wk][team]
        # alternatives: best other teams for this week by raw win prob, regardless of the plan
        alts = sorted(
            ((t, o["p_blend"], o["opponent"], o["is_home"]) for t, o in options[wk].items()
             if t != team and t not in used_already),
            key=lambda x: -x[1])[:3]
        plan.append(dict(week=wk, team=team, opponent=info["opponent"], is_home=info["is_home"],
                          p_blend=round(info["p_blend"], 4),
                          p_comp=round(info["p_comp"], 4) if info["p_comp"] is not None else None,
                          p_mkt=round(info["p_mkt"], 4) if info["p_mkt"] is not None else None,
                          source=info["source"], tier=tier(info["p_blend"]),
                          alternatives=[dict(team=t, p_blend=round(p, 4), opponent=o, is_home=h) for t, p, o, h in alts]))
        if wk == CURRENT_WEEK and own:
            plan[-1].update(ownership=round(own.get(team, 0.0), 4), equity_mult=round(mult[team], 4))

    survival_prob = 1.0
    for p in plan:
        if p.get("p_blend"):
            survival_prob *= p["p_blend"]

    # Per-team view: for every team, every remaining week they play, ranked best matchup first --
    # "if I want to save this team, which weeks are worth it" independent of the single optimal
    # path above. Includes the already-used teams too (their remaining schedule is moot to pick,
    # but the UI can still show it labeled as unavailable rather than just omitting them).
    plan_week_by_team = {p["team"]: p["week"] for p in plan if p.get("team")}
    team_schedule = {}
    for team in ALL_TEAMS:
        rows = []
        for wk in weeks:
            info = options.get(wk, {}).get(team)
            if not info:
                continue  # bye week
            occupied_by = plan_week_by_team.get(team) == wk
            other_team_here = next((p["team"] for p in plan if p["week"] == wk and p.get("team") != team), None)
            rows.append(dict(week=wk, opponent=info["opponent"], is_home=info["is_home"],
                              p_blend=round(info["p_blend"], 4), tier=tier(info["p_blend"]),
                              is_plan_pick=occupied_by,
                              plan_uses_instead=None if occupied_by else other_team_here))
        rows.sort(key=lambda r: -r["p_blend"])
        team_schedule[team] = rows

    return plan, survival_prob, team_schedule

if __name__ == "__main__":
    plan, survival_prob, team_schedule = optimize()
    own = load_ownership()
    plan_own, survival_own, _ = optimize(mode="ownership") if own else (None, None, None)
    print(f"{'Wk':>3s} {'Team':26s} {'Opp':22s} {'H/A':4s} {'P(win)':>7s} {'Tier':10s} {'Top alt (p)'}")
    for p in plan:
        if p["team"] is None:
            print(f"{p['week']:>3d}  ERROR: {p['error']}")
            continue
        alt = p["alternatives"][0] if p["alternatives"] else None
        alt_str = f"{alt['team']} ({alt['p_blend']:.2f})" if alt else "-"
        print(f"{p['week']:>3d} {p['team']:26s} {p['opponent']:22s} {'vs' if p['is_home'] else '@':4s} "
              f"{p['p_blend']:>6.1%} {p['tier']:10s} {alt_str}")
    print(f"\nEstimated probability of surviving weeks {plan[0]['week']}-{plan[-1]['week']}: {survival_prob:.1%}")
    used = ", ".join(f"{t} (Wk{wk})" for wk, t in sorted(ALREADY_USED.items()))
    print(f"(Already used and won: {used})")
    if plan_own:
        changed = [(a["week"], a["team"], b["team"]) for a, b in zip(plan, plan_own) if a["team"] != b["team"]]
        print(f"\nOwnership-aware plan: survival {survival_own:.2%} (vs {survival_prob:.2%}); picks that differ: {changed or 'none'}")
        cw = plan_own[0]
        print(f"  Week {CURRENT_WEEK} pick: {cw['team']} -- win {cw['p_blend']:.1%}, projected ownership {cw['ownership']:.1%}, equity x{cw['equity_mult']:.3f}")

    out = dict(
        already_used=[dict(week=wk, team=t) for wk, t in sorted(ALREADY_USED.items())],
        start_week=CURRENT_WEEK,
        plan=plan,
        survival_prob=round(survival_prob, 6),
        plan_ownership=plan_own,
        survival_prob_ownership=round(survival_own, 6) if survival_own else None,
        ownership={t: round(v, 4) for t, v in own.items()} if own else None,
        equity_mult=({t: round(v, 6) for t, v in equity_multipliers(build_week_options(load_schedule())[CURRENT_WEEK], own).items()}
                     if own else None),
        team_schedule=team_schedule,
        season_win_totals=SEASON_WIN_TOTALS,
        composite_ratings={t: round(v, 1) for t, v in COMP.items()},
        generated_note=f"Weeks {CURRENT_WEEK+1}-18 blend this week's composite power ratings with 2026 "
                        f"season win totals (50/50); Week {CURRENT_WEEK} uses the fully-built weekly "
                        "model (market lines where sourced, QB and injury adjustments). Full-season "
                        "optimization (assignment problem, not greedy) maximizes total survival "
                        "probability across all remaining weeks at once.",
    )
    with open(os.path.join(HERE, "survivor_plan.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nWrote {os.path.join(HERE, 'survivor_plan.json')}")
