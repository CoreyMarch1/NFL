import csv, os
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))

TEAM_ID = {
    1: "Cardinals", 2: "Falcons", 3: "Ravens", 4: "Bills", 5: "Panthers", 6: "Bears",
    7: "Bengals", 8: "Browns", 9: "Cowboys", 10: "Broncos", 11: "Lions", 12: "Packers",
    13: "Texans", 14: "Colts", 15: "Jaguars", 16: "Chiefs", 17: "Dolphins", 18: "Vikings",
    19: "Patriots", 20: "Saints", 21: "Giants", 22: "Jets", 23: "Raiders", 24: "Eagles",
    25: "Steelers", 26: "Chargers", 27: "Seahawks", 28: "49ers", 29: "Rams",
    30: "Buccaneers", 31: "Titans", 32: "Commanders",
}
# Confirmed against the file by cross-referencing player names already known from other SIS
# tables (e.g. TeamId 1 is >90% Jacoby Brissett/Paris Johnson Jr./Trey McBride -- all Cardinals).
POS_ID = {
    1: "QB", 2: "RB", 3: "FB", 4: "WR", 5: "TE", 6: "OT", 7: "OG", 8: "C", 9: "DE",
    10: "DT", 11: "LB", 12: "CB", 13: "S", 14: "K", 15: "P", 16: "LS",
}

src = "/root/.claude/uploads/60adbde6-e2ae-5114-a91c-c73bbab8e423/fbee2007-NFL_Snap_Counts.xlsx"
wb = openpyxl.load_workbook(src, data_only=True)
ws = wb.active

# TeamOffSnaps/TeamDefSnaps/*Pct columns are unreliable (spot-checked against the ~180 rows
# where they ARE populated: those values run ~4x a realistic single-game snap count, versus
# max(OffSnaps) per team-game landing at a normal 50-70 -- almost certainly a season-cumulative
# figure mistakenly attached to one row). Dropped; only the raw per-player counts are trustworthy.
rows_out = []
for row in ws.iter_rows(min_row=2, values_only=True):
    season, week, teamid, gameid, playerid, name, posid, offsnaps = row[:8]
    defsnaps, stsnaps, totalsnaps = row[10], row[13], row[16]
    if season != 2026:
        continue
    rows_out.append([
        int(week), TEAM_ID[int(teamid)], name, POS_ID.get(int(posid), f"POS{int(posid)}"),
        int(offsnaps), int(defsnaps) if defsnaps != "NULL" else 0,
        int(stsnaps) if stsnaps != "NULL" else 0, int(totalsnaps),
    ])

out_path = os.path.join(HERE, "..", "data", "nfl_snap_counts_2026_thru_wk2.csv")
with open(out_path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Week", "Team", "Player", "Pos", "OffSnaps", "DefSnaps", "STSnaps", "TotalSnaps"])
    w.writerows(rows_out)

print(f"wrote {len(rows_out)} rows to {out_path}")
