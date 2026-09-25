import random, statistics, json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))

random.seed(42)

# Team, Composite, StdDev, FPI, nfelo, Inpredictable, UnexpectedPoints, FTN_DVOA, PFF
# Week 3 composite ratings (via @SamHoppen), updated from Week 2.
TEAMS = {
"Buffalo Bills":        dict(comp=5.8, sd=0.6, fpi=5.5, nfelo=5.8, inpred=5.2, up=5.2, dvoa=6.8, pff=6.1),
"Los Angeles Rams":     dict(comp=5.5, sd=0.6, fpi=4.7, nfelo=5.1, inpred=5.4, up=6.3, dvoa=6.0, pff=5.7),
"San Francisco 49ers":  dict(comp=4.9, sd=1.3, fpi=7.3, nfelo=3.7, inpred=4.2, up=4.6, dvoa=5.3, pff=4.2),
"Seattle Seahawks":     dict(comp=4.6, sd=1.1, fpi=3.0, nfelo=5.0, inpred=5.5, up=4.8, dvoa=3.6, pff=6.0),
"Baltimore Ravens":     dict(comp=3.9, sd=0.4, fpi=4.1, nfelo=3.8, inpred=3.7, up=4.4, dvoa=3.2, pff=4.0),
"Kansas City Chiefs":   dict(comp=3.9, sd=0.5, fpi=4.4, nfelo=3.3, inpred=4.4, up=4.3, dvoa=3.4, pff=3.8),
"New England Patriots": dict(comp=2.5, sd=1.1, fpi=1.9, nfelo=2.9, inpred=1.9, up=4.1, dvoa=0.9, pff=3.1),
"Philadelphia Eagles":  dict(comp=2.5, sd=1.6, fpi=1.6, nfelo=1.9, inpred=5.1, up=0.5, dvoa=2.5, pff=3.3),
"Detroit Lions":        dict(comp=2.0, sd=0.8, fpi=2.1, nfelo=2.3, inpred=0.6, up=3.2, dvoa=2.2, pff=1.9),
"Jacksonville Jaguars": dict(comp=2.0, sd=0.8, fpi=2.6, nfelo=0.9, inpred=2.5, up=2.9, dvoa=2.0, pff=1.4),
"Houston Texans":       dict(comp=1.9, sd=0.7, fpi=1.1, nfelo=1.7, inpred=2.5, up=1.1, dvoa=2.8, pff=1.9),
"Cincinnati Bengals":   dict(comp=1.8, sd=0.8, fpi=1.7, nfelo=2.2, inpred=2.9, up=2.0, dvoa=1.0, pff=0.9),
"Dallas Cowboys":       dict(comp=1.7, sd=1.0, fpi=3.0, nfelo=1.7, inpred=0.8, up=1.4, dvoa=2.8, pff=0.7),
"Denver Broncos":       dict(comp=1.6, sd=1.0, fpi=-0.3, nfelo=1.4, inpred=1.7, up=2.0, dvoa=2.2, pff=2.5),
"Minnesota Vikings":    dict(comp=0.6, sd=1.2, fpi=1.4, nfelo=1.7, inpred=1.5, up=-0.5, dvoa=-1.1, pff=0.8),
"Green Bay Packers":    dict(comp=0.0, sd=1.5, fpi=0.5, nfelo=0.6, inpred=-2.1, up=1.5, dvoa=-1.5, pff=1.3),
"Los Angeles Chargers": dict(comp=-0.5, sd=0.6, fpi=-1.3, nfelo=-0.6, inpred=-0.1, up=-0.2, dvoa=-1.3, pff=0.2),
"Chicago Bears":        dict(comp=-0.9, sd=2.3, fpi=-2.0, nfelo=-1.6, inpred=1.2, up=2.6, dvoa=-2.7, pff=-2.9),
"Tampa Bay Buccaneers": dict(comp=-1.0, sd=0.9, fpi=-1.1, nfelo=-1.0, inpred=-1.4, up=-0.4, dvoa=0.1, pff=-2.5),
"Indianapolis Colts":   dict(comp=-1.1, sd=1.0, fpi=-1.2, nfelo=-0.9, inpred=-1.4, up=-1.3, dvoa=0.7, pff=-2.5),
"Carolina Panthers":    dict(comp=-1.6, sd=0.6, fpi=-1.4, nfelo=-1.5, inpred=-2.1, up=-0.5, dvoa=-1.8, pff=-2.2),
"Pittsburgh Steelers":  dict(comp=-1.8, sd=0.8, fpi=-2.7, nfelo=-1.2, inpred=-2.2, up=-1.1, dvoa=-2.6, pff=-1.1),
"New Orleans Saints":   dict(comp=-2.3, sd=1.3, fpi=-0.6, nfelo=-2.0, inpred=-2.2, up=-1.8, dvoa=-4.7, pff=-2.4),
"Las Vegas Raiders":    dict(comp=-3.2, sd=0.5, fpi=-3.0, nfelo=-3.2, inpred=-3.5, up=-3.9, dvoa=-3.0, pff=-2.5),
"Washington Commanders":dict(comp=-3.2, sd=1.0, fpi=-3.5, nfelo=-3.7, inpred=-2.7, up=-1.4, dvoa=-3.6, pff=-4.1),
"New York Jets":        dict(comp=-3.9, sd=0.9, fpi=-3.2, nfelo=-4.8, inpred=-4.5, up=-4.0, dvoa=-2.3, pff=-4.3),
"Arizona Cardinals":    dict(comp=-4.3, sd=1.9, fpi=-5.2, nfelo=-6.0, inpred=-2.7, up=-4.8, dvoa=-1.4, pff=-5.9),
"New York Giants":      dict(comp=-4.3, sd=2.4, fpi=-8.3, nfelo=-3.1, inpred=-2.1, up=-4.8, dvoa=-5.5, pff=-2.3),
"Atlanta Falcons":      dict(comp=-4.8, sd=1.7, fpi=-5.3, nfelo=-4.3, inpred=-7.2, up=-5.3, dvoa=-4.8, pff=-1.9),
"Tennessee Titans":     dict(comp=-5.2, sd=0.8, fpi=-4.7, nfelo=-5.4, inpred=-4.1, up=-6.5, dvoa=-4.8, pff=-5.6),
"Cleveland Browns":     dict(comp=-6.3, sd=0.6, fpi=-6.2, nfelo=-6.2, inpred=-6.4, up=-6.2, dvoa=-7.4, pff=-5.4),
"Miami Dolphins":       dict(comp=-8.0, sd=0.9, fpi=-8.0, nfelo=-8.2, inpred=-8.3, up=-8.1, dvoa=-6.2, pff=-8.9),
}

