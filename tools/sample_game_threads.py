#!/usr/bin/env python3
"""s6834: summarise a macOS `sample` call-tree file per thread: for each guest ([Game] ...) and runtime thread
(VI / SP Task / Gfx / Timer / AUDIOMGR), print the heaviest leaf path's innermost frames. Used by
tools/boot_freeze_hunt.sh to name where every game thread sits when the RDP frame counter stops.
Usage: sample_game_threads.py <sample.txt> [frames=8]"""
import re, sys

path = sys.argv[1]
depth = int(sys.argv[2]) if len(sys.argv) > 2 else 8
WANT = re.compile(r"\[Game\]|VI Thread|SP Task|Gfx Thread|Timer Thread|RT64 Present|main-thread")
HDR = re.compile(r"^\s+(\d+) Thread_\d+(.*)$")
FRAME = re.compile(r"^([\s+!:|]*)(\d+) (.+?)  \(in ([^)]+)\)")

threads, cur = [], None
for line in open(path, errors="replace"):
    if line.startswith("Total number in stack"):
        break
    m = HDR.match(line)
    if m:
        cur = {"name": m.group(2).strip(": ") or "(unnamed)", "rows": []}
        threads.append(cur)
        continue
    if cur is None:
        continue
    f = FRAME.match(line)
    if f:
        cur["rows"].append((len(f.group(1)), int(f.group(2)), f.group(3).strip(), f.group(4)))

for t in threads:
    if not WANT.search(t["name"]):
        continue
    # heaviest path: from the top, at each level follow the child with the largest count
    rows, path_, i = t["rows"], [], 0
    while i < len(rows):
        ind, n, fn, mod = rows[i]
        path_.append((n, fn, mod))
        sub = []
        j = i + 1
        while j < len(rows) and rows[j][0] > ind:
            sub.append(j)
            j += 1
        kids = [k for k in sub if rows[k][0] == min(rows[s][0] for s in sub)] if sub else []
        best = max(kids, key=lambda k: rows[k][1]) if kids else None
        if best is None:
            break
        i = best
    print(f"== {t['name']}  ({len(rows)} frames)")
    for n, fn, mod in path_[-depth:]:
        print(f"   {n:6d} {fn[:110]}{'' if mod == 'RogueSquadron64Recomp' else '  [' + mod + ']'}")
