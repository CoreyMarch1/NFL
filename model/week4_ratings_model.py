import random, statistics, json, math, os, csv

HERE = os.path.dirname(os.path.abspath(__file__))

random.seed(42)

# ============================================================================
# Week 4 build status -- what's fresh vs. carried forward stale this round:
#   - Composite ratings below: FRESH (Week 4 blended composite via @SamHoppen,
#     sourced from the user, itself built on ESPN/nfelo/Inpredictable/
#     Unexpected Points/FTN/PFF through Week 3 results).
#   - Schedule (MATCHUPS): FRESH (Week 4 slate).
#   - Inpredictable input to the composite: FRESH (Oct 4 betting-market GPF
#     replaces the composite's older Inpredictable snapshot; comp/sd recomputed).
#   - Off/def split: FRESH -- Inpredictable's market-derived dGPF, replacing the
#     SIS DataHub split that was stuck at Week 2 data.
#   - QB layer: STARTERS is FRESH (real Week 4 starters, confirmed by the user --
#     three changes from Week 3: Bears, Buccaneers, Seahawks). The underlying
#     performance data (QB_2025 / QB_2026_YTD) is still STALE -- through Week 2
#     only, and the three changed starters have no entry in either table, so
#     their qb_adj falls back to 0.0 (no fabricated numbers).
#   - Injury adjustments: STALE -- reusing week3_injury_adjustments.json
#     unchanged; no refreshed Week 4 injury report was available.
#   - Market lines (VEGAS): FRESH for 11 of 15 games (user-supplied sportsbook
#     screenshots, spread/total/moneyline). Washington@Indianapolis,
#     Chicago@NY Jets, Cincinnati@Jacksonville, and Tampa Bay@Green Bay have
#     no line sourced and run on the model's own margin with no market blend.
# This was an explicit user-requested tradeoff (partial/best-effort update
# now rather than waiting on fresh data uploads) -- see injury_point_adjustment.py
# and week3_ratings_model.py for the full methodology these levers implement.
# ============================================================================