AVG_PTS = 22.5   # league-average team points/game baseline used for off/def decomposition

# ============================================================================
# Real offense/defense split (lever #3), replacing the earlier synthetic
# 50/50-plus-tilt heuristic. Source: SIS DataHub team Run Defense and Pass
# Defense tables (2025 season + 2026 through Week 2; the "2026" team files run
# ~44-87 pass attempts against, roughly 2 games' worth, not 1, unlike the
# earlier per-QB Week-1-only files). Both are "Points Above Avg" (PAA) --
# positive = defense saves points relative to league average.
#
# Pass Rush data was also supplied but is intentionally NOT summed in here:
# a sack/pressure event that shows up in Pass Rush's own PAA also shows up in
# Pass Defense's overall EPA-allowed number for that same play, so adding
# both would double-count. It's kept below as a diagnostic-only figure.
#
# def_rating (points allowed/game, lower=better) = AVG_PTS - defense_total_ppg
# off_rating is then a residual of the vendor composite identity comp=off-def:
# off_rating = comp + def_rating. This needs no separate offense data at all.
# ============================================================================
TEAM_SHORT = {
"Buffalo Bills":"Bills","Los Angeles Rams":"Rams","Baltimore Ravens":"Ravens",
"San Francisco 49ers":"49ers","Kansas City Chiefs":"Chiefs","Chicago Bears":"Bears",
"Houston Texans":"Texans","Jacksonville Jaguars":"Jaguars","Philadelphia Eagles":"Eagles",
"Detroit Lions":"Lions","Seattle Seahawks":"Seahawks","New England Patriots":"Patriots",
"Cincinnati Bengals":"Bengals","Dallas Cowboys":"Cowboys","Green Bay Packers":"Packers",
"Los Angeles Chargers":"Chargers","Denver Broncos":"Broncos","Tampa Bay Buccaneers":"Buccaneers",
"Minnesota Vikings":"Vikings","New York Giants":"Giants","Pittsburgh Steelers":"Steelers",
"Washington Commanders":"Commanders","Indianapolis Colts":"Colts","New Orleans Saints":"Saints",
"Carolina Panthers":"Panthers","Arizona Cardinals":"Cardinals","Las Vegas Raiders":"Raiders",
"New York Jets":"Jets","Atlanta Falcons":"Falcons","Tennessee Titans":"Titans",
"Miami Dolphins":"Dolphins","Cleveland Browns":"Browns",
}

