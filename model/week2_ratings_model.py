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

def simulate(home, away):
    ho, hd = TEAMS[home]["off"], TEAMS[home]["def"]
    ao, ad = TEAMS[away]["off"], TEAMS[away]["def"]
    hsd, asd = TEAMS[home]["sd"], TEAMS[away]["sd"]

    expected_margin = (TEAMS[home]["comp"] - TEAMS[away]["comp"]) + HFA
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

out = dict(importance=importance, results=results,
           teams={t: dict(comp=TEAMS[t]["comp"], sd=TEAMS[t]["sd"],
                           off=round(TEAMS[t]["off"],1), defr=round(TEAMS[t]["def"],1))
                  for t in TEAMS})

with open("/tmp/claude-0/-home-user-NFL/60adbde6-e2ae-5114-a91c-c73bbab8e423/scratchpad/model_output.json","w") as f:
    json.dump(out, f, indent=2)

for r in results:
    print(f"{r['away']:24s} @ {r['home']:24s} | model {r['home']} {r.get('model_home_spread', -r['median_margin']):+.1f} "
          f"(exp {r['expected_margin']:+.1f}, med {r['median_margin']:+.1f}) win% H{r['win_home']}/A{r['win_away']} conf {r['confidence']}")
