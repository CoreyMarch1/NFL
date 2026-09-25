import random, statistics, json, math

random.seed(42)

# Team, Composite, StdDev, FPI, nfelo, Inpredictable, UnexpectedPoints, FTN_DVOA, PFF
TEAMS = {
"Buffalo Bills":        dict(comp=4.9, sd=0.4, fpi=4.9, nfelo=4.4, inpred=4.7, up=4.8, dvoa=5.2, pff=5.5),
"Los Angeles Rams":     dict(comp=4.4, sd=0.9, fpi=2.9, nfelo=3.9, inpred=4.8, up=5.4, dvoa=4.4, pff=5.1),
"Baltimore Ravens":     dict(comp=4.1, sd=0.8, fpi=4.8, nfelo=4.2, inpred=4.3, up=4.4, dvoa=2.5, pff=4.5),
"San Francisco 49ers":  dict(comp=3.6, sd=1.3, fpi=5.4, nfelo=1.9, inpred=4.7, up=2.7, dvoa=3.0, pff=4.0),
"Kansas City Chiefs":   dict(comp=3.3, sd=1.1, fpi=4.3, nfelo=3.1, inpred=3.4, up=4.1, dvoa=1.1, pff=3.5),
"Chicago Bears":        dict(comp=2.8, sd=0.7, fpi=2.7, nfelo=2.2, inpred=4.1, up=2.9, dvoa=2.6, pff=2.3),
"Houston Texans":       dict(comp=2.5, sd=0.7, fpi=1.9, nfelo=1.9, inpred=2.6, up=2.3, dvoa=3.8, pff=2.3),
"Jacksonville Jaguars": dict(comp=2.3, sd=1.1, fpi=3.4, nfelo=1.4, inpred=0.9, up=3.6, dvoa=2.4, pff=2.2),
"Philadelphia Eagles":  dict(comp=2.3, sd=1.2, fpi=1.5, nfelo=1.8, inpred=3.9, up=0.6, dvoa=2.6, pff=3.2),
"Detroit Lions":        dict(comp=2.2, sd=1.0, fpi=1.6, nfelo=2.0, inpred=0.8, up=3.7, dvoa=2.7, pff=2.6),
"Seattle Seahawks":     dict(comp=2.2, sd=2.5, fpi=-2.9, nfelo=3.8, inpred=3.0, up=2.7, dvoa=3.1, pff=3.4),
"New England Patriots": dict(comp=1.9, sd=1.2, fpi=1.5, nfelo=2.3, inpred=0.5, up=3.7, dvoa=0.9, pff=2.5),
"Cincinnati Bengals":   dict(comp=1.4, sd=0.5, fpi=1.6, nfelo=1.5, inpred=1.8, up=2.0, dvoa=1.1, pff=0.5),
"Dallas Cowboys":       dict(comp=0.9, sd=0.8, fpi=1.9, nfelo=0.2, inpred=1.6, up=0.7, dvoa=1.3, pff=0.0),
"Green Bay Packers":    dict(comp=0.8, sd=1.2, fpi=1.1, nfelo=0.4, inpred=-0.2, up=2.6, dvoa=-0.7, pff=1.8),
"Los Angeles Chargers": dict(comp=0.7, sd=0.8, fpi=0.4, nfelo=-0.2, inpred=1.8, up=0.5, dvoa=0.4, pff=1.5),
"Denver Broncos":       dict(comp=0.5, sd=1.1, fpi=-1.4, nfelo=0.2, inpred=1.0, up=1.4, dvoa=0.2, pff=1.7),
"Tampa Bay Buccaneers": dict(comp=-0.3, sd=0.7, fpi=0.0, nfelo=-0.8, inpred=0.2, up=0.1, dvoa=0.2, pff=-1.6),
"Minnesota Vikings":    dict(comp=-0.8, sd=1.2, fpi=-0.5, nfelo=-1.5, inpred=0.7, up=-0.7, dvoa=-2.6, pff=0.0),
"New York Giants":      dict(comp=-1.0, sd=0.8, fpi=0.0, nfelo=-2.3, inpred=-1.0, up=-0.7, dvoa=-1.0, pff=-1.2),
"Pittsburgh Steelers":  dict(comp=-1.2, sd=0.6, fpi=-1.5, nfelo=-0.8, inpred=-2.2, up=-1.2, dvoa=-1.2, pff=-0.4),
"Washington Commanders":dict(comp=-1.2, sd=0.4, fpi=-0.8, nfelo=-1.7, inpred=-1.0, up=-0.6, dvoa=-1.4, pff=-1.5),
"Indianapolis Colts":   dict(comp=-1.6, sd=0.5, fpi=-1.8, nfelo=-2.1, inpred=-1.6, up=-1.6, dvoa=-0.7, pff=-2.1),
"New Orleans Saints":   dict(comp=-2.7, sd=1.3, fpi=-1.5, nfelo=-3.5, inpred=-1.9, up=-1.7, dvoa=-4.8, pff=-3.0),
"Carolina Panthers":    dict(comp=-2.8, sd=0.8, fpi=-2.9, nfelo=-3.8, inpred=-2.1, up=-2.0, dvoa=-2.5, pff=-3.7),
"Arizona Cardinals":    dict(comp=-3.5, sd=2.0, fpi=-3.0, nfelo=-5.7, inpred=-2.2, up=-4.4, dvoa=-0.6, pff=-5.4),
"Las Vegas Raiders":    dict(comp=-3.9, sd=0.7, fpi=-3.7, nfelo=-4.1, inpred=-3.2, up=-5.2, dvoa=-3.2, pff=-3.8),
"New York Jets":        dict(comp=-4.3, sd=1.2, fpi=-3.3, nfelo=-5.2, inpred=-5.2, up=-4.7, dvoa=-2.4, pff=-4.8),
"Atlanta Falcons":      dict(comp=-4.9, sd=1.8, fpi=-2.5, nfelo=-5.1, inpred=-5.8, up=-5.6, dvoa=-7.3, pff=-2.9),
"Tennessee Titans":     dict(comp=-5.8, sd=0.6, fpi=-5.5, nfelo=-6.2, inpred=-5.1, up=-6.7, dvoa=-5.9, pff=-5.6),
"Miami Dolphins":       dict(comp=-7.0, sd=1.3, fpi=-7.5, nfelo=-7.6, inpred=-6.8, up=-6.4, dvoa=-5.0, pff=-8.7),
"Cleveland Browns":     dict(comp=-7.1, sd=0.9, fpi=-7.1, nfelo=-7.3, inpred=-6.6, up=-6.6, dvoa=-8.7, pff=-6.2),
}