# Team, Composite, StdDev, FPI, nfelo, Inpredictable, UnexpectedPoints, FTN_DVOA, PFF
# Week 4 composite ratings (via @SamHoppen), updated from Week 3.
TEAMS = {
"Buffalo Bills":        dict(comp=5.8,  sd=0.7, fpi=4.5,  nfelo=5.9,  inpred=6.1,  up=6.4,  dvoa=6.0,  pff=6.0),
"Seattle Seahawks":     dict(comp=5.4,  sd=0.6, fpi=4.8,  nfelo=4.9,  inpred=5.2,  up=5.9,  dvoa=5.4,  pff=6.2),
"San Francisco 49ers":  dict(comp=5.4,  sd=1.5, fpi=7.3,  nfelo=4.2,  inpred=3.7,  up=5.9,  dvoa=6.9,  pff=4.4),
"Los Angeles Rams":     dict(comp=5.3,  sd=0.7, fpi=4.1,  nfelo=5.4,  inpred=4.8,  up=5.8,  dvoa=6.0,  pff=5.9),
"Kansas City Chiefs":   dict(comp=4.3,  sd=0.4, fpi=4.8,  nfelo=4.2,  inpred=3.8,  up=4.8,  dvoa=4.1,  pff=4.2),
"Baltimore Ravens":     dict(comp=4.0,  sd=0.6, fpi=3.7,  nfelo=4.8,  inpred=3.6,  up=4.6,  dvoa=3.2,  pff=4.4),
"Jacksonville Jaguars": dict(comp=3.3,  sd=0.9, fpi=4.6,  nfelo=3.0,  inpred=2.7,  up=4.3,  dvoa=2.9,  pff=2.5),
"Detroit Lions":        dict(comp=2.7,  sd=0.3, fpi=2.4,  nfelo=2.7,  inpred=2.8,  up=3.2,  dvoa=2.9,  pff=2.3),
"Cincinnati Bengals":   dict(comp=1.9,  sd=1.0, fpi=1.9,  nfelo=3.1,  inpred=2.6,  up=2.3,  dvoa=1.5,  pff=0.3),
"Dallas Cowboys":       dict(comp=1.9,  sd=1.1, fpi=3.4,  nfelo=2.1,  inpred=1.1,  up=2.0,  dvoa=2.3,  pff=0.3),
"Denver Broncos":       dict(comp=1.8,  sd=0.7, fpi=0.8,  nfelo=2.2,  inpred=2.6,  up=1.5,  dvoa=1.4,  pff=2.3),
"Houston Texans":       dict(comp=1.6,  sd=0.9, fpi=0.6,  nfelo=1.9,  inpred=1.5,  up=0.8,  dvoa=2.9,  pff=2.1),
"New England Patriots": dict(comp=1.0,  sd=1.5, fpi=0.2,  nfelo=1.7,  inpred=0.4,  up=3.0,  dvoa=-1.3, pff=2.0),
"Philadelphia Eagles":  dict(comp=0.9,  sd=1.2, fpi=-0.8, nfelo=1.9,  inpred=1.2,  up=-0.4, dvoa=1.2,  pff=2.2),
"Minnesota Vikings":    dict(comp=0.8,  sd=0.9, fpi=0.7,  nfelo=2.4,  inpred=0.6,  up=0.7,  dvoa=-0.4, pff=1.0),
"Chicago Bears":        dict(comp=-0.3, sd=1.4, fpi=-1.2, nfelo=-0.8, inpred=-2.1, up=1.6,  dvoa=1.0,  pff=-0.1),
"Los Angeles Chargers": dict(comp=-0.4, sd=0.7, fpi=-0.7, nfelo=0.1,  inpred=-0.2, up=-0.5, dvoa=-1.6, pff=0.4),
"Green Bay Packers":    dict(comp=-0.5, sd=1.2, fpi=-0.9, nfelo=-0.2, inpred=0.9,  up=0.4,  dvoa=-2.5, pff=-0.8),
"Indianapolis Colts":   dict(comp=-1.1, sd=1.0, fpi=-1.1, nfelo=-0.1, inpred=-1.6, up=-1.2, dvoa=0.0,  pff=-2.8),
"Pittsburgh Steelers":  dict(comp=-1.3, sd=0.9, fpi=-2.4, nfelo=-0.2, inpred=-2.2, up=-0.8, dvoa=-1.7, pff=-0.4),
"Carolina Panthers":    dict(comp=-1.7, sd=1.0, fpi=-2.0, nfelo=-1.4, inpred=-2.4, up=0.3,  dvoa=-2.4, pff=-2.2),
"Las Vegas Raiders":    dict(comp=-2.2, sd=0.4, fpi=-2.1, nfelo=-2.1, inpred=-2.8, up=-2.7, dvoa=-2.1, pff=-1.6),
"New Orleans Saints":   dict(comp=-2.4, sd=1.3, fpi=-1.1, nfelo=-1.5, inpred=-1.7, up=-2.3, dvoa=-4.7, pff=-3.3),
"Atlanta Falcons":      dict(comp=-2.8, sd=1.4, fpi=-3.5, nfelo=-2.2, inpred=-2.8, up=-4.6, dvoa=-3.1, pff=-0.5),
"Washington Commanders":dict(comp=-3.2, sd=1.5, fpi=-2.3, nfelo=-2.5, inpred=-5.6, up=-1.4, dvoa=-3.1, pff=-4.2),
"New York Jets":        dict(comp=-3.4, sd=0.8, fpi=-3.3, nfelo=-3.5, inpred=-3.4, up=-3.6, dvoa=-2.1, pff=-4.7),
"Arizona Cardinals":    dict(comp=-4.0, sd=1.6, fpi=-4.7, nfelo=-4.4, inpred=-2.9, up=-4.6, dvoa=-1.4, pff=-6.1),
"New York Giants":      dict(comp=-5.0, sd=1.9, fpi=-7.1, nfelo=-2.7, inpred=-5.7, up=-6.0, dvoa=-6.0, pff=-2.6),
"Tampa Bay Buccaneers": dict(comp=-5.0, sd=1.4, fpi=-6.9, nfelo=-4.7, inpred=-3.3, up=-3.9, dvoa=-4.9, pff=-6.3),
"Tennessee Titans":     dict(comp=-5.5, sd=0.5, fpi=-5.5, nfelo=-4.9, inpred=-6.0, up=-5.9, dvoa=-4.7, pff=-5.7),
"Cleveland Browns":     dict(comp=-5.9, sd=0.8, fpi=-5.2, nfelo=-5.2, inpred=-6.2, up=-6.4, dvoa=-7.1, pff=-5.4),
"Miami Dolphins":       dict(comp=-8.1, sd=1.0, fpi=-8.2, nfelo=-7.9, inpred=-7.9, up=-8.9, dvoa=-6.4, pff=-9.3),
}

AVG_PTS = 22.5   # league-average team points/game baseline used for off/def decomposition

# ============================================================================
# Inpredictable betting-market ratings (as of Oct 4, 2026). Inpredictable is
# already one of the composite's six inputs, so its fresh GPF REPLACES the older
# snapshot in the composite rather than being added as a seventh source (which
# would double-count it). The published composite reproduces exactly as the plain
# mean of its six sources (sd = sample sd), so recomputing it with one input
# swapped is the same formula the vendor uses. `comp_published` keeps the original.
# ============================================================================
INPRED_CSV = os.path.join(HERE, "..", "data", "inpredictable_gpf_2026-10-04.csv")
SOURCES = ["fpi", "nfelo", "inpred", "up", "dvoa", "pff"]
with open(INPRED_CSV) as f:
    INPRED = {r["Team"]: r for r in csv.DictReader(f)}
