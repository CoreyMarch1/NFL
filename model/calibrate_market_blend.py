# Diagnostic tool, not the source of truth for the blend weight: grid-searches the
# MAE-minimizing model/market blend weight in-sample on Week 2. That optimum came out
# to 0.0 (pure market) on this single 16-game week, which is a classic small-sample
# overfit rather than a real answer -- week2_ratings_model.py uses a shrinkage formula
# instead (model_weight = validated_games/(validated_games+64), capped at 0.5) and
# this script exists to show why, and to re-run once more validated weeks accumulate.
import json, os, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "week2_model_output.json")))

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

games = []
for r in d["results_qb_adjusted"]:
    key = (r["home"], r["away"])
    if key not in ACTUALS or r.get("vegas_home_spread") is None:
        continue
    hs, as_ = ACTUALS[key]
    games.append(dict(
        matchup=f"{r['away']} @ {r['home']}",
        actual_margin=hs-as_,
        model_margin=r["expected_margin"],   # pre-simulation expected margin (model + QB adj)
        vegas_margin=-r["vegas_home_spread"],
    ))

def mae_at(w):
    errs = [abs((w*g["model_margin"] + (1-w)*g["vegas_margin"]) - g["actual_margin"]) for g in games]
    return statistics.mean(errs)

best_w, best_mae = None, 1e9
sweep = []
for i in range(0, 21):
    w = i/20
    m = mae_at(w)
    sweep.append((w, m))
    if m < best_mae:
        best_mae, best_w = m, w

print(f"n games with market line: {len(games)}")
print(f"{'weight(model)':>13s} {'MAE':>8s}")
for w, m in sweep:
    marker = "  <-- best" if w == best_w else ""
    print(f"{w:13.2f} {m:8.3f}{marker}")

print(f"\nPure model (w=1.0): MAE={mae_at(1.0):.3f}")
print(f"Pure market (w=0.0): MAE={mae_at(0.0):.3f}")
print(f"Best blend: model_weight={best_w:.2f}, MAE={best_mae:.3f}")
