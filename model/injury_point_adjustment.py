import csv, json, os, re
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))

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

def norm(name):
    name = re.sub(r"\s+(Jr\.|Sr\.|III|II|IV|V)$", "", name)
    name = name.replace(".", "").replace("'", "").replace("-", " ")
    return name.strip().lower()

OFFENSE_POS = {"RB", "WR", "TE", "OT", "OG", "C"}
DEFENSE_POS = {"CB", "S", "LB", "DE", "DT"}

# --- 2026-to-date value per player, same combine-by-play-type logic as tier_injuries.py's
# 2025 season loader, just pointed at the current-season files. A player absent from every one
# of these tables is treated as replacement-level (0.0), not "unknown" -- per SIS, a player who
# doesn't crack these tables hasn't had a meaningful 2026 impact (hurt, suspended, or buried on
# the depth chart), which is itself the right prior for "how much does losing him cost."
value_2026 = {}  # (team, norm_name) -> paa_2026_total
with open(os.path.join(HERE, "..", "data", "sis_receiving_2026_thru_wk2.csv")) as f:
    for row in csv.DictReader(f):
        team = row["Team"]
        if team == "2 teams":
            continue
        value_2026[(team, norm(row["Player"]))] = float(row["Points Above Avg"])
with open(os.path.join(HERE, "..", "data", "sis_rushing_2026_thru_wk2.csv")) as f:
    for row in csv.DictReader(f):
        team = row["Team"]
        if team == "2 teams":
            continue
        key = (team, norm(row["Player"]))
        value_2026[key] = value_2026.get(key, 0.0) + float(row["Points Above Avg"])
with open(os.path.join(HERE, "..", "data", "sis_blocking_2026_thru_wk2.csv")) as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        team = row[3]
        if team == "2 teams":
            continue
        value_2026[(team, norm(row[2]))] = float(row[8])
for fname, pos_col, usage_col, allowed_pos in [
    ("sis_player_passdef_2026_thru_wk2.csv", "Pos.", "Cov. Snaps", {"CB", "S", "LB"}),
    ("sis_player_rundef_2026_thru_wk2.csv", "Pos.", "Rush Snaps", {"CB", "S", "LB", "DE", "DT"}),
    ("sis_player_passrush_2026_thru_wk2.csv", "Pos.", "Pass Rushes", {"DE", "DT", "LB"}),
]:
    with open(os.path.join(HERE, "..", "data", fname)) as f:
        for row in csv.DictReader(f):
            team, pos = row["Team"], row[pos_col]
            if team == "2 teams" or pos not in allowed_pos:
                continue
            key = (team, norm(row["Player"]))
            value_2026[key] = value_2026.get(key, 0.0) + float(row["Points Above Avg"])

# --- Games played 2026, from the real per-game snap-count file (one row = one game appeared in).
games_2026 = defaultdict(int)
with open(os.path.join(HERE, "..", "data", "nfl_snap_counts_2026_thru_wk2.csv")) as f:
    for row in csv.DictReader(f):
        games_2026[(row["Team"], norm(row["Player"]))] += 1

def value_per_game(team_short, name):
    key = (team_short, norm(name))
    if key not in value_2026:
        return 0.0
    games = games_2026.get(key, 0)
    return value_2026[key] / games if games else 0.0

# --- Pair each tiered, notable injury with the next healthy player at that position (by 2025
# season usage rank, the same ranking §06 already shows), then price the swap in 2026-to-date
# points-per-game.
tier_reference = json.load(open(os.path.join(HERE, "week3_skill_value_tiers.json")))
notable = json.load(open(os.path.join(HERE, "week3_injuries_notable.json")))

PER_PLAYER_CAP = 1.0
PER_SIDE_CAP = 2.0

adjustments = {}
for full_team, plist in notable.items():
    short = TEAM_SHORT[full_team]
    injured_by_pos = defaultdict(list)  # pos -> [(rank, name)]
    injured_names_by_pos = defaultdict(set)
    for p in plist:
        if "tier" not in p:
            continue
        pos = p["pos"]
        rank = int(re.search(r"\d+", p["tier"]).group())
        injured_by_pos[pos].append((rank, p["name"]))
        injured_names_by_pos[pos].add(norm(p["name"]))

    off_total, def_total, detail = 0.0, 0.0, []
    for pos, injured in injured_by_pos.items():
        injured.sort()  # process the most senior injury first
        full_list = tier_reference.get(short, {}).get(pos, [])  # rank order, index 0 = rank 1
        used = set()
        for rank, inj_name in injured:
            # The replacement is whoever moves into THIS role: the next healthy player *below*
            # this one on the depth chart, not the team's best available player overall (a
            # deep-bench RB3 going down doesn't hand his snaps to a healthy RB1 -- RB1 was
            # already playing). Search forward from this player's own rank, skipping anyone
            # already claimed as another injury's replacement so simultaneous injuries at the
            # same position don't double-count the same fill-in player.
            repl_name = None
            for name, usage, paa in full_list[rank:]:
                nk = norm(name)
                if nk in injured_names_by_pos[pos] or nk in used:
                    continue
                repl_name = name
                used.add(nk)
                break
            inj_vpg = value_per_game(short, inj_name)
            repl_vpg = value_per_game(short, repl_name) if repl_name else 0.0
            if pos in OFFENSE_POS:
                impact = max(-PER_PLAYER_CAP, min(PER_PLAYER_CAP, repl_vpg - inj_vpg))
                off_total += impact
            else:
                impact = max(-PER_PLAYER_CAP, min(PER_PLAYER_CAP, inj_vpg - repl_vpg))
                def_total += impact
            detail.append(dict(pos=pos, injured=inj_name, tier=f"{pos}{rank}", replacement=repl_name,
                                injured_vpg=round(inj_vpg, 2), replacement_vpg=round(repl_vpg, 2),
                                impact=round(impact, 2)))

    off_adj = max(-PER_SIDE_CAP, min(PER_SIDE_CAP, off_total))
    def_adj = max(-PER_SIDE_CAP, min(PER_SIDE_CAP, def_total))
    if off_adj or def_adj or detail:
        adjustments[full_team] = dict(off_adj=round(off_adj, 2), def_adj=round(def_adj, 2), detail=detail)

json.dump(adjustments, open(os.path.join(HERE, "week3_injury_adjustments.json"), "w"), indent=2)

nonzero = {t: a for t, a in adjustments.items() if a["off_adj"] or a["def_adj"]}
print(f"Computed injury point-adjustments for {len(adjustments)} teams with a tiered injury; "
      f"{len(nonzero)} have a nonzero net adjustment after caps.")
for t, a in sorted(nonzero.items(), key=lambda kv: -abs(kv[1]["off_adj"]) - abs(kv[1]["def_adj"])):
    print(f"  {t:24s} off_adj={a['off_adj']:+.2f}  def_adj={a['def_adj']:+.2f}")
    for d in a["detail"]:
        if d["impact"]:
            print(f"      {d['tier']:5s} {d['injured']:22s} (vpg={d['injured_vpg']:+.2f}) -> "
                  f"{str(d['replacement']):22s} (vpg={d['replacement_vpg']:+.2f})  impact={d['impact']:+.2f}")
