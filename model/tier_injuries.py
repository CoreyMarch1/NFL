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

# --- Build 2025 season skill-position value (real PAA, real season -- the basis for depth-chart rank) ---
receiving = {}  # (short_team, norm_name) -> (display_name, pos, paa)
with open(os.path.join(HERE, "..", "data", "sis_receiving_2025.csv")) as f:
    for row in csv.DictReader(f):
        team = row["Team"]
        if team == "2 teams":
            continue
        receiving[(team, norm(row["Player"]))] = (row["Player"], row["Pos"], float(row["Points Above Avg"]))

rushing = {}  # (short_team, norm_name) -> paa
with open(os.path.join(HERE, "..", "data", "sis_rushing_2025.csv")) as f:
    for row in csv.DictReader(f):
        team = row["Team"]
        if team == "2 teams":
            continue
        rushing[(team, norm(row["Player"]))] = float(row["Points Above Avg"])

# value = receiving PAA, plus rushing PAA too for anyone tagged RB in the receiving file
# (a modern RB's rushing work is usually the bigger half of their value; WR/TE rushing PAA is
# jet-sweep noise and is left out).
players = {}  # short_team -> list of (display_name, pos, value)
for (team, nkey), (name, pos, paa_rec) in receiving.items():
    value = paa_rec
    if pos == "RB" and (team, nkey) in rushing:
        value += rushing[(team, nkey)]
    players.setdefault(team, []).append((name, nkey, pos, value))
# pure rushers with zero receiving value don't show up in the receiving file at all -- add them
# under RB as long as they're not a QB (QBs are mixed into the same rushing table).
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
for (team, nkey), paa_rush in rushing.items():
    if nkey in QB_NAMES or (team, nkey) in receiving:
        continue
    name = None
    # recover a display name from the rushing csv directly
    players.setdefault(team, []).append((None, nkey, "RB", paa_rush))

# recover display names for the rushing-only additions
rushing_names = {}
with open(os.path.join(HERE, "..", "data", "sis_rushing_2025.csv")) as f:
    for row in csv.DictReader(f):
        rushing_names[(row["Team"], norm(row["Player"]))] = row["Player"]
for team, plist in players.items():
    for i, (name, nkey, pos, value) in enumerate(plist):
        if name is None:
            plist[i] = (rushing_names.get((team, nkey), nkey), nkey, pos, value)

# Global name -> (2025 team, pos, value) index, for players who changed teams since 2025 and
# so don't show up under their new team's roster in the SIS files above.
global_index = {}
for team, plist in players.items():
    for name, nkey, pos, value in plist:
        if pos in ("WR", "TE", "RB"):
            global_index[nkey] = (team, pos, value)

def build_tiers(players):
    tiers = {}  # short_team -> {norm_name: "WR1"/"RB2"/...}
    tier_reference = {}  # short_team -> {"WR": [names in order], ...}
    for team, plist in players.items():
        by_pos = {}
        for name, nkey, pos, value in plist:
            if pos in ("WR", "TE", "RB"):
                by_pos.setdefault(pos, []).append((name, nkey, value))
        tiers[team] = {}
        tier_reference[team] = {}
        for pos, plist2 in by_pos.items():
            plist2.sort(key=lambda x: -x[2])
            tier_reference[team][pos] = [(n, round(v, 2)) for n, _, v in plist2]
            for i, (name, nkey, value) in enumerate(plist2):
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
        if tier:
            p["tier"] = tier
            continue
        # not on this team's 2025 roster in the data -- check if they simply changed teams
        # since 2025 (a real, valuable player elsewhere), and if so, slot their 2025 value into
        # the CURRENT team's depth chart to estimate a tier, flagged with a trailing "*".
        g = global_index.get(norm(p["name"]))
        if g and g[0] != short:
            old_team, pos, value = g
            merged = dict(players)
            merged[short] = list(players.get(short, [])) + [(p["name"], norm(p["name"]), pos, value)]
            tmp_tiers, _ = build_tiers({short: merged[short]})
            p["tier"] = tmp_tiers[short][norm(p["name"])] + "*"
            traded.append((full_team, p["name"], old_team, round(value, 2)))
        else:
            misses.append((full_team, p["name"], p["pos"]))

json.dump(notable, open(os.path.join(HERE, "week3_injuries_notable.json"), "w"), indent=2)

tagged = sum(1 for plist in notable.values() for p in plist if "tier" in p)
print(f"Tagged {tagged} RB/WR/TE injury entries with a depth-chart tier from 2025 season value.")
print(f"{len(traded)} of those are estimated from a different 2025 team (tier marked with *):")
for t in traded:
    print("  ", t)
print(f"{len(misses)} RB/WR/TE entries had no 2025 season value on record anywhere (rookie or minimal-usage player):")
for m in misses:
    print("  ", m)
