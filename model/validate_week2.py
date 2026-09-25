import json, os, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "week2_model_output.json")))

# (home, away): (home_score, away_score) -- confirmed final scores
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
        ats_hit = None
        if vegas_spread is not None:
            # vegas favors home by -vegas_spread; ats "cover" = actual_margin - (-vegas_spread) > 0 for home
            home_cover = (actual_margin + vegas_spread) > 0
            model_favors_home_more_than_market = (-pred_margin) < vegas_spread  # model's home spread more negative (favors home) than market's
            # simpler: did the side our model leaned relative to market actually win the bet?
            model_edge = r.get("edge_pts")
            if model_edge is not None and abs(model_edge) >= 0.3:
                leans_home = model_edge < 0  # model_home_spread < vegas => model likes home more
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

base_rows, base_mae, base_su = eval_set(d["results"], "BASE MODEL (no QB adjustment)")
qb_rows, qb_mae, qb_su = eval_set(d["results_qb_adjusted"], "QB-ADJUSTED MODEL")
vegas_only_eval(d["results"])

print("Per-game detail (QB-adjusted):")
for r in qb_rows:
    print(f"  {r['matchup']:42s} actual {r['actual']:>7s} (margin {r['actual_margin']:+3d}) | "
          f"pred {r['pred_margin']:+5.1f} | err {r['err']:4.1f} | SU {'HIT' if r['su_hit'] else 'MISS'} | "
          f"totals pred {r['pred_total']:.1f} vs actual {r['actual_total']}")

out = dict(base=base_rows, qb_adjusted=qb_rows,
           summary=dict(base_mae=round(base_mae,2), qb_mae=round(qb_mae,2),
                        base_su=base_su, qb_su=qb_su, n=len(base_rows)))
with open(os.path.join(HERE, "week2_validation_output.json"),"w") as f:
    json.dump(out, f, indent=2)
