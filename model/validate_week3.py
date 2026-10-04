import json, os, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "week3_model_output.json")))

# (home, away): (home_score, away_score) -- confirmed final scores, via user-supplied
# ESPN scoreboard screenshots. Thursday's Falcons 35, Packers 14 isn't here -- it was
# never in MATCHUPS (already final before the Week 3 build ran) and is scored
# separately as a narrative point in the README/dashboard.
ACTUALS = {
    ("Dallas Cowboys","Baltimore Ravens"): (31, 34),
    ("Tampa Bay Buccaneers","Minnesota Vikings"): (16, 23),
    ("Denver Broncos","Los Angeles Rams"): (30, 26),
    ("Chicago Bears","Philadelphia Eagles"): (27, 7),
    ("Jacksonville Jaguars","New England Patriots"): (35, 6),
    ("Pittsburgh Steelers","Cincinnati Bengals"): (30, 27),
    ("Buffalo Bills","Los Angeles Chargers"): (24, 16),
    ("Cleveland Browns","Carolina Panthers"): (21, 18),
    ("Detroit Lions","New York Jets"): (31, 24),
    ("Indianapolis Colts","Houston Texans"): (19, 17),
    ("Miami Dolphins","Kansas City Chiefs"): (10, 24),
    ("New York Giants","Tennessee Titans"): (12, 7),
    ("Washington Commanders","Seattle Seahawks"): (33, 31),
    ("San Francisco 49ers","Arizona Cardinals"): (36, 30),
    ("New Orleans Saints","Las Vegas Raiders"): (27, 35),
}

def eval_set(results, label):
    errs, su_correct, ats_correct, ats_total, total_pts_err = [], 0, 0, 0, []
    rows = []
    for r in results:
        key = (r["home"], r["away"])
        hs, as_ = ACTUALS[key]
        actual_margin = hs - as_
        pred_margin = r["median_margin"]
        err = abs(pred_margin - actual_margin)
        errs.append(err)
        pred_home_win = pred_margin > 0
        actual_home_win = actual_margin > 0
        su_hit = pred_home_win == actual_home_win
        su_correct += su_hit
        vegas_spread = r.get("vegas_home_spread")
        if vegas_spread is not None:
            home_cover = (actual_margin + vegas_spread) > 0
            model_edge = r.get("edge_pts")
            if model_edge is not None and abs(model_edge) >= 0.3:
                leans_home = model_edge < 0
                bet_won = home_cover if leans_home else (not home_cover)
                ats_total += 1
                ats_correct += bet_won
        actual_total = hs+as_
        pred_total = r["proj_home_score"]+r["proj_away_score"]
        total_pts_err.append(abs(pred_total-actual_total))
        rows.append(dict(matchup=f"{r['away']} @ {r['home']}", actual=f"{as_}-{hs}",
                          actual_margin=actual_margin, pred_margin=round(pred_margin,1),
                          err=round(err,1), su_hit=su_hit, vegas_spread=vegas_spread,
                          pred_total=round(pred_total,1), actual_total=actual_total))
    print(f"=== {label} ===")
    print(f"MAE (margin): {statistics.mean(errs):.2f} pts | Median AE: {statistics.median(errs):.2f} pts")
    print(f"Straight-up (winner) accuracy: {su_correct}/{len(results)} ({su_correct/len(results)*100:.0f}%)")
    print(f"MAE (total points): {statistics.mean(total_pts_err):.2f} pts")
    if ats_total:
        print(f"ATS record when model diverged >=0.3pt from market: {ats_correct}/{ats_total} ({ats_correct/ats_total*100:.0f}%)")
    print()
    return rows, statistics.mean(errs), su_correct

def vegas_only_eval(results):
    errs, su_correct = [], 0
    for r in results:
        key = (r["home"], r["away"])
        hs, as_ = ACTUALS[key]
        actual_margin = hs-as_
        vs = r.get("vegas_home_spread")
        if vs is None:
            continue
        pred_margin = -vs
        errs.append(abs(pred_margin-actual_margin))
        su_correct += (pred_margin>0) == (actual_margin>0)
    print("=== Vegas closing line (spread only) ===")
    print(f"MAE (margin): {statistics.mean(errs):.2f} pts")
    print(f"Straight-up accuracy: {su_correct}/{len(errs)} ({su_correct/len(errs)*100:.0f}%)")
    print()

base_rows, base_mae, base_su = eval_set(d["results"], "BASE MODEL (no QB/injury adjustment)")
qb_rows, qb_mae, qb_su = eval_set(d["results_qb_adjusted"], "QB-ADJUSTED MODEL")
inj_rows, inj_mae, inj_su = eval_set(d["results_injury_adjusted"], "QB+INJURY-ADJUSTED MODEL")
blend_rows, blend_mae, blend_su = eval_set(d["results_market_blended"], f"MARKET-BLENDED MODEL (model_weight={d.get('model_weight')})")
vegas_only_eval(d["results"])

print("Per-game detail (market-blended):")
for r in blend_rows:
    print(f"  {r['matchup']:42s} actual {r['actual']:>7s} (margin {r['actual_margin']:+3d}) | "
          f"pred {r['pred_margin']:+5.1f} | err {r['err']:4.1f} | SU {'HIT' if r['su_hit'] else 'MISS'} | "
          f"totals pred {r['pred_total']:.1f} vs actual {r['actual_total']}")

out = dict(base=base_rows, qb_adjusted=qb_rows, injury_adjusted=inj_rows, market_blended=blend_rows,
           summary=dict(base_mae=round(base_mae,2), qb_mae=round(qb_mae,2), inj_mae=round(inj_mae,2),
                        blend_mae=round(blend_mae,2), blend_su=blend_su, model_weight=d.get("model_weight"),
                        base_su=base_su, qb_su=qb_su, inj_su=inj_su, n=len(base_rows)))
with open(os.path.join(HERE, "week3_validation_output.json"),"w") as f:
    json.dump(out, f, indent=2)
