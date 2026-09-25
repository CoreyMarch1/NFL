import csv, json, os, re

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

# --- Depth-chart tiers are a ROLE/usage read (targets, rush attempts), not a value read.
# PAA measures how efficient a player was per opportunity -- a low-volume backup can out-PAA
# the actual starter, which would mislabel him as "WR1". Usage (who actually gets the touches)
# is what "depth chart" means, so it's the sort key; PAA is kept only as separate context.
receiving = {}  # (team, norm_name) -> (display_name, pos, targets, paa)
with open(os.path.join(HERE, "..", "data", "sis_receiving_2025.csv")) as f:
    for row in csv.DictReader(f):
        team = row["Team"]
        if team == "2 teams":
            continue
        receiving[(team, norm(row["Player"]))] = (row["Player"], row["Pos"], int(row["Tgts"]), float(row["Points Above Avg"]))

rushing = {}  # (team, norm_name) -> (display_name, att, paa)
with open(os.path.join(HERE, "..", "data", "sis_rushing_2025.csv")) as f:
    for row in csv.DictReader(f):
        team = row["Team"]
        if team == "2 teams":
            continue
        rushing[(team, norm(row["Player"]))] = (row["Player"], int(row["Att"]), float(row["Points Above Avg"]))

# Position lookup used to keep a jet-sweep WR (a handful of rush attempts, no meaningful role at
# RB) out of the RB group -- some of these players have too few 2025 targets to make the
# receiving-value cut but still show up in the 2026-to-date file, or in the injury report itself
# (both of which carry an official position), even with zero receiving-value data anywhere.
known_pos = {(team, nkey): pos for (team, nkey), (_, pos, _, _) in receiving.items()}
with open(os.path.join(HERE, "..", "data", "sis_receiving_2026_thru_wk2.csv")) as f:
    for row in csv.DictReader(f):
        team = row["Team"]
        if team == "2 teams":
            continue
        known_pos.setdefault((team, norm(row["Player"])), row["Pos"])
parsed_injuries = json.load(open(os.path.join(HERE, "week3_injuries_parsed.json")))
for full_team, plist in parsed_injuries.items():
    short = TEAM_SHORT[full_team]
    for p in plist:
        known_pos.setdefault((short, norm(p["name"])), p["pos"])

QB_NAMES = {norm(n) for n in [
    "Bo Nix","Matthew Stafford","Caleb Williams","Jared Goff","Patrick Mahomes","Jordan Love",
    "Dak Prescott","Jalen Hurts","C.J. Stroud","Drake Maye","Bryce Young","Trevor Lawrence",
    "Jacoby Brissett","Josh Allen","Brock Purdy","Daniel Jones","Justin Herbert","Tyler Shough",
    "Baker Mayfield","Aaron Rodgers","Jaxson Dart","Lamar Jackson","Joe Burrow","Jayden Daniels",
    "Cam Ward","Carson Wentz","Kirk Cousins","Geno Smith","Cooper Rush","Michael Penix Jr.",
    "Kyler Murray","Marcus Mariota","Malik Willis","Tyrod Taylor","Trey Lance","Riley Leonard",
    "Joe Milton III","Joe Flacco","Tua Tagovailoa","Justin Fields","Russell Wilson",
    "Dillon Gabriel","Davis Mills","Shedeur Sanders","Spencer Rattler","Jake Browning",
    "Mac Jones","J.J. McCarthy","Brady Cook","Josh Johnson",
]}

# players: short_team -> list of (display_name, norm_name, pos, usage, paa)
# usage = targets for WR/TE; rush attempts + targets ("touches") for RB.
players = {}
for (team, nkey), (name, pos, tgts, paa_rec) in receiving.items():
    usage, paa = tgts, paa_rec
    if pos == "RB" and (team, nkey) in rushing:
        _, att, paa_rush = rushing[(team, nkey)]
        usage += att
        paa += paa_rush
    players.setdefault(team, []).append((name, nkey, pos, usage, paa))