assert set(INPRED) == set(TEAMS), "Inpredictable team names must match TEAMS exactly"

for t, d in TEAMS.items():
    d["comp_published"], d["inpred_published"] = d["comp"], d["inpred"]
    d["inpred"] = float(INPRED[t]["GPF"])
    vals = [d[s] for s in SOURCES]
    d["comp"], d["sd"] = statistics.mean(vals), statistics.stdev(vals)

# ============================================================================
# Offense/defense split (lever #3), now from Inpredictable's market-derived
# dGPF (the defensive share of a team's points-favored vs. an average opponent;
# + = defense saves points). This replaces the SIS DataHub run/pass-defense split
# used through Week 3 (see week3_ratings_model.py), which was stuck at Week 2
# data -- and checked against the 11 real Week 4 market totals, that stale split
# was off by 4.6 pts on average, worse than no split at all (4.1); dGPF is off by
# 1.0. Caveat: dGPF is itself built from betting markets, so agreeing with market
# totals is partly circular -- consistency, not proof. Actual Week 4 totals are
# the real test. See compare_def_split.py.
#
# def_rating (points allowed/game, lower=better) = AVG_PTS - dGPF
# off_rating is the residual of the composite identity comp = off - def, as before.
# ============================================================================
def decompose(team):
    dfn = AVG_PTS - float(INPRED[team]["dGPF"])
    off = TEAMS[team]["comp"] + dfn
    return off, dfn

for t in TEAMS:
    o, f = decompose(t)
    TEAMS[t]["off"], TEAMS[t]["def"] = o, f

# ---- Feature importance: correlation of each submetric with the composite ----
def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs)/n, sum(ys)/n
    cov = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    vx = sum((x-mx)**2 for x in xs)
    vy = sum((y-my)**2 for y in ys)
    return cov / math.sqrt(vx*vy)

metrics = ["fpi", "nfelo", "inpred", "up", "dvoa", "pff"]
comp_vals = [TEAMS[t]["comp"] for t in TEAMS]
importance = {}
for m in metrics:
    mvals = [TEAMS[t][m] for t in TEAMS]
    corr = pearson(mvals, comp_vals)
    mae = sum(abs(TEAMS[t][m]-TEAMS[t]["comp"]) for t in TEAMS)/len(TEAMS)
    importance[m] = dict(corr=round(corr,3), mae_vs_composite=round(mae,3))

# ---- Monte Carlo simulation engine ----
HFA = 2.0
BASE_MARGIN_SD = 13.0
UNCERTAINTY_K = 1.4
BASE_TOTAL_SD = 9.5
N_ITERS = 5000

