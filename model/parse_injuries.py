import re, json, os

HERE = os.path.dirname(os.path.abspath(__file__))

text = open(os.path.join(HERE, "week3_injuries_raw.txt")).read()

TEAMS = ["Arizona Cardinals","Atlanta Falcons","Baltimore Ravens","Buffalo Bills",
"Carolina Panthers","Chicago Bears","Cincinnati Bengals","Cleveland Browns",
"Dallas Cowboys","Denver Broncos","Detroit Lions","Green Bay Packers",
"Houston Texans","Indianapolis Colts","Jacksonville Jaguars","Kansas City Chiefs",
"Las Vegas Raiders","Los Angeles Chargers","Los Angeles Rams","Miami Dolphins",
"Minnesota Vikings","New England Patriots","New Orleans Saints","New York Giants",
"New York Jets","Philadelphia Eagles","Pittsburgh Steelers","San Francisco 49ers",
"Seattle Seahawks","Tampa Bay Buccaneers","Tennessee Titans","Washington Commanders"]

# split into per-team chunks using team names as anchors (order in doc may differ from TEAMS list order,
# so find all anchor positions first)
anchors = []
for t in TEAMS:
    idx = text.find(t + "NAMEPOS")
    if idx == -1:
        print("MISSING TEAM HEADER:", t)
        continue
    anchors.append((idx, t))
anchors.sort()

chunks = {}
for i, (idx, t) in enumerate(anchors):
    start = idx + len(t) + len("NAMEPOSEST. RETURN DATESTATUSCOMMENT")
    end = anchors[i+1][0] if i+1 < len(anchors) else len(text)
    chunks[t] = text[start:end]

POS = r"(?:QB|RB|WR|TE|OT|OG|OL|DE|DT|LB|CB|S|G|C|FB|K|P|DL|EDGE)"
DATE = r"(?:[A-Z][a-z]{2} \d{1,2}|-)"
STATUS = r"(?:Questionable|Doubtful|Out|Injured Reserve)"
PLAYER_RE = re.compile(rf"([A-Z][A-Za-z.'\-]*(?: [A-Z][A-Za-z.'\-]*)*(?: Jr\.| Sr\.| III| II| IV)?)({POS})({DATE})({STATUS})")

WILL_NOT_PLAY = {"Doubtful", "Out", "Injured Reserve"}

# A player's name can pick up a trailing word bled in from the previous player's comment text
# (no delimiter between "...against the Packers." and "Cooper Rush..."). Only strip a leading
# "Word." when Word is 3+ letters -- short ones (A., T.J.) are real initials, not artifacts.
def clean_name(name):
    m = re.match(r"^([A-Za-z]+)\.([A-Z].+)$", name)
    if m and len(m.group(1)) >= 3 and " " in m.group(2):
        return m.group(2)
    return name

report = {}
for t, chunk in chunks.items():
    players = []
    for m in PLAYER_RE.finditer(chunk):
        name, pos, date, status = m.groups()
        players.append(dict(name=clean_name(name.strip()), pos=pos, status=status,
                             will_play=status not in WILL_NOT_PLAY))
    report[t] = players

total_players = sum(len(v) for v in report.values())
total_out = sum(1 for v in report.values() for p in v if not p["will_play"])
print(f"Parsed {total_players} player entries across {len(report)} teams, {total_out} ruled OUT (Doubtful/Out/IR)")
json.dump(report, open(os.path.join(HERE, "week3_injuries_parsed.json"),"w"), indent=2)

# Filtered to positions that plausibly move a line -- this is what the dashboard consumes.
# No depth-chart rank is available, so a WR1 and a WR4 both just show as "WR out".
NOTABLE_POS = {"QB", "RB", "WR", "TE", "OT", "OG", "C", "CB"}
notable = {}
for t, players in report.items():
    notable[t] = [dict(name=p["name"], pos=p["pos"], status=p["status"])
                  for p in players if not p["will_play"] and p["pos"] in NOTABLE_POS]
notable_total = sum(len(v) for v in notable.values())
print(f"{notable_total} notable (QB/RB/WR/TE/OT/OG/C/CB) entries ruled out")
json.dump(notable, open(os.path.join(HERE, "week3_injuries_notable.json"),"w"), indent=2)
