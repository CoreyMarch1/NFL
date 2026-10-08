import csv, json, math, os, statistics
from collections import defaultdict
from scipy.optimize import minimize

# Survivor pool ownership model, fit on this pool's own Weeks 2-4 pick distributions and used to
# project Week 5. Each team's share of picks is modeled as
#
#     share_t  ∝  avail_t * exp(beta * margin_t + gamma * strength_t)
#
# normalized over every team playing that week:
#   - avail_t: estimated fraction of live entries that haven't already used team t. It enters as a
#     fixed offset (coefficient 1): an entry that's used a team mechanically can't pick it again.
#   - margin_t: the team's expected margin from the market spread (or, where no line was sourced,
#     that week's composite rating + 2.0 home field).
#   - strength_t: that week's composite rating, a proxy for "saving" good teams for later weeks.
# Week 1 can't be fit (no lines or ratings on file for it) but feeds availability for later weeks.

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
FIT_WEEKS, PROJECT_WEEK = [2, 3, 4], 5
HFA = 2.0

def load_pool():
    rows = list(csv.DictReader(open(os.path.join(DATA, "survivor_pool_ownership_2026.csv"))))
    by_week = defaultdict(dict)
    for r in rows:
        by_week[int(r["Week"])][r["Team"]] = dict(pct=float(r["PickedPct"]), picks=int(r["Picks"]), won=r["Result"] == "W")
    return by_week

def entrants(week_rows):
    return sum(v["picks"] for v in week_rows.values()) / (sum(v["pct"] for v in week_rows.values()) / 100)

def load_slates():
    sched = defaultdict(list)
    for r in csv.DictReader(open(os.path.join(DATA, "nfl_2026_schedule.csv"))):
        sched[int(r["Week"])].append((r["HomeTeam"], r["AwayTeam"]))
    slates = {}
    for w in FIT_WEEKS + [PROJECT_WEEK]:
        out = json.load(open(os.path.join(HERE, f"week{w}_model_output.json")))
        comp = {t: v["comp"] for t, v in out["teams"].items()}
        lines = {(r["home"], r["away"]): r["vegas_home_spread"] for r in out["results"] if "vegas_home_spread" in r}
        teams = {}
        for h, a in sched[w]:
            sourced = (h, a) in lines
            home_margin = -lines[(h, a)] if sourced else comp[h] - comp[a] + HFA
            teams[h] = dict(margin=home_margin, strength=comp[h], line=sourced)
            teams[a] = dict(margin=-home_margin, strength=comp[a], line=sourced)
        slates[w] = teams
    return slates

def used_fractions(pool, week, n_next):
    # Fraction of live entries entering `week` that have already used each team. A team picked and
    # won in week k is used by picks_k / N_{k+1} of the next week's entries; the share is assumed
    # preserved afterward (pickers of a team survive later weeks at the same rate as everyone else,
    # and re-entries keep their history). Losing picks don't count -- those entries were eliminated.
    used = defaultdict(float)
    for k in range(1, week):
        for t, v in pool[k].items():
            if v["won"]:
                used[t] += v["picks"] / n_next[k + 1]
    return {t: min(u, 0.99) for t, u in used.items()}

def shares(slate, used, beta, gamma, use_avail=True):
    w = {t: (1 - used.get(t, 0.0) if use_avail else 1.0) * math.exp(beta * f["margin"] + gamma * f["strength"])
         for t, f in slate.items()}
    z = sum(w.values())
    return {t: x / z for t, x in w.items()}

def neg_loglik(params, weeks, ctx, spec):
    beta, gamma = params[0], (params[1] if spec["gamma"] else 0.0)
    ll = 0.0
    for w in weeks:
        pred = shares(ctx["slates"][w], ctx["used"][w], beta, gamma, spec["avail"])
        obs = ctx["pool"][w]
        other_obs = 100 - sum(v["pct"] for v in obs.values())
        other_pred = max(1e-9, 1 - sum(pred[t] for t in obs))
        ll += sum(v["pct"] * math.log(max(pred[t], 1e-9)) for t, v in obs.items()) + other_obs * math.log(other_pred)
    return -ll   # every week weighted equally (shares sum to 100), not by entry count

def fit(weeks, ctx, spec):
    x0 = [0.3, 0.0] if spec["gamma"] else [0.3]
    return minimize(neg_loglik, x0, args=(weeks, ctx, spec), method="Nelder-Mead").x

def evaluate(params, week, ctx, spec):
    beta, gamma = params[0], (params[1] if spec["gamma"] else 0.0)
    pred = shares(ctx["slates"][week], ctx["used"][week], beta, gamma, spec["avail"])
    obs = ctx["pool"][week]
    mae = statistics.mean(abs(pred[t] * 100 - v["pct"]) for t, v in obs.items())
    top_obs = max(obs, key=lambda t: obs[t]["pct"])
    return mae, max(pred, key=pred.get) == top_obs, pred