def simulate(home, away, home_qb_adj=0.0, away_qb_adj=0.0, market_home_spread=None, model_weight=1.0,
             home_off_injury_adj=0.0, home_def_injury_adj=0.0, away_off_injury_adj=0.0, away_def_injury_adj=0.0):
    ho = TEAMS[home]["off"] + home_qb_adj + home_off_injury_adj
    hd = TEAMS[home]["def"] + home_def_injury_adj
    ao = TEAMS[away]["off"] + away_qb_adj + away_off_injury_adj
    ad = TEAMS[away]["def"] + away_def_injury_adj
    hsd, asd = TEAMS[home]["sd"], TEAMS[away]["sd"]

    # off_injury_adj is added to "off" the same way qb_adj is, so it moves margin 1:1; a
    # def_injury_adj raises "def" (points allowed, lower = better), which moves margin the
    # opposite way -- both terms are exactly what falls out of expressing model_margin as
    # (ho-hd)-(ao-ad)+HFA, which is algebraically identical to the composite-based line below.
    model_margin = ((TEAMS[home]["comp"] - TEAMS[away]["comp"]) + HFA
                    + (home_qb_adj - away_qb_adj)
                    + (home_off_injury_adj - away_off_injury_adj)
                    - (home_def_injury_adj - away_def_injury_adj))
    if market_home_spread is not None:
        # Blend the model's own margin with the market-implied margin BEFORE simulating, so the
        # blend shapes win probability and the CIs too, not just the reported median spread.
        market_margin = -market_home_spread
        expected_margin = model_weight*model_margin + (1-model_weight)*market_margin
    else:
        expected_margin = model_margin
    combined_margin_sd = math.sqrt(BASE_MARGIN_SD**2 + (UNCERTAINTY_K*(hsd+asd))**2)
    # Matchup-aware total: each side's expected points = its own offense blended with the
    # opponent's defense (points allowed), not just its own offense in isolation.
    expected_home_pts = ho + ad - AVG_PTS
    expected_away_pts = ao + hd - AVG_PTS
    expected_total = expected_home_pts + expected_away_pts
    total_sd = math.sqrt(BASE_TOTAL_SD**2 + (UNCERTAINTY_K*0.6*(hsd+asd))**2)

    margins, home_scores, away_scores = [], [], []
    for _ in range(N_ITERS):
        m = random.gauss(expected_margin, combined_margin_sd)
        tot = max(20.0, random.gauss(expected_total, total_sd))
        hs = max(0.0, (tot+m)/2)
        as_ = max(0.0, (tot-m)/2)
        margins.append(hs-as_)
        home_scores.append(hs)
        away_scores.append(as_)

    margins.sort()
    def pct(p):
        idx = min(len(margins)-1, max(0, int(p*len(margins))))
        return margins[idx]

    median_margin = statistics.median(margins)
    win_home = sum(1 for m in margins if m > 0) / len(margins)
    win_home += 0.5*sum(1 for m in margins if m == 0)/len(margins)

    confidence = round(min(99, abs(win_home-0.5)*2*100))

    return dict(
        home=home, away=away,
        home_off=round(ho,1), home_def=round(hd,1),
        away_off=round(ao,1), away_def=round(ad,1),
        model_margin=round(model_margin,1),
        expected_margin=round(expected_margin,1),
        median_margin=round(median_margin,1),
        ci68=(round(pct(0.16),1), round(pct(0.84),1)),
        ci95=(round(pct(0.025),1), round(pct(0.975),1)),
        win_home=round(win_home*100,1),
        win_away=round((1-win_home)*100,1),
        confidence=confidence,
        proj_home_score=round(statistics.mean(home_scores),1),
        proj_away_score=round(statistics.mean(away_scores),1),
        combined_sd=round(combined_margin_sd,2),
    )

# Week 4 slate. Pittsburgh Steelers @ Cleveland Browns already played Thursday
# 10/1 -- its result isn't available in this session (no live data access), so
# it's excluded from MATCHUPS entirely rather than guessed at. Backfill it as a
# validation point, same as Week 3 did for GB/ATL, once the actual score is known.
MATCHUPS = [
    ("Washington Commanders", "Indianapolis Colts"),
    ("Baltimore Ravens", "Tennessee Titans"),
    ("Buffalo Bills", "New England Patriots"),
    ("Chicago Bears", "New York Jets"),
    ("Cincinnati Bengals", "Jacksonville Jaguars"),
    ("Houston Texans", "Dallas Cowboys"),
    ("New York Giants", "Arizona Cardinals"),
    ("Philadelphia Eagles", "Los Angeles Rams"),
    ("Tampa Bay Buccaneers", "Green Bay Packers"),
    ("Minnesota Vikings", "Miami Dolphins"),
    ("Las Vegas Raiders", "Kansas City Chiefs"),
    ("Seattle Seahawks", "Los Angeles Chargers"),
    ("San Francisco 49ers", "Denver Broncos"),
    ("Carolina Panthers", "Detroit Lions"),
    ("New Orleans Saints", "Atlanta Falcons"),
]
# tuple = (home, away)

# Week 4 market lines (spread/total/moneyline), via user-supplied sportsbook
# screenshots. 11 of the 15 games are covered; Washington@Indianapolis,
# Chicago@NY Jets, Cincinnati@Jacksonville, and Tampa Bay@Green Bay have no
# line sourced and fall back to the model's own margin (simulate() treats
# market_home_spread=None as "use model_margin").
VEGAS = {
    ("San Francisco 49ers","Denver Broncos"):     dict(home_spread=-2.5, total=47.5, home_ml=-148, away_ml=126),
    ("Carolina Panthers","Detroit Lions"):        dict(home_spread=3.5,  total=50.5, home_ml=172,  away_ml=-205),
    ("New Orleans Saints","Atlanta Falcons"):     dict(home_spread=-2.5, total=47.5, home_ml=-132, away_ml=112),
    ("Houston Texans","Dallas Cowboys"):          dict(home_spread=-3.0, total=48.5, home_ml=-158, away_ml=134),
    ("Minnesota Vikings","Miami Dolphins"):       dict(home_spread=-9.5, total=38.5, home_ml=-510, away_ml=390),
    ("Las Vegas Raiders","Kansas City Chiefs"):   dict(home_spread=4.5,  total=47.5, home_ml=180,  away_ml=-215),
    ("Seattle Seahawks","Los Angeles Chargers"):  dict(home_spread=-7.0, total=43.5, home_ml=-370, away_ml=295),
    ("Philadelphia Eagles","Los Angeles Rams"):   dict(home_spread=3.5,  total=42.5, home_ml=162,  away_ml=-194),
    ("New York Giants","Arizona Cardinals"):      dict(home_spread=2.5,  total=44.5, home_ml=118,  away_ml=-138),
    ("Buffalo Bills","New England Patriots"):     dict(home_spread=-6.5, total=49.5, home_ml=-340, away_ml=275),
    ("Baltimore Ravens","Tennessee Titans"):      dict(home_spread=-11.5,total=42.5, home_ml=-750, away_ml=530),
}

