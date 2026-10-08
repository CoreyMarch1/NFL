import importlib.util, io, contextlib, json, os, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "week4_model_output.json")))

# (home, away): (home_score, away_score) -- final scores via user-supplied ESPN scoreboard
# screenshots. Thursday's Browns 27, Steelers 24 isn't here: it was already final before the
# Week 4 build ran, so it was never in MATCHUPS.
ACTUALS = {
    ("Washington Commanders","Indianapolis Colts"): (13, 30),
    ("Baltimore Ravens","Tennessee Titans"): (24, 18),
    ("Buffalo Bills","New England Patriots"): (26, 29),
    ("Chicago Bears","New York Jets"): (23, 12),
    ("Cincinnati Bengals","Jacksonville Jaguars"): (17, 22),
    ("Houston Texans","Dallas Cowboys"): (30, 34),
    ("New York Giants","Arizona Cardinals"): (36, 24),
    ("Philadelphia Eagles","Los Angeles Rams"): (20, 24),
    ("Tampa Bay Buccaneers","Green Bay Packers"): (14, 17),
    ("Minnesota Vikings","Miami Dolphins"): (15, 10),
    ("Las Vegas Raiders","Kansas City Chiefs"): (27, 30),
    ("Seattle Seahawks","Los Angeles Chargers"): (30, 23),
    ("San Francisco 49ers","Denver Broncos"): (24, 14),
    ("Carolina Panthers","Detroit Lions"): (32, 26),
    ("New Orleans Saints","Atlanta Falcons"): (24, 45),
}
WITH_LINE = {(r["home"], r["away"]) for r in d["results_market_blended"] if "vegas_home_spread" in r}

def score(results, keys=None):
    rows = []
    for r in results:
        key = (r["home"], r["away"])
        if keys is not None and key not in keys:
            continue
        hs, as_ = ACTUALS[key]
        actual_margin, pred_margin = hs - as_, r["median_margin"]
        pred_total = r["proj_home_score"] + r["proj_away_score"]
        rows.append(dict(matchup=f"{r['away']} @ {r['home']}", actual=f"{as_}-{hs}",
                         actual_margin=actual_margin, pred_margin=round(pred_margin, 1),
                         err=round(abs(pred_margin - actual_margin), 1),
                         su_hit=(pred_margin > 0) == (actual_margin > 0),
                         vegas_spread=r.get("vegas_home_spread"), vegas_total=r.get("vegas_total"),
                         pred_total=round(pred_total, 1), actual_total=hs + as_))
    return rows

def summarize(rows):
    return dict(mae=round(statistics.mean(r["err"] for r in rows), 2),
                su=sum(r["su_hit"] for r in rows), n=len(rows),
                total_mae=round(statistics.mean(abs(r["pred_total"] - r["actual_total"]) for r in rows), 2))

def market_summary(rows):
    lined = [r for r in rows if r["vegas_spread"] is not None]
    return dict(mae=round(statistics.mean(abs(-r["vegas_spread"] - r["actual_margin"]) for r in lined), 2),
                su=sum((-r["vegas_spread"] > 0) == (r["actual_margin"] > 0) for r in lined), n=len(lined),
                total_mae=round(statistics.mean(abs(r["vegas_total"] - r["actual_total"]) for r in lined), 2))

stages = [("base", "results"), ("qb_adjusted", "results_qb_adjusted"),
          ("injury_adjusted", "results_injury_adjusted"), ("market_blended", "results_market_blended")]
all_rows = {name: score(d[key]) for name, key in stages}
lined_rows = {name: score(d[key], WITH_LINE) for name, key in stages}

print(f"=== All {len(ACTUALS)} games ===")
for name, _ in stages:
    s = summarize(all_rows[name])
    print(f"  {name:16s} margin MAE {s['mae']:5.2f} | SU {s['su']}/{s['n']} | total MAE {s['total_mae']:5.2f}")