AVG_PTS = 22.5   # league-average team points/game baseline used for off/def decomposition
K_TILT = 0.35    # damping applied to Unexpected Points vs composite gap -> pace/style tilt

def decompose(team):
    d = TEAMS[team]
    tilt = K_TILT * (d["up"] - d["comp"])
    tilt = max(-1.5, min(1.5, tilt))
    off = AVG_PTS + d["comp"]/2 + tilt
    dfn = AVG_PTS - d["comp"]/2 + tilt
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
    expected_total = ho + ao
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

MATCHUPS = [
    ("Buffalo Bills", "Detroit Lions"),
    ("Atlanta Falcons", "Carolina Panthers"),
    ("Baltimore Ravens", "New Orleans Saints"),
    ("Chicago Bears", "Minnesota Vikings"),
    ("Houston Texans", "Cincinnati Bengals"),
    ("New England Patriots", "Pittsburgh Steelers"),
    ("New York Jets", "Green Bay Packers"),
    ("Tampa Bay Buccaneers", "Cleveland Browns"),
    ("Tennessee Titans", "Philadelphia Eagles"),
    ("Denver Broncos", "Jacksonville Jaguars"),
    ("Los Angeles Chargers", "Las Vegas Raiders"),
    ("Arizona Cardinals", "Seattle Seahawks"),
    ("Dallas Cowboys", "Washington Commanders"),
    ("San Francisco 49ers", "Miami Dolphins"),
    ("Kansas City Chiefs", "Indianapolis Colts"),
    ("Los Angeles Rams", "New York Giants"),
]
# tuple = (home, away)