# short name -> 2025 season PAA total (Points Above Avg)
RUN_DEF_2025 = {"Browns":30.16,"Vikings":4.80,"Raiders":14.63,"Saints":1.83,"Bears":7.30,
"Jets":-0.66,"Bills":-7.85,"Dolphins":-0.76,"Cardinals":3.68,"Eagles":1.52,"Steelers":8.11,
"Packers":-7.41,"Patriots":6.88,"Rams":2.50,"Cowboys":3.10,"Chargers":4.65,"Panthers":-17.61,
"Texans":4.34,"Falcons":-8.72,"Bengals":-11.47,"Giants":-5.04,"Chiefs":-8.20,"Broncos":12.78,
"Seahawks":9.59,"Ravens":7.32,"Titans":-9.69,"Commanders":-20.27,"Buccaneers":4.81,
"Jaguars":14.73,"Colts":-7.62,"Lions":-17.38,"49ers":-22.46}
# short name -> 2026 PAA total through Week 2 (~2 games)
RUN_DEF_2026 = {"Cardinals":5.88,"Steelers":3.40,"Raiders":6.80,"Eagles":2.08,"Dolphins":1.83,
"Buccaneers":5.07,"Vikings":4.42,"Browns":0.68,"Seahawks":3.51,"Packers":1.77,"Chargers":0.50,
"Jets":6.48,"Broncos":-1.49,"Panthers":-1.77,"Cowboys":-0.78,"49ers":-3.70,"Bears":-1.40,
"Commanders":2.52,"Falcons":2.77,"Colts":-2.57,"Patriots":-0.39,"Titans":-5.64,"Jaguars":-2.35,
"Bills":-0.63,"Texans":-1.63,"Giants":-1.46,"Rams":-4.12,"Chiefs":-3.49,"Lions":-2.75,
"Bengals":0.33,"Ravens":-5.79,"Saints":-7.29}
PASS_DEF_2025 = {"Jaguars":102.37,"Broncos":55.23,"Patriots":54.88,"Seahawks":43.26,
"Eagles":42.48,"Rams":29.59,"Chargers":25.73,"Bears":31.09,"Texans":16.37,"Falcons":25.30,
"Browns":32.10,"Lions":11.44,"Panthers":22.29,"Ravens":-7.32,"Chiefs":3.96,"Buccaneers":-15.76,
"Bills":0.18,"Colts":-20.78,"Packers":-11.53,"49ers":-21.09,"Steelers":-20.37,"Saints":-4.40,
"Raiders":-9.51,"Dolphins":-17.07,"Vikings":-1.91,"Titans":-39.79,"Giants":-40.50,
"Cardinals":-48.83,"Commanders":-54.67,"Bengals":-68.69,"Cowboys":-77.95,"Jets":-75.23}
PASS_DEF_2026 = {"Rams":14.43,"Jets":10.42,"Falcons":10.29,"Panthers":13.21,"Seahawks":9.93,
"Ravens":8.80,"Bengals":4.45,"Titans":8.48,"Chiefs":4.91,"Patriots":4.40,"49ers":5.36,
"Browns":3.40,"Packers":2.31,"Steelers":4.57,"Jaguars":2.36,"Buccaneers":0.92,"Lions":-0.14,
"Raiders":-0.46,"Dolphins":1.60,"Bears":-1.64,"Saints":-4.17,"Vikings":-4.43,"Eagles":-3.31,
"Broncos":-3.58,"Commanders":-6.00,"Cardinals":-5.13,"Bills":-10.58,"Cowboys":-10.09,
"Chargers":-9.68,"Giants":-14.19,"Texans":-15.02,"Colts":-27.09}

