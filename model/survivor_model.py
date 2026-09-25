import csv, importlib.util, json, math, os, sys
from scipy.optimize import linear_sum_assignment
from scipy.stats import norm

HERE = os.path.dirname(os.path.abspath(__file__))

# --- Reuse the live composite ratings (this week's build) as the season-long team-strength half
# of the blend. It's a single-week snapshot, not a preseason projection, but it's the most
# current, validated signal this project has, and the user chose to blend it with market win
# totals rather than either alone.
spec = importlib.util.spec_from_file_location("week3_ratings_model", os.path.join(HERE, "week3_ratings_model.py"))
w3 = importlib.util.module_from_spec(spec)
_stdout = sys.stdout
sys.stdout = open(os.devnull, "w")
spec.loader.exec_module(w3)
sys.stdout = _stdout

COMP = {t: w3.TEAMS[t]["comp"] for t in w3.TEAMS}
HFA = w3.HFA
BASE_MARGIN_SD = w3.BASE_MARGIN_SD

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

ALREADY_USED = {1: "Jacksonville Jaguars", 2: "San Francisco 49ers"}
ALL_TEAMS = sorted(COMP.keys())

def tier(p):
    return "Very Safe" if p >= 0.80 else "Safe" if p >= 0.68 else "Moderate" if p >= 0.55 else "Risky"

def load_week3_overrides():
    # Week 3 already has a fully-built model (real market lines, QB adjustment, and the injury
    # point-adjustment) -- use its win probabilities instead of the coarse season-long blend for
    # that one week, since it's strictly more information than a composite+win-total estimate.
    try:
        with open(os.path.join(HERE, "week3_model_output.json")) as f:
            d = json.load(f)
    except FileNotFoundError:
        return {}
    overrides = {}
    for r in d["results_market_blended"]:
        overrides[r["home"]] = dict(opponent=r["away"], is_home=True, p_blend=r["win_home"] / 100,
                                     p_comp=None, p_mkt=None, source="week3_model")
        overrides[r["away"]] = dict(opponent=r["home"], is_home=False, p_blend=r["win_away"] / 100,
                                     p_comp=None, p_mkt=None, source="week3_model")
    return overrides

def build_week_options(games_by_week):
    # week -> {team: dict(opponent, is_home, p_blend, p_comp, p_mkt)}
    options = {}
    week3_overrides = load_week3_overrides()
    for wk, games in games_by_week.items():
        if wk == 3 and week3_overrides:
            options[wk] = week3_overrides
            continue
        opts = {}
        for g in games:
            pb_h, pc_h, pm_h = blended_win_prob(g["home"], g["away"], True)
            pb_a, pc_a, pm_a = blended_win_prob(g["away"], g["home"], False)
            opts[g["home"]] = dict(opponent=g["away"], is_home=True, p_blend=pb_h, p_comp=pc_h, p_mkt=pm_h, source="composite+wintotal")
            opts[g["away"]] = dict(opponent=g["home"], is_home=False, p_blend=pb_a, p_comp=pc_a, p_mkt=pm_a, source="composite+wintotal")
        options[wk] = opts
    return options

def optimize(start_week=3, end_week=18):
    games_by_week = load_schedule()
    options = build_week_options(games_by_week)
    used_already = set(ALREADY_USED.values())
    available_teams = [t for t in ALL_TEAMS if t not in used_already]
    weeks = list(range(start_week, end_week + 1))

    INFEASIBLE = 1e6
    cost = [[INFEASIBLE] * len(available_teams) for _ in weeks]
    for i, wk in enumerate(weeks):
        for j, team in enumerate(available_teams):
            if team in options.get(wk, {}):
                p = options[wk][team]["p_blend"]
                cost[i][j] = -math.log(max(p, 1e-6))

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

    survival_prob = 1.0
    for p in plan:
        if p.get("p_blend"):
            survival_prob *= p["p_blend"]

    # Per-team view: for every team, every week 3-18 they play, ranked best matchup first --
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
    # Combine with the two already-clinched weeks (assumed won, or this exercise wouldn't be live)
    print(f"(Weeks 1-2 already used: Jacksonville Jaguars, San Francisco 49ers -- assumed already won)")

    out = dict(
        already_used=[dict(week=wk, team=t) for wk, t in ALREADY_USED.items()],
        plan=plan,
        survival_prob=round(survival_prob, 6),
        team_schedule=team_schedule,
        season_win_totals=SEASON_WIN_TOTALS,
        composite_ratings={t: round(v, 1) for t, v in COMP.items()},
        generated_note="Weeks 4-18 blend this week's composite power ratings with 2026 season win "
                        "totals (50/50); Week 3 uses the fully-built model (real market lines, QB "
                        "and injury adjustments). Full-season optimization (assignment problem, "
                        "not greedy) maximizes total survival probability across all 16 remaining "
                        "weeks at once.",
    )
    with open(os.path.join(HERE, "survivor_plan.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nWrote {os.path.join(HERE, 'survivor_plan.json')}")