def ml_to_prob(ml):
    if ml is None:
        return None
    return -ml/(-ml+100) if ml < 0 else 100/(ml+100)

# ============================================================================
# QB layer: STALE this week. STARTERS, QB_2025 and QB_2026_YTD are all
# carried forward unchanged from the Week 3 build -- no refreshed Week 3 SIS
# DataHub QB tables were available this session, so qb_adj values here still
# reflect each team's QB form through Week 2, not Week 3. See
# week3_ratings_model.py / calibrate_qb_layer.py for the original methodology.
# ============================================================================
STARTERS = {
    "Carolina Panthers": ("Bryce Young", False), "Atlanta Falcons": ("Michael Penix Jr.", False),
    "New Orleans Saints": ("Tyler Shough", False), "Baltimore Ravens": ("Lamar Jackson", False),
    "Minnesota Vikings": ("Kyler Murray", False), "Chicago Bears": ("Tyson Bagent", True),
    "Cincinnati Bengals": ("Joe Burrow", False), "Houston Texans": ("C.J. Stroud", False),
    "Pittsburgh Steelers": ("Aaron Rodgers", False), "New England Patriots": ("Drake Maye", False),
    "Green Bay Packers": ("Jordan Love", False), "New York Jets": ("Geno Smith", False),
    "Cleveland Browns": ("Deshaun Watson", False), "Tampa Bay Buccaneers": ("Jalon Daniels", True),
    "Philadelphia Eagles": ("Jalen Hurts", False), "Tennessee Titans": ("Cam Ward", False),
    "Jacksonville Jaguars": ("Trevor Lawrence", False), "Denver Broncos": ("Bo Nix", False),
    "Las Vegas Raiders": ("Kirk Cousins", False), "Los Angeles Chargers": ("Justin Herbert", False),
    "Seattle Seahawks": ("Sam Darnold", False), "Arizona Cardinals": ("Jacoby Brissett", False),
    "Washington Commanders": ("Marcus Mariota", True), "Dallas Cowboys": ("Dak Prescott", False),
    "Miami Dolphins": ("Malik Willis", False), "San Francisco 49ers": ("Brock Purdy", False),
    "Indianapolis Colts": ("Daniel Jones", False), "Kansas City Chiefs": ("Patrick Mahomes", False),
    "New York Giants": ("Jameis Winston", True), "Los Angeles Rams": ("Matthew Stafford", False),
    "Buffalo Bills": ("Josh Allen", False), "Detroit Lions": ("Jared Goff", False),
}
# Week 4 starters as confirmed by the user (real, not carried forward). Three changes from the
# Week 3 build: Chicago (Case Keenum -> Tyson Bagent), Tampa Bay (Baker Mayfield -> Jalon Daniels,
# a backup/rookie now starting), and Seattle (Drew Lock -> Sam Darnold, who's back as the starter,
# no longer a backup). Bagent, Daniels, and Darnold all have no entry in QB_2025 or QB_2026_YTD
# below (no 2025 baseline was collected for any of them, and no 2026-to-date SIS data exists yet
# for the two new backups) -- build_qb_profile's "no-data" branch handles this correctly: qb_adj
# falls back to 0.0 rather than fabricating a number, same treatment the injury layer gives an
# absent player.
# Combines passing AND rushing production (SIS DataHub). name -> (games, pass_att,
# pass_PAA_season_total, rush_att, rush_PAA_season_total, 2025 team)
QB_2025 = {
    "Bo Nix": (17, 612, 61.94, 83, -7.13, "Broncos"), "Matthew Stafford": (17, 597, 55.99, 29, -8.75, "Rams"),
    "Caleb Williams": (17, 568, 45.63, 77, -8.36, "Bears"), "Jared Goff": (17, 578, 38.96, 19, -4.24, "Lions"),
    "Patrick Mahomes": (14, 502, 45.90, 64, 5.56, "Chiefs"), "Jordan Love": (15, 439, 42.92, 47, 5.11, "Packers"),
    "Dak Prescott": (17, 600, 19.71, 53, 5.55, "Cowboys"), "Jalen Hurts": (16, 454, 26.44, 105, -14.70, "Eagles"),
    "C.J. Stroud": (14, 423, 32.99, 48, 0.57, "Texans"), "Drake Maye": (17, 492, 18.25, 103, -3.81, "Patriots"),
    "Bryce Young": (16, 478, 16.00, 54, 10.65, "Panthers"), "Trevor Lawrence": (17, 560, 3.40, 82, 13.44, "Jaguars"),
    "Jacoby Brissett": (13, 485, 7.96, 38, -0.27, "Cardinals"), "Josh Allen": (16, 460, 6.24, 112, 21.64, "Bills"),
    "Brock Purdy": (9, 284, 27.77, 33, 1.02, "49ers"), "Daniel Jones": (13, 384, 6.59, 45, -1.01, "Colts"),
    "Justin Herbert": (16, 512, -14.01, 83, 3.47, "Chargers"), "Tyler Shough": (11, 327, 10.30, 45, 0.25, "Saints"),
    "Baker Mayfield": (17, 543, -19.24, 55, 32.35, "Buccaneers"), "Aaron Rodgers": (16, 498, -18.72, 21, -5.90, "Steelers"),
    "Jaxson Dart": (13, 339, 3.16, 86, 3.84, "Giants"), "Lamar Jackson": (13, 302, -6.33, 67, 8.58, "Ravens"),
    "Joe Burrow": (8, 259, 6.83, 14, -2.47, "Bengals"), "Jayden Daniels": (7, 188, 6.60, 58, 7.54, "Commanders"),
    "Cam Ward": (17, 540, -48.66, 39, 2.63, "Titans"), "Carson Wentz": (5, 169, -11.41, 11, 2.38, "Vikings"),
    "Kirk Cousins": (10, 269, 3.96, 14, -4.14, "Falcons"), "Geno Smith": (15, 448, -69.04, 41, -5.23, "Raiders"),
    "Cooper Rush": (3, 52, 5.77, 4, -0.46, "Ravens"),
    "Michael Penix Jr.": (9, 276, 5.24, 21, -2.33, "Falcons"),
    "Kyler Murray": (5, 161, 10.83, 29, 7.06, "Cardinals"),
}
# name -> (2026 pass_att through Wk2, pass_PAA_total through Wk2, rush_att through Wk2, rush_PAA_total through Wk2)
QB_2026_YTD = {
    "Jayden Daniels": (51, 17.85, 12, 6.72), "Dak Prescott": (65, 12.77, 6, 0.77),
    "Jared Goff": (77, 10.79, 5, -0.72), "Brock Purdy": (56, 11.57, 8, 1.09),
    "Drew Lock": (48, 7.93, 0, 0.0), "Josh Allen": (60, 6.11, 20, -1.79),
    "Geno Smith": (65, 5.90, 11, 2.57), "Caleb Williams": (55, 6.83, 15, 0.30),
    "Kirk Cousins": (59, 5.95, 9, -1.23), "Bryce Young": (73, 3.25, 0, 0.0),
    "Patrick Mahomes": (74, 4.27, 9, 2.97), "Matthew Stafford": (56, 4.27, 6, -0.51),
    "Jalen Hurts": (62, 2.89, 12, 0.11), "Joe Burrow": (66, 2.27, 6, -0.12),
    "Cam Ward": (52, 2.12, 8, 3.25), "Jacoby Brissett": (65, 0.01, 7, -0.55),
    "Malik Willis": (50, 0.21, 8, -0.61), "Jaxson Dart": (34, 4.16, 11, -0.30),
    "Tyler Shough": (90, -2.26, 13, 3.07), "Lamar Jackson": (56, -0.92, 11, 5.29),
    "Marcus Mariota": (16, 3.87, 0, 0.0), "Bo Nix": (59, -3.60, 8, -0.65),
    "Trevor Lawrence": (52, -2.04, 0, 0.0), "Drake Maye": (55, -3.47, 11, 0.19),
    "Daniel Jones": (62, -4.38, 0, 0.0), "C.J. Stroud": (93, -6.27, 5, -0.82),
    "Jameis Winston": (27, -2.04, 0, 0.0), "Deshaun Watson": (52, -6.73, 13, 7.37),
    "Jordan Love": (71, -9.28, 0, 0.0), "Justin Herbert": (54, -7.57, 8, -3.22),
    "Cooper Rush": (39, -24.10, 0, 0.0), "Carson Wentz": (39, -8.47, 8, 2.32),
    "Aaron Rodgers": (79, -12.53, 0, 0.0), "Kyler Murray": (5, -3.37, 0, 0.0),
    "Baker Mayfield": (62, -10.73, 9, 4.71),
}
GAMES_2026 = 2   # elapsed through Week 2 -- data not refreshed past this
STABILIZE_CAP, RECENCY_BOOST = 450, 5.0
REG_WEIGHT, TEAM_CHANGE_DISCOUNT, QB_ADJ_CAP = 0.11, 0.5, 1.2

