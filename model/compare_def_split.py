import importlib.util, io, contextlib, json, os, statistics

HERE = os.path.dirname(os.path.abspath(__file__))

def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    m = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m

w3, w4 = load("week3_ratings_model"), load("week4_ratings_model")

# Composite refresh: swapping one of six inputs should move comp by delta/6 (plus up to 0.05 of
# the vendor's own rounding), never more.
worst = max(abs((d["comp"] - d["comp_published"]) - (d["inpred"] - d["inpred_published"]) / 6)
            for d in w4.TEAMS.values())
print(f"Composite refresh: max deviation from delta/6 = {worst:.3f} pts (should be <= 0.05)")

# Off/def split comparison against the real Week 4 market totals. SIS defense comes from the Week 3
# build (its def rating doesn't depend on comp); comp itself is held at Week 4 values for both, so
# the only thing that differs is the split.
def model_total(h, a, def_allowed):
    off = lambda t: w4.TEAMS[t]["comp"] + def_allowed[t]
    return (off(h) + def_allowed[a] - w4.AVG_PTS) + (off(a) + def_allowed[h] - w4.AVG_PTS)

splits = {
    "SIS run+pass defense (thru Wk2)": {t: w3.TEAMS[t]["def"] for t in w4.TEAMS},
    "Inpredictable dGPF (Oct 4)":      {t: w4.TEAMS[t]["def"] for t in w4.TEAMS},
    "No split (every D average)":      {t: w4.AVG_PTS for t in w4.TEAMS},
}
print(f"\nModel total vs. market total, {len(w4.VEGAS)} games with a sourced line:")
for name, d in splits.items():
    errs = [model_total(h, a, d) - v["total"] for (h, a), v in w4.VEGAS.items()]
    print(f"  {name:34s} MAE {statistics.mean(map(abs, errs)):5.2f} | bias {statistics.mean(errs):+5.2f}")

# Same check on the simulated (Monte Carlo) totals actually shipped in the output.
out = json.load(open(os.path.join(HERE, "week4_model_output.json")))
sim = [(r["proj_home_score"] + r["proj_away_score"]) - r["vegas_total"]
       for r in out["results_market_blended"] if "vegas_total" in r]
print(f"\nShipped simulated totals vs. market: MAE {statistics.mean(map(abs, sim)):.2f} | bias {statistics.mean(sim):+.2f}")
print("Caveat: dGPF is derived from betting markets, so matching market totals is partly circular --"
      "\nit shows consistency with the market, not predictive accuracy. Actual Week 4 totals are the real test.")