DEF_SEASON_GAMES_2025 = 17
DEF_GAMES_2026 = 2          # elapsed through Week 2
DEF_RECENCY_BOOST = 6       # weight multiplier per 2026 game vs a 2025 game (roster turnover)

def blended_def_component(short, season25, wk2_26):
    pg25 = season25[short] / DEF_SEASON_GAMES_2025
    pg26 = wk2_26[short] / DEF_GAMES_2026
    w25 = DEF_SEASON_GAMES_2025
    w26 = DEF_GAMES_2026 * DEF_RECENCY_BOOST
    return (pg25*w25 + pg26*w26) / (w25+w26)

def decompose(team):
    short = TEAM_SHORT[team]
    run_def = blended_def_component(short, RUN_DEF_2025, RUN_DEF_2026)
    pass_def = blended_def_component(short, PASS_DEF_2025, PASS_DEF_2026)
    defense_total_ppg = run_def + pass_def          # points saved vs average; + = good D
    dfn = AVG_PTS - defense_total_ppg                # points allowed/game; lower = better
    off = TEAMS[team]["comp"] + dfn                  # off - def = comp, by the vendor's own definition
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

def simulate(home, away, home_qb_adj=0.0, away_qb_adj=0.0, market_home_spread=None, model_weight=1.0):
    ho, hd = TEAMS[home]["off"] + home_qb_adj, TEAMS[home]["def"]
    ao, ad = TEAMS[away]["off"] + away_qb_adj, TEAMS[away]["def"]
    hsd, asd = TEAMS[home]["sd"], TEAMS[away]["sd"]

    model_margin = (TEAMS[home]["comp"] - TEAMS[away]["comp"]) + HFA + (home_qb_adj - away_qb_adj)
    if market_home_spread is not None:
        # Blend the model's own margin with the market-implied margin BEFORE simulating, so the
        # blend shapes win probability and the CIs too, not just the reported median spread.
        market_margin = -market_home_spread
        expected_margin = model_weight*model_margin + (1-model_weight)*market_margin
    else:
        expected_margin = model_margin
    combined_margin_sd = math.sqrt(BASE_MARGIN_SD**2 + (UNCERTAINTY_K*(hsd+asd))**2)
    # Matchup-aware total: each side's expected points = its own offense blended with the
    # opponent's defense (points allowed), not just its own offense in isolation. The previous
    # version used expected_total = ho+ao, which never referenced hd/ad at all -- two great
    # offenses facing two great defenses projected the same total as facing two bad ones. That
    # was very likely the biggest driver of the systematic total-points underprediction flagged
    # in the Week 2 validation.
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

    z = expected_margin / combined_margin_sd
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