def main(n5_inflow=None):
    pool, slates = load_pool(), load_slates()
    n = {w: entrants(pool[w]) for w in pool}
    survivors = {w: n[w] - sum(v["picks"] for v in pool[w].values() if not v["won"]) for w in pool}
    inflows = [n[w + 1] / survivors[w] for w in (1, 2, 3)]
    inflow = statistics.mean(inflows) if n5_inflow is None else n5_inflow
    n[PROJECT_WEEK] = survivors[4] * inflow
    ctx = dict(pool=pool, slates=slates, used={w: used_fractions(pool, w, n) for w in FIT_WEEKS + [PROJECT_WEEK]})

    specs = {"spread only": dict(avail=False, gamma=False),
             "spread + availability": dict(avail=True, gamma=False),
             "spread + availability + strength": dict(avail=True, gamma=True)}
    cv = {}
    for name, spec in specs.items():
        maes, tops, chalk = [], [], []
        for held in FIT_WEEKS:
            p = fit([w for w in FIT_WEEKS if w != held], ctx, spec)
            mae, top, pred = evaluate(p, held, ctx, spec)
            maes.append(mae); tops.append(top)
            chalk += [abs(pred[t] * 100 - v["pct"]) for t, v in pool[held].items() if v["pct"] >= 10]
        cv[name] = dict(mae=statistics.mean(maes), by_week=maes, top_hits=sum(tops),
                        chalk_mae=statistics.mean(chalk), chalk_max=max(chalk), chalk_n=len(chalk))
    best = min(cv, key=lambda k: cv[k]["mae"])
    spec = specs[best]
    params = fit(FIT_WEEKS, ctx, spec)

    beta, gamma = params[0], (params[1] if spec["gamma"] else 0.0)
    proj = shares(slates[PROJECT_WEEK], ctx["used"][PROJECT_WEEK], beta, gamma, spec["avail"])
    s_spec = specs["spread + availability + strength"]
    sp = fit(FIT_WEEKS, ctx, s_spec)
    alt = shares(slates[PROJECT_WEEK], ctx["used"][PROJECT_WEEK], sp[0], sp[1], True)
    return dict(n=n, inflows=inflows, inflow_used=inflow, cv=cv, best=best, params=dict(beta=beta, gamma=gamma),
                strength_variant_params=dict(beta=sp[0], gamma=sp[1]),
                projection={t: dict(share=proj[t], share_if_saving_strong_teams=alt[t],
                                    margin=slates[PROJECT_WEEK][t]["margin"], used=ctx["used"][PROJECT_WEEK].get(t, 0.0))
                            for t in proj},
                fit_check={w: evaluate(params, w, ctx, spec)[2] for w in FIT_WEEKS})

if __name__ == "__main__":
    r = main()
    print("Entrants per week:", {w: round(v) for w, v in r["n"].items()}, f"(Week 5 estimated at inflow {r['inflow_used']:.2f})")
    print("\nLeave-one-week-out validation (MAE in pick-% points on the teams shown each week):")
    for name, c in r["cv"].items():
        print(f"  {name:34s} MAE {c['mae']:4.2f}  (wk2/3/4: {', '.join(f'{x:.1f}' for x in c['by_week'])})  top pick right {c['top_hits']}/3"
              f"  | on chalk (>=10% actual, n={c['chalk_n']}): avg miss {c['chalk_mae']:.1f}, worst {c['chalk_max']:.1f}")
    print(f"\nChosen: {r['best']} | beta {r['params']['beta']:.3f}/pt | gamma {r['params']['gamma']:.3f}")
    print(f"  strength variant: beta {r['strength_variant_params']['beta']:.3f}, gamma {r['strength_variant_params']['gamma']:.3f} (negative = pool saves strong teams)")
    print(f"\nWeek {PROJECT_WEEK} projected ownership:")
    for t, p in sorted(r["projection"].items(), key=lambda x: -x[1]["share"])[:12]:
        print(f"  {t:24s} {p['share']*100:5.1f}%  (if pool saves strong teams: {p['share_if_saving_strong_teams']*100:4.1f}%)  margin {p['margin']:+5.1f}  already used by {p['used']:4.0%}")
    sens = {lab: main(x)["projection"] for lab, x in [("low inflow", min(r["inflows"])), ("high inflow", max(r["inflows"]))]}
    top = sorted(r["projection"], key=lambda t: -r["projection"][t]["share"])[:5]
    print("\nWeek 5 pool-size sensitivity (top 5):", {t.split()[-1]: [round(s[t]["share"]*100, 1) for s in sens.values()] for t in top})

    out = dict(model=r["best"], params=r["params"], strength_variant_params=r["strength_variant_params"], cv=r["cv"],
               entrants={str(k): round(v) for k, v in r["n"].items()}, week5_inflow_assumed=r["inflow_used"],
               week5_projection={t: {k: round(v, 4) for k, v in p.items()} for t, p in r["projection"].items()},
               fitted_vs_actual={str(w): {t: dict(pred=round(pr[t]*100, 1)) for t in pr} for w, pr in r["fit_check"].items()})
    with open(os.path.join(HERE, "survivor_ownership_week5.json"), "w") as f:
        json.dump(out, f, indent=2)