def build_qb_profile(team):
    name, is_backup = STARTERS[team]
    d25, d26 = QB_2025.get(name), QB_2026_YTD.get(name)
    team_change = bool(d25 and d25[5] not in team)
    total26_pg = (d26[1]+d26[3])/GAMES_2026 if d26 else None   # pass PAA + rush PAA, per game
    if d25 and total26_pg is not None:
        games25, patt25, ppaa25, ratt25, rpaa25 = d25[0], d25[1], d25[2], d25[3], d25[4]
        ppg25 = (ppaa25+rpaa25)/games25
        w25 = min(patt25+ratt25, STABILIZE_CAP)
        w26 = (d26[0]+d26[2])*RECENCY_BOOST
        blended = (ppg25*w25 + total26_pg*w26) / (w25+w26)
        hot_cold = round(total26_pg-ppg25, 2)
        w = TEAM_CHANGE_DISCOUNT if team_change else 1.0
        qb_adj = max(-QB_ADJ_CAP, min(QB_ADJ_CAP, w*REG_WEIGHT*(ppg25-total26_pg)))
        quality = "team-change" if team_change else "full"
        paa25_out = round(ppg25, 2)
    elif total26_pg is not None:
        blended, hot_cold, qb_adj, quality, paa25_out = total26_pg, None, 0.0, "no-2025-baseline", None
    elif d25:
        games25, patt25, ppaa25, ratt25, rpaa25 = d25[0], d25[1], d25[2], d25[3], d25[4]
        ppg25 = (ppaa25+rpaa25)/games25
        blended, hot_cold, qb_adj, quality = ppg25, None, 0.0, "no-2026-games-yet"
        paa25_out = round(ppg25, 2)
    else:
        blended, hot_cold, qb_adj, quality, paa25_out = None, None, 0.0, "no-data", None
    return dict(team=team, name=name, is_backup=is_backup, paa2025=paa25_out,
                paa2026=round(total26_pg,2) if total26_pg is not None else None,
                blended_paa=round(blended,2) if blended is not None else None,
                hot_cold_delta=hot_cold, qb_adj=round(qb_adj,2), data_quality=quality)