# Week 3 slate. Green Bay/Atlanta already played Thursday 9/24 (Falcons won 35-14) --
# kept out of MATCHUPS (nothing to simulate) and scored separately as a validation point.
MATCHUPS = [
    ("Dallas Cowboys", "Baltimore Ravens"),        # Rio de Janeiro; Dallas is the designated home team
    ("Tampa Bay Buccaneers", "Minnesota Vikings"),
    ("Denver Broncos", "Los Angeles Rams"),
    ("Chicago Bears", "Philadelphia Eagles"),
    ("Jacksonville Jaguars", "New England Patriots"),
    ("Pittsburgh Steelers", "Cincinnati Bengals"),
    ("Buffalo Bills", "Los Angeles Chargers"),
    ("Cleveland Browns", "Carolina Panthers"),
    ("Detroit Lions", "New York Jets"),
    ("Indianapolis Colts", "Houston Texans"),
    ("Miami Dolphins", "Kansas City Chiefs"),
    ("New York Giants", "Tennessee Titans"),
    ("Washington Commanders", "Seattle Seahawks"),
    ("San Francisco 49ers", "Arizona Cardinals"),
    ("New Orleans Saints", "Las Vegas Raiders"),
]
# tuple = (home, away)

# Week 3 market (spread/total), home-team perspective, sourced from sportsbook consensus
# lines for the Sat 9/26 (Rio) - Mon 9/28 slate. Moneylines not sourced this week (spread/
# total only), so vegas_win_home/away and win_prob_edge won't populate -- that's fine, the
# code treats them as optional.
VEGAS = {
    ("Dallas Cowboys","Baltimore Ravens"):        dict(home_spread=3.5,  total=52.5, home_ml=None, away_ml=None),
    ("Tampa Bay Buccaneers","Minnesota Vikings"): dict(home_spread=1.5,  total=42.5, home_ml=None, away_ml=None),
    ("Denver Broncos","Los Angeles Rams"):        dict(home_spread=2.5,  total=45.5, home_ml=None, away_ml=None),
    ("Chicago Bears","Philadelphia Eagles"):      dict(home_spread=4.5,  total=43.5, home_ml=None, away_ml=None),
    ("Jacksonville Jaguars","New England Patriots"): dict(home_spread=-3.0, total=45.5, home_ml=None, away_ml=None),
    ("Pittsburgh Steelers","Cincinnati Bengals"): dict(home_spread=3.5,  total=42.5, home_ml=None, away_ml=None),
    ("Buffalo Bills","Los Angeles Chargers"):     dict(home_spread=-7.0, total=50.5, home_ml=None, away_ml=None),
    ("Cleveland Browns","Carolina Panthers"):     dict(home_spread=2.5,  total=42.5, home_ml=None, away_ml=None),
    ("Detroit Lions","New York Jets"):            dict(home_spread=-6.5, total=47.5, home_ml=None, away_ml=None),
    ("Indianapolis Colts","Houston Texans"):      dict(home_spread=3.0,  total=42.5, home_ml=None, away_ml=None),
    ("Miami Dolphins","Kansas City Chiefs"):      dict(home_spread=11.5, total=45.5, home_ml=None, away_ml=None),
    ("New York Giants","Tennessee Titans"):       dict(home_spread=-2.5, total=39.5, home_ml=None, away_ml=None),
    ("Washington Commanders","Seattle Seahawks"): dict(home_spread=7.0,  total=40.5, home_ml=None, away_ml=None),
    ("San Francisco 49ers","Arizona Cardinals"):  dict(home_spread=-8.5, total=47.5, home_ml=None, away_ml=None),
    ("New Orleans Saints","Las Vegas Raiders"):   dict(home_spread=-3.0, total=43.5, home_ml=None, away_ml=None),
}

def ml_to_prob(ml):
    if ml is None:
        return None
    return -ml/(-ml+100) if ml < 0 else 100/(ml+100)

