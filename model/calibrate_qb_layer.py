# Diagnostic tool, same spirit as calibrate_market_blend.py: grid-searches the QB layer's
# hand-picked constants (REG_WEIGHT, RECENCY_BOOST, STABILIZE_CAP, TEAM_CHANGE_DISCOUNT,
# QB_ADJ_CAP) against Week 2's 16 actual results, to see whether the current values are
# defensible or just guesses that happen to be wrong. Same overfitting caveat applies even
# harder here: 5 free parameters against 16 games is enough degrees of freedom to fit noise,
# and TEAM_CHANGE_DISCOUNT in particular only touches a single game (Cooper Rush) this week,
# so its "optimum" here is not a real answer. Report the sweep, don't blindly adopt the argmin.
import importlib.util, os, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("week2_ratings_model", os.path.join(HERE, "week2_ratings_model.py"))
w2 = importlib.util.module_from_spec(spec)
sys.stdout = open(os.devnull, "w")  # week2_ratings_model prints its own table on import; suppress it here
spec.loader.exec_module(w2)
sys.stdout = sys.__stdout__

ACTUALS = {
    ("Buffalo Bills","Detroit Lions"): (41, 31),
    ("Atlanta Falcons","Carolina Panthers"): (3, 34),
    ("Baltimore Ravens","New Orleans Saints"): (17, 24),
    ("Chicago Bears","Minnesota Vikings"): (3, 9),
    ("Houston Texans","Cincinnati Bengals"): (6, 20),
    ("New England Patriots","Pittsburgh Steelers"): (20, 3),
    ("New York Jets","Green Bay Packers"): (17, 20),
    ("Tampa Bay Buccaneers","Cleveland Browns"): (19, 23),
    ("Tennessee Titans","Philadelphia Eagles"): (20, 24),
    ("Denver Broncos","Jacksonville Jaguars"): (20, 13),
    ("Los Angeles Chargers","Las Vegas Raiders"): (14, 26),
    ("Arizona Cardinals","Seattle Seahawks"): (7, 31),
    ("Dallas Cowboys","Washington Commanders"): (37, 20),
    ("San Francisco 49ers","Miami Dolphins"): (35, 13),
    ("Kansas City Chiefs","Indianapolis Colts"): (33, 30),
    ("Los Angeles Rams","New York Giants"): (28, 6),
}

def qb_adj(team, REG_WEIGHT, RECENCY_BOOST, STABILIZE_CAP, TEAM_CHANGE_DISCOUNT, QB_ADJ_CAP):
    name, _ = w2.STARTERS[team]
    d25, d26 = w2.QB_2025.get(name), w2.QB_2026_WK1.get(name)
    if not (d25 and d26):
        return 0.0
    games25, patt25, ppaa25, ratt25, rpaa25, team25 = d25
    ppg25 = (ppaa25 + rpaa25) / games25
    total26 = d26[1] + d26[3]
    w25 = min(patt25 + ratt25, STABILIZE_CAP)
    w26 = (d26[0] + d26[2]) * RECENCY_BOOST
    team_change = team25 not in team
    w = TEAM_CHANGE_DISCOUNT if team_change else 1.0
    return max(-QB_ADJ_CAP, min(QB_ADJ_CAP, w * REG_WEIGHT * (ppg25 - total26)))

def score(REG_WEIGHT, RECENCY_BOOST, STABILIZE_CAP, TEAM_CHANGE_DISCOUNT, QB_ADJ_CAP):
    errs, su_correct = [], 0
    for home, away in w2.MATCHUPS:
        hs, as_ = ACTUALS[(home, away)]
        actual_margin = hs - as_
        hq = qb_adj(home, REG_WEIGHT, RECENCY_BOOST, STABILIZE_CAP, TEAM_CHANGE_DISCOUNT, QB_ADJ_CAP)
        aq = qb_adj(away, REG_WEIGHT, RECENCY_BOOST, STABILIZE_CAP, TEAM_CHANGE_DISCOUNT, QB_ADJ_CAP)
        pred_margin = (w2.TEAMS[home]["comp"] - w2.TEAMS[away]["comp"]) + w2.HFA + (hq - aq)
        errs.append(abs(pred_margin - actual_margin))
        su_correct += (pred_margin > 0) == (actual_margin > 0)
    return statistics.mean(errs), su_correct

CURRENT = dict(REG_WEIGHT=0.11, RECENCY_BOOST=5.0, STABILIZE_CAP=450, TEAM_CHANGE_DISCOUNT=0.5, QB_ADJ_CAP=1.2)
cur_mae, cur_su = score(**CURRENT)
print(f"Current constants {CURRENT}")
print(f"  -> MAE={cur_mae:.3f} pts, straight-up={cur_su}/16\n")

REG_WEIGHTS = [0.0, 0.05, 0.08, 0.11, 0.15, 0.20, 0.30]
RECENCY_BOOSTS = [1, 2, 3, 5, 7, 10]
STABILIZE_CAPS = [150, 300, 450, 600, 900]
TEAM_CHANGE_DISCOUNTS = [0.25, 0.5, 0.75, 1.0]
QB_ADJ_CAPS = [0.6, 1.2, 1.8, 2.4]

results = []
for rw in REG_WEIGHTS:
    for rb in RECENCY_BOOSTS:
        for sc in STABILIZE_CAPS:
            for tcd in TEAM_CHANGE_DISCOUNTS:
                for cap in QB_ADJ_CAPS:
                    mae, su = score(rw, rb, sc, tcd, cap)
                    results.append((mae, -su, rw, rb, sc, tcd, cap))

results.sort()
print(f"Grid size: {len(results)} combinations\n")
print("Top 10 by MAE (tie-break: higher straight-up accuracy):")
print(f"{'MAE':>6s} {'SU':>4s} {'REG_WEIGHT':>10s} {'RECENCY':>8s} {'STAB_CAP':>9s} {'TEAM_CHG':>9s} {'ADJ_CAP':>8s}")
for mae, neg_su, rw, rb, sc, tcd, cap in results[:10]:
    print(f"{mae:6.3f} {-neg_su:4d} {rw:10.2f} {rb:8.1f} {sc:9.0f} {tcd:9.2f} {cap:8.1f}")

print("\nWorst 5 (for contrast):")
for mae, neg_su, rw, rb, sc, tcd, cap in results[-5:]:
    print(f"{mae:6.3f} {-neg_su:4d} {rw:10.2f} {rb:8.1f} {sc:9.0f} {tcd:9.2f} {cap:8.1f}")

# Sensitivity: hold everything else at current, vary one parameter at a time
print("\n--- One-at-a-time sensitivity around current constants ---")
for pname, values in [("REG_WEIGHT", REG_WEIGHTS), ("RECENCY_BOOST", RECENCY_BOOSTS),
                       ("STABILIZE_CAP", STABILIZE_CAPS), ("TEAM_CHANGE_DISCOUNT", TEAM_CHANGE_DISCOUNTS),
                       ("QB_ADJ_CAP", QB_ADJ_CAPS)]:
    print(f"{pname}:")
    for v in values:
        params = dict(CURRENT)
        params[pname] = v
        mae, su = score(**params)
        marker = "  <-- current" if v == CURRENT[pname] else ""
        print(f"  {v:>7} -> MAE={mae:.3f}, SU={su}/16{marker}")