# Full Week 2 market (spread/total/moneyline), home-team perspective, sourced from
# sportsbook consensus lines for the Sun 9/20 - Mon 9/21 slate (BUF/DET already final).
VEGAS = {
    ("Buffalo Bills","Detroit Lions"):        dict(home_spread=-5.5, total=54.5, home_ml=None, away_ml=None),
    ("Atlanta Falcons","Carolina Panthers"):  dict(home_spread=2.5,  total=43.5, home_ml=124,  away_ml=-148),
    ("Baltimore Ravens","New Orleans Saints"):dict(home_spread=-8.5, total=46.5, home_ml=-395, away_ml=310),
    ("Chicago Bears","Minnesota Vikings"):    dict(home_spread=-4.5, total=47.5, home_ml=-205, away_ml=170),
    ("Houston Texans","Cincinnati Bengals"):  dict(home_spread=-2.5, total=45.5, home_ml=-135, away_ml=114),
    ("New England Patriots","Pittsburgh Steelers"): dict(home_spread=-5.5, total=41.5, home_ml=-218, away_ml=180),
    ("New York Jets","Green Bay Packers"):    dict(home_spread=3.5,  total=44.5, home_ml=164,  away_ml=-198),
    ("Tampa Bay Buccaneers","Cleveland Browns"): dict(home_spread=-8.5, total=41.5, home_ml=-455, away_ml=350),
    ("Tennessee Titans","Philadelphia Eagles"): dict(home_spread=7.0, total=39.5, home_ml=250,  away_ml=-310),
    ("Denver Broncos","Jacksonville Jaguars"): dict(home_spread=-2.5, total=45.5, home_ml=-148, away_ml=124),
    ("Los Angeles Chargers","Las Vegas Raiders"): dict(home_spread=-6.5, total=43.5, home_ml=-310, away_ml=250),
    ("Arizona Cardinals","Seattle Seahawks"): dict(home_spread=3.5,  total=40.5, home_ml=180,  away_ml=-218),
    ("Dallas Cowboys","Washington Commanders"): dict(home_spread=-4.5, total=50.5, home_ml=-218, away_ml=180),
    ("San Francisco 49ers","Miami Dolphins"): dict(home_spread=-12.5, total=44.5, home_ml=-900, away_ml=600),
    ("Kansas City Chiefs","Indianapolis Colts"): dict(home_spread=-6.5, total=46.5, home_ml=-290, away_ml=235),
    ("Los Angeles Rams","New York Giants"):   dict(home_spread=-7.0, total=48.5, home_ml=-375, away_ml=295),
}

def ml_to_prob(ml):
    if ml is None:
        return None
    return -ml/(-ml+100) if ml < 0 else 100/(ml+100)

# ============================================================================
# QB layer: blends each Week 2 starter's 2025 season form with their 2026
# Week 1 game to (a) flag hot/cold starts and (b) produce a small, capped
# points-per-game adjustment fed back into the simulation as partial
# regression toward the established baseline. Source: SIS DataHub QB tables
# (2025 season + 2026 Week 1), plus user-confirmed Week 2 starters.
# ============================================================================
STARTERS = {
    "Carolina Panthers": ("Bryce Young", False), "Atlanta Falcons": ("Cooper Rush", True),
    "New Orleans Saints": ("Tyler Shough", False), "Baltimore Ravens": ("Lamar Jackson", False),
    "Minnesota Vikings": ("Carson Wentz", True), "Chicago Bears": ("Caleb Williams", False),
    "Cincinnati Bengals": ("Joe Burrow", False), "Houston Texans": ("C.J. Stroud", False),
    "Pittsburgh Steelers": ("Aaron Rodgers", False), "New England Patriots": ("Drake Maye", False),
    "Green Bay Packers": ("Jordan Love", False), "New York Jets": ("Geno Smith", False),
    "Cleveland Browns": ("Deshaun Watson", False), "Tampa Bay Buccaneers": ("Baker Mayfield", False),
    "Philadelphia Eagles": ("Jalen Hurts", False), "Tennessee Titans": ("Cam Ward", False),
    "Jacksonville Jaguars": ("Trevor Lawrence", False), "Denver Broncos": ("Bo Nix", False),
    "Las Vegas Raiders": ("Kirk Cousins", False), "Los Angeles Chargers": ("Justin Herbert", False),
    "Seattle Seahawks": ("Drew Lock", True), "Arizona Cardinals": ("Jacoby Brissett", False),
    "Washington Commanders": ("Jayden Daniels", False), "Dallas Cowboys": ("Dak Prescott", False),
    "Miami Dolphins": ("Malik Willis", False), "San Francisco 49ers": ("Brock Purdy", False),
    "Indianapolis Colts": ("Daniel Jones", False), "Kansas City Chiefs": ("Patrick Mahomes", False),
    "New York Giants": ("Jaxson Dart", False), "Los Angeles Rams": ("Matthew Stafford", False),
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
}
# name -> (2026 Wk1 pass_att, pass_PAA_total, rush_att, rush_PAA_total)
QB_2026_WK1 = {
    "Jayden Daniels": (34, 12.04, 5, 2.97), "Jared Goff": (39, 10.38, 2, -0.63),
    "Dak Prescott": (34, 7.22, 2, 0.74), "Joe Burrow": (35, 6.24, 5, -0.14),
    "Caleb Williams": (29, 6.52, 10, -3.92), "Jacoby Brissett": (37, 5.29, 6, 0.61),
    "Josh Allen": (29, 4.75, 6, -3.76), "Geno Smith": (24, 6.39, 6, -0.41),
    "Jaxson Dart": (29, 3.89, 11, -0.34), "Cam Ward": (32, 1.88, 4, 1.94),
    "Trevor Lawrence": (23, 3.25, 2, -0.35), "Drew Lock": (22, 1.88, 2, 0.02),
    "Bryce Young": (37, 0.36, 2, -0.30), "Aaron Rodgers": (40, -0.41, 3, 0.00),
    "Lamar Jackson": (25, 1.11, 7, 3.18), "Brock Purdy": (34, 0.15, 5, 1.48),
    "Malik Willis": (27, -0.79, 6, -0.81), "Jalen Hurts": (25, -0.62, 7, 2.01),
    "Daniel Jones": (31, -1.55, 1, 0.85), "C.J. Stroud": (38, -1.17, 2, -0.74),
    "Drake Maye": (33, -1.52, 7, 0.01), "Justin Herbert": (27, -2.41, 5, -1.22),
    "Kirk Cousins": (30, -1.66, 5, -0.63), "Tyler Shough": (56, -3.61, 4, 0.20),
    "Carson Wentz": (19, -1.55, 5, -0.36), "Bo Nix": (28, -4.28, 3, -0.73),
    "Baker Mayfield": (28, -4.49, 5, -1.50), "Patrick Mahomes": (27, -3.62, 7, 1.97),
    "Jordan Love": (42, -5.71, 1, -4.69), "Matthew Stafford": (25, -4.68, 2, 0.00),
    "Deshaun Watson": (22, -12.76, 6, 3.54), "Cooper Rush": (22, -14.79, 0, 0.00),
}
STABILIZE_CAP, RECENCY_BOOST = 450, 5.0
REG_WEIGHT, TEAM_CHANGE_DISCOUNT, QB_ADJ_CAP = 0.11, 0.5, 1.2