# ============================================================================
# QB layer: blends each Week 3 starter's 2025 season form with their 2026
# season-to-date (2 games) to (a) flag hot/cold starts and (b) produce a small,
# capped points-per-game adjustment fed back into the simulation as partial
# regression toward the established baseline. Source: SIS DataHub QB tables
# (2025 season + 2026 through Week 2), plus user-confirmed Week 3 starters.
# Note: the 2026 rushing tables haven't been refreshed past Week 1, so the
# "current season" read below is passing-only; the 2025 baseline still
# includes rushing (already collected). A known, documented asymmetry.
# ============================================================================
STARTERS = {
    "Carolina Panthers": ("Bryce Young", False), "Atlanta Falcons": ("Michael Penix Jr.", False),
    "New Orleans Saints": ("Tyler Shough", False), "Baltimore Ravens": ("Lamar Jackson", False),
    "Minnesota Vikings": ("Kyler Murray", False), "Chicago Bears": ("Case Keenum", True),
    "Cincinnati Bengals": ("Joe Burrow", False), "Houston Texans": ("C.J. Stroud", False),
    "Pittsburgh Steelers": ("Aaron Rodgers", False), "New England Patriots": ("Drake Maye", False),
    "Green Bay Packers": ("Jordan Love", False), "New York Jets": ("Geno Smith", False),
    "Cleveland Browns": ("Deshaun Watson", False), "Tampa Bay Buccaneers": ("Baker Mayfield", False),
    "Philadelphia Eagles": ("Jalen Hurts", False), "Tennessee Titans": ("Cam Ward", False),
    "Jacksonville Jaguars": ("Trevor Lawrence", False), "Denver Broncos": ("Bo Nix", False),
    "Las Vegas Raiders": ("Kirk Cousins", False), "Los Angeles Chargers": ("Justin Herbert", False),
    "Seattle Seahawks": ("Drew Lock", True), "Arizona Cardinals": ("Jacoby Brissett", False),
    "Washington Commanders": ("Marcus Mariota", True), "Dallas Cowboys": ("Dak Prescott", False),
    "Miami Dolphins": ("Malik Willis", False), "San Francisco 49ers": ("Brock Purdy", False),
    "Indianapolis Colts": ("Daniel Jones", False), "Kansas City Chiefs": ("Patrick Mahomes", False),
    "New York Giants": ("Jameis Winston", True), "Los Angeles Rams": ("Matthew Stafford", False),
    "Buffalo Bills": ("Josh Allen", False), "Detroit Lions": ("Jared Goff", False),
}
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
# name -> (2026 pass_att through Wk2, pass_PAA_total through Wk2, rush_att, rush_PAA_total)
# rush columns held at 0 -- see note above (weeks 1-2 rushing tables not yet available)
QB_2026_YTD = {
    "Jayden Daniels": (51, 17.85, 0, 0.0), "Dak Prescott": (65, 12.77, 0, 0.0),
    "Jared Goff": (77, 10.79, 0, 0.0), "Brock Purdy": (56, 11.57, 0, 0.0),
    "Drew Lock": (48, 7.93, 0, 0.0), "Josh Allen": (60, 6.11, 0, 0.0),
    "Geno Smith": (65, 5.90, 0, 0.0), "Caleb Williams": (55, 6.83, 0, 0.0),
    "Kirk Cousins": (59, 5.95, 0, 0.0), "Bryce Young": (73, 3.25, 0, 0.0),
    "Patrick Mahomes": (74, 4.27, 0, 0.0), "Matthew Stafford": (56, 4.27, 0, 0.0),
    "Jalen Hurts": (62, 2.89, 0, 0.0), "Joe Burrow": (66, 2.27, 0, 0.0),
    "Cam Ward": (52, 2.12, 0, 0.0), "Jacoby Brissett": (65, 0.01, 0, 0.0),
    "Malik Willis": (50, 0.21, 0, 0.0), "Jaxson Dart": (34, 4.16, 0, 0.0),
    "Tyler Shough": (90, -2.26, 0, 0.0), "Lamar Jackson": (56, -0.92, 0, 0.0),
    "Marcus Mariota": (16, 3.87, 0, 0.0), "Bo Nix": (59, -3.60, 0, 0.0),
    "Trevor Lawrence": (52, -2.04, 0, 0.0), "Drake Maye": (55, -3.47, 0, 0.0),
    "Daniel Jones": (62, -4.38, 0, 0.0), "C.J. Stroud": (93, -6.27, 0, 0.0),
    "Jameis Winston": (27, -2.04, 0, 0.0), "Deshaun Watson": (52, -6.73, 0, 0.0),
    "Jordan Love": (71, -9.28, 0, 0.0), "Justin Herbert": (54, -7.57, 0, 0.0),
    "Cooper Rush": (39, -24.10, 0, 0.0), "Carson Wentz": (39, -8.47, 0, 0.0),
    "Aaron Rodgers": (79, -12.53, 0, 0.0), "Kyler Murray": (5, -3.37, 0, 0.0),
    "Baker Mayfield": (62, -10.73, 0, 0.0),
}
GAMES_2026 = 2   # elapsed through Week 2
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
        # full 2025 track record, but hasn't played yet in 2026 (e.g. injury/suspension) --
        # use the 2025 baseline outright, no hot/cold read possible yet.
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
# Market blend (lever #1): shrinks toward the market line early, trusting the
# model more as validated weeks accumulate. model_weight = N/(N+K), capped at
# 0.5 -- the market will generally keep information (injuries, weather, sharp
# money) this composite-based model never sees, so it's a floor, not a stage
# the model "graduates past." N = games validated so far; K sets how fast
# trust shifts (K=64 ~= 4 weeks of games).
# ============================================================================
VALIDATED_GAMES = 16   # update this as more weeks are scored against actuals
BLEND_STABILIZE_K = 64
MODEL_WEIGHT = min(0.5, VALIDATED_GAMES / (VALIDATED_GAMES + BLEND_STABILIZE_K))