qb_profiles = {team: build_qb_profile(team) for team in STARTERS}
_vals = sorted(p["blended_paa"] for p in qb_profiles.values() if p["blended_paa"] is not None)
def _tier(v):
    if v is None: return "Unrated"
    pct = _vals.index(v)/(len(_vals)-1) if len(_vals) > 1 else 0.5
    return "Elite" if pct>=0.8 else "Above Average" if pct>=0.6 else "Average" if pct>=0.4 else "Below Average" if pct>=0.2 else "Replacement Level"
for p in qb_profiles.values():
    p["tier"] = _tier(p["blended_paa"])

results = []
for home, away in MATCHUPS:
    r = simulate(home, away)
    v = VEGAS.get((home, away))
    if v:
        r["vegas_home_spread"] = v["home_spread"]
        r["vegas_total"] = v["total"]
        r["model_home_spread"] = -r["median_margin"]
        r["edge_pts"] = round(r["model_home_spread"] - v["home_spread"], 1)
        hp, ap = ml_to_prob(v["home_ml"]), ml_to_prob(v["away_ml"])
        if hp is not None:
            overround = hp + ap
            r["vegas_win_home"] = round(hp/overround*100, 1)
            r["vegas_win_away"] = round(ap/overround*100, 1)
            r["win_prob_edge"] = round(r["win_home"] - r["vegas_win_home"], 1)
    results.append(r)

results_qb = []
for home, away in MATCHUPS:
    hq = qb_profiles[home]["qb_adj"]
    aq = qb_profiles[away]["qb_adj"]
    r = simulate(home, away, home_qb_adj=hq, away_qb_adj=aq)
    v = VEGAS.get((home, away))
    r["home_qb_adj"], r["away_qb_adj"] = hq, aq
    if v:
        r["vegas_home_spread"] = v["home_spread"]
        r["model_home_spread"] = -r["median_margin"]
        r["edge_pts"] = round(r["model_home_spread"] - v["home_spread"], 1)
    results_qb.append(r)

# ============================================================================
# Non-QB injuries (lever #2): STALE this week. Reusing week3_injury_adjustments.json
# unchanged -- no refreshed Week 4 injury report was available this session, so
# any injury news since the Week 3 report (returns, new injuries) isn't reflected.
# See injury_point_adjustment.py for the full methodology.
# ============================================================================
try:
    with open(os.path.join(HERE, "week3_injury_adjustments.json")) as f:
        INJURY_ADJ = json.load(f)
except FileNotFoundError:
    INJURY_ADJ = {}