print(f"\n=== The {len(WITH_LINE)} games with a market line (apples-to-apples vs. the market) ===")
for name, _ in stages:
    s = summarize(lined_rows[name])
    print(f"  {name:16s} margin MAE {s['mae']:5.2f} | SU {s['su']}/{s['n']} | total MAE {s['total_mae']:5.2f}")
mkt = market_summary(lined_rows["market_blended"])
print(f"  {'closing market':16s} margin MAE {mkt['mae']:5.2f} | SU {mkt['su']}/{mkt['n']} | total MAE {mkt['total_mae']:5.2f}")

# The off/def split only drives projected totals. Week 4 switched from the SIS split (stuck at Week 2
# data) to Inpredictable's dGPF because dGPF matched the *market's* totals far better -- a partly
# circular check. Here is the real one: each split's deterministic expected total vs. actual totals.
def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    m = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m
w3, w4 = load("week3_ratings_model"), load("week4_ratings_model")
def model_total(h, a, def_allowed):
    off = lambda t: w4.TEAMS[t]["comp"] + def_allowed[t]
    return (off(h) + def_allowed[a] - w4.AVG_PTS) + (off(a) + def_allowed[h] - w4.AVG_PTS)
splits = {"sis": {t: w3.TEAMS[t]["def"] for t in w4.TEAMS},
          "dgpf": {t: w4.TEAMS[t]["def"] for t in w4.TEAMS},
          "flat": {t: w4.AVG_PTS for t in w4.TEAMS}}
split_mae = {}
print("\n=== Off/def split vs. ACTUAL totals (all 15 games | the 11 lined games) ===")
for name, dd in splits.items():
    errs = {k: model_total(*k, dd) - sum(v) for k, v in ACTUALS.items()}
    a15 = statistics.mean(abs(e) for e in errs.values())
    a11 = statistics.mean(abs(errs[k]) for k in WITH_LINE)
    bias = statistics.mean(errs.values())
    split_mae[name] = dict(mae_all=round(a15, 2), mae_lined=round(a11, 2), bias=round(bias, 2))
    print(f"  {name:5s} MAE {a15:5.2f} | {a11:5.2f}   (bias {bias:+.2f})")
print(f"  market total (11 lined games) MAE {mkt['total_mae']:5.2f}")

print("\nPer-game detail (market-blended):")
for r in all_rows["market_blended"]:
    line = f"line {-r['vegas_spread']:+5.1f}" if r["vegas_spread"] is not None else "no line   "
    print(f"  {r['matchup']:42s} actual {r['actual']:>6s} (margin {r['actual_margin']:+3d}) | pred {r['pred_margin']:+5.1f} "
          f"| {line} | err {r['err']:4.1f} | SU {'HIT ' if r['su_hit'] else 'MISS'} | total {r['pred_total']:.1f} vs {r['actual_total']}")

s = {name: summarize(all_rows[name]) for name, _ in stages}
out = dict(base=all_rows["base"], qb_adjusted=all_rows["qb_adjusted"],
           injury_adjusted=all_rows["injury_adjusted"], market_blended=all_rows["market_blended"],
           lined_games=dict(model={name: summarize(lined_rows[name]) for name, _ in stages}, market=mkt),
           def_split_vs_actual_totals=split_mae,
           summary=dict(base_mae=s["base"]["mae"], qb_mae=s["qb_adjusted"]["mae"], inj_mae=s["injury_adjusted"]["mae"],
                        blend_mae=s["market_blended"]["mae"], base_su=s["base"]["su"], qb_su=s["qb_adjusted"]["su"],
                        inj_su=s["injury_adjusted"]["su"], blend_su=s["market_blended"]["su"],
                        blend_total_mae=s["market_blended"]["total_mae"],
                        model_weight=d.get("model_weight"), n=len(ACTUALS)))
with open(os.path.join(HERE, "week4_validation_output.json"), "w") as f:
    json.dump(out, f, indent=2)
