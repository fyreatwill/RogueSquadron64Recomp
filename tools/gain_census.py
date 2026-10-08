"""s4220: count active-voice rows whose voice-0 gain words (first 4 words of `first=`, record +0x00..+0x0C) are nonzero.
Usage: gain_census.py <port s4218 log> <retail oracle log>"""
import re, sys
from collections import defaultdict

def rows(path, tag):
    for line in open(path, errors="replace"):
        if not line.startswith(tag):
            continue
        m = re.search(r"active=(\d+).*first=([0-9A-F,]+)", line)
        if not m:
            continue
        ph = re.search(r"phase=(\d+)", line)
        w = re.search(r"width=(\d+)", line)
        key = ("phase" + ph.group(1)) if ph else ("w" + (w.group(1) if w else "?"))
        yield key, int(m.group(1)), m.group(2).split(",")[:4]

for path, tag in ((sys.argv[1], "[s4218-act]"), (sys.argv[2], "[audio-objects-frame]")):
    tot = defaultdict(lambda: [0, 0])
    for key, active, g in rows(path, tag):
        if active == 0:
            continue
        tot[key][0] += 1
        tot[key][1] += any(int(x, 16) for x in g)
    print(tag, {k: f"{v[1]}/{v[0]} nonzero-gain" for k, v in sorted(tot.items())})