def injury_adj(team):
    a = INJURY_ADJ.get(team, {})
    return a.get("off_adj", 0.0), a.get("def_adj", 0.0)

results_injury = []
for home, away in MATCHUPS:
    hq, aq = qb_profiles[home]["qb_adj"], qb_profiles[away]["qb_adj"]
    hoi, hdi = injury_adj(home)
    aoi, adi = injury_adj(away)
    r = simulate(home, away, home_qb_adj=hq, away_qb_adj=aq,
                 home_off_injury_adj=hoi, home_def_injury_adj=hdi,
                 away_off_injury_adj=aoi, away_def_injury_adj=adi)
    v = VEGAS.get((home, away))
    r["home_qb_adj"], r["away_qb_adj"] = hq, aq
    r["home_off_injury_adj"], r["home_def_injury_adj"] = hoi, hdi
    r["away_off_injury_adj"], r["away_def_injury_adj"] = aoi, adi
    if v:
        r["vegas_home_spread"] = v["home_spread"]
        r["model_home_spread"] = -r["median_margin"]
        r["edge_pts"] = round(r["model_home_spread"] - v["home_spread"], 1)
    results_injury.append(r)

# ============================================================================
# Market blend (lever #1): a no-op this week -- VEGAS is empty (no current
# lines sourced), so market_spread is None for every game and simulate()
# falls back to the model's own margin everywhere. VALIDATED_GAMES now
# includes Week 3 (validate_week3.py, run against user-supplied final
# scores): 16 from Week 2 + 15 from Week 3 = 31. This has no effect on this
# week's output (no market lines to blend against), but keeps the constant
# honest for whenever Week 5 actually has lines to blend.
# ============================================================================
VALIDATED_GAMES = 31
BLEND_STABILIZE_K = 64
MODEL_WEIGHT = min(0.5, VALIDATED_GAMES / (VALIDATED_GAMES + BLEND_STABILIZE_K))

results_blended = []
for home, away in MATCHUPS:
    hq, aq = qb_profiles[home]["qb_adj"], qb_profiles[away]["qb_adj"]
    hoi, hdi = injury_adj(home)
    aoi, adi = injury_adj(away)
    v = VEGAS.get((home, away))
    market_spread = v["home_spread"] if v else None
    r = simulate(home, away, home_qb_adj=hq, away_qb_adj=aq,
                 home_off_injury_adj=hoi, home_def_injury_adj=hdi,
                 away_off_injury_adj=aoi, away_def_injury_adj=adi,
                 market_home_spread=market_spread, model_weight=MODEL_WEIGHT)
    r["home_qb_adj"], r["away_qb_adj"] = hq, aq
    r["home_off_injury_adj"], r["home_def_injury_adj"] = hoi, hdi
    r["away_off_injury_adj"], r["away_def_injury_adj"] = aoi, adi
    r["model_weight"] = MODEL_WEIGHT
    if v:
        r["vegas_home_spread"] = v["home_spread"]
        r["vegas_total"] = v["total"]
        r["model_home_spread"] = -r["median_margin"]
        r["edge_pts"] = round(r["model_home_spread"] - v["home_spread"], 1)
    results_blended.append(r)

out = dict(importance=importance, results=results, results_qb_adjusted=results_qb,
           results_injury_adjusted=results_injury,
           results_market_blended=results_blended, model_weight=MODEL_WEIGHT,
           qb_profiles=qb_profiles, injury_adjustments=INJURY_ADJ,
           teams={t: dict(comp=round(TEAMS[t]["comp"],2), sd=round(TEAMS[t]["sd"],2),
                           comp_published=TEAMS[t]["comp_published"],
                           inpred_published=TEAMS[t]["inpred_published"], inpred_gpf=TEAMS[t]["inpred"],
                           off=round(TEAMS[t]["off"],1), defr=round(TEAMS[t]["def"],1))
                  for t in TEAMS},
           stale_inputs=dict(
               qb_performance="through Week 2 only (starters themselves are confirmed Week 4)",
               injuries="Week 3 report, reused unchanged",
               market_lines="11 of 15 games sourced; WAS-IND, CHI-NYJ, CIN-JAX, TB-GB missing"))

with open(os.path.join(HERE, "week4_model_output.json"),"w") as f:
    json.dump(out, f, indent=2)

print(f"{'Away @ Home':50s} {'Base spread':>12s} {'QB-adj spread':>14s} {'Shift':>7s}")
for r, rq in zip(results, results_qb):
    base_sp = -r['median_margin']
    qb_sp = -rq['median_margin']
    print(f"{r['away']:22s} @ {r['home']:22s} {base_sp:>+12.1f} {qb_sp:>+14.1f} {qb_sp-base_sp:>+7.1f}")