# pure rushers with zero targets don't show up in the receiving file -- add them under RB, unless
# the position lookup says they're actually a WR/TE getting jet-sweep touches (rushing table mixes
# in QBs and gadget WRs alike, so exclude known QB names and confirmed non-RBs).
for (team, nkey), (name, att, paa) in rushing.items():
    if nkey in QB_NAMES or (team, nkey) in receiving:
        continue
    if known_pos.get((team, nkey), "RB") != "RB":
        continue
    players.setdefault(team, []).append((name, nkey, "RB", att, paa))

# Global name -> (2025 team, pos, usage, paa), for players who changed teams since 2025 and so
# don't show up under their new team's roster in the files above.
global_index = {}
for team, plist in players.items():
    for name, nkey, pos, usage, paa in plist:
        if pos in ("WR", "TE", "RB"):
            global_index[nkey] = (team, pos, usage, paa)

def build_tiers(players):
    tiers = {}  # short_team -> {norm_name: "WR1"/"RB2"/...}
    tier_reference = {}  # short_team -> {"WR": [(name, usage, paa) in tier order], ...}
    for team, plist in players.items():
        by_pos = {}
        for name, nkey, pos, usage, paa in plist:
            if pos in ("WR", "TE", "RB"):
                by_pos.setdefault(pos, []).append((name, nkey, usage, paa))
        tiers[team] = {}
        tier_reference[team] = {}
        for pos, plist2 in by_pos.items():
            plist2.sort(key=lambda x: -x[2])  # sort by usage, not PAA
            tier_reference[team][pos] = [(n, u, round(v, 2)) for n, _, u, v in plist2]
            for i, (name, nkey, usage, paa) in enumerate(plist2):
                tiers[team][nkey] = f"{pos}{i+1}"
    return tiers, tier_reference

tiers, tier_reference = build_tiers(players)
json.dump(tier_reference, open(os.path.join(HERE, "week3_skill_value_tiers.json"), "w"), indent=2)

# --- Annotate the notable-injuries feed with a tier where we can find one ---
notable = json.load(open(os.path.join(HERE, "week3_injuries_notable.json")))
misses = []
traded = []
for full_team, plist in notable.items():
    short = TEAM_SHORT[full_team]
    for p in plist:
        if p["pos"] not in ("RB", "WR", "TE"):
            continue
        tier = tiers.get(short, {}).get(norm(p["name"]))
        if tier and tier.startswith(p["pos"]):
            p["tier"] = tier
            continue
        # not on this team's 2025 roster in the data -- check if they simply changed teams
        # since 2025 (a real player elsewhere), and if so, slot their 2025 usage into the
        # CURRENT team's depth chart to estimate a tier, flagged with a trailing "*". Also
        # guards against a rushing-only entry whose true position (per the injury report itself)
        # doesn't match the RB default a "pure rusher" with no receiving record was given.
        g = global_index.get(norm(p["name"]))
        if g and g[1] == p["pos"] and g[0] != short:
            old_team, pos, usage, paa = g
            merged_list = list(players.get(short, [])) + [(p["name"], norm(p["name"]), pos, usage, paa)]
            tmp_tiers, _ = build_tiers({short: merged_list})
            p["tier"] = tmp_tiers[short][norm(p["name"])] + "*"
            traded.append((full_team, p["name"], old_team, usage))
        else:
            misses.append((full_team, p["name"], p["pos"]))

json.dump(notable, open(os.path.join(HERE, "week3_injuries_notable.json"), "w"), indent=2)

tagged = sum(1 for plist in notable.values() for p in plist if "tier" in p)
print(f"Tagged {tagged} RB/WR/TE injury entries with a depth-chart tier from 2025 season usage (targets/touches).")
print(f"{len(traded)} of those are estimated from a different 2025 team (tier marked with *):")
for t in traded:
    print("  ", t)
print(f"{len(misses)} RB/WR/TE entries had no 2025 season usage on record anywhere (rookie or minimal-usage player):")
for m in misses:
    print("  ", m)