results_blended = []
for home, away in MATCHUPS:
    hq = qb_profiles[home]["qb_adj"]
    aq = qb_profiles[away]["qb_adj"]
    v = VEGAS.get((home, away))
    market_spread = v["home_spread"] if v else None
    r = simulate(home, away, home_qb_adj=hq, away_qb_adj=aq,
                 market_home_spread=market_spread, model_weight=MODEL_WEIGHT)
    r["home_qb_adj"], r["away_qb_adj"] = hq, aq
    r["model_weight"] = MODEL_WEIGHT
    if v:
        r["vegas_home_spread"] = v["home_spread"]
        r["model_home_spread"] = -r["median_margin"]
        r["edge_pts"] = round(r["model_home_spread"] - v["home_spread"], 1)
    results_blended.append(r)

out = dict(importance=importance, results=results, results_qb_adjusted=results_qb,
           results_market_blended=results_blended, model_weight=MODEL_WEIGHT,
           qb_profiles=qb_profiles,
           teams={t: dict(comp=TEAMS[t]["comp"], sd=TEAMS[t]["sd"],
                           off=round(TEAMS[t]["off"],1), defr=round(TEAMS[t]["def"],1))
                  for t in TEAMS})

with open(os.path.join(HERE, "week3_model_output.json"),"w") as f:
    json.dump(out, f, indent=2)

print(f"{'Away @ Home':50s} {'Base spread':>12s} {'QB-adj spread':>14s} {'Shift':>7s}")
for r, rq in zip(results, results_qb):
    base_sp = -r['median_margin']
    qb_sp = -rq['median_margin']
    print(f"{r['away']:22s} @ {r['home']:22s} {base_sp:>+12.1f} {qb_sp:>+14.1f} {qb_sp-base_sp:>+7.1f}")