def build_qb_profile(team):
    name, is_backup = STARTERS[team]
    d25, d26 = QB_2025.get(name), QB_2026_WK1.get(name)
    team_change = bool(d25 and d25[5] not in team)
    total26 = (d26[1]+d26[3]) if d26 else None   # pass PAA + rush PAA, this game
    if d25 and total26 is not None:
        games25, patt25, ppaa25, ratt25, rpaa25 = d25[0], d25[1], d25[2], d25[3], d25[4]
        ppg25 = (ppaa25+rpaa25)/games25
        w25 = min(patt25+ratt25, STABILIZE_CAP)
        w26 = (d26[0]+d26[2])*RECENCY_BOOST
        blended = (ppg25*w25 + total26*w26) / (w25+w26)
        hot_cold = round(total26-ppg25, 2)
        w = TEAM_CHANGE_DISCOUNT if team_change else 1.0
        qb_adj = max(-QB_ADJ_CAP, min(QB_ADJ_CAP, w*REG_WEIGHT*(ppg25-total26)))
        quality = "team-change" if team_change else "full"
        paa25_out = round(ppg25, 2)
    elif total26 is not None:
        blended, hot_cold, qb_adj, quality, paa25_out = total26, None, 0.0, "no-2025-baseline", None
    else:
        blended, hot_cold, qb_adj, quality, paa25_out = None, None, 0.0, "no-data", None
    return dict(team=team, name=name, is_backup=is_backup, paa2025=paa25_out,
                paa2026=round(total26,2) if total26 is not None else None,
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

with open("/tmp/claude-0/-home-user-NFL/60adbde6-e2ae-5114-a91c-c73bbab8e423/scratchpad/model_output.json","w") as f:
    json.dump(out, f, indent=2)

print(f"{'Away @ Home':50s} {'Base spread':>12s} {'QB-adj spread':>14s} {'Shift':>7s}")
for r, rq in zip(results, results_qb):
    base_sp = -r['median_margin']
    qb_sp = -rq['median_margin']
    print(f"{r['away']:22s} @ {r['home']:22s} {base_sp:>+12.1f} {qb_sp:>+14.1f} {qb_sp-base_sp:>+7.1f}")
