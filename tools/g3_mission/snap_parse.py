"""summarise g3_frame_snap output (same pass as s6768, now a file).
usage: snap_parse.py SNAP_TXT  -> npc rows, point diffs, first obj diff / retail-only / disallowed word tick."""
import re, sys
SNAP_OK = {2, 3, 4, 5, 6, 9}
GLOB_OK = {7, 8, 18} | set(range(20, 32))
tick = None; rows = pdiff = 0
first = {}
def note(k):
    first.setdefault(k, tick)
for line in open(sys.argv[1]):
    m = re.match(r'tick\s+(\d+)', line)
    if m:
        tick = int(m.group(1))
        w = re.search(r'snap diff words \[([^\]]*)\]', line)
        if w and w.group(1).strip() and set(int(x) for x in w.group(1).split(',')) - SNAP_OK:
            note('disallowed-snap')
        continue
    s = line.strip()
    if s.startswith('glob'):
        w = re.search(r'diff words \[([^\]]*)\]', s)
        if w and w.group(1).strip() and set(int(x) for x in w.group(1).split(',')) - GLOB_OK:
            note('disallowed-glob')
    elif s.startswith('npc') and 'retail only' in s:
        note('retail-only')
    elif s.startswith('npc') and 'port only' in s:
        note('port-only')
    elif s.startswith('npc'):
        rows += 1
        m = re.search(r'pt R\[([^\]]*)\] P\[([^\]]*)\]', s)
        if m and m.group(1) != m.group(2):
            pdiff += 1; note('point')
        if not s.endswith('obj diff []'):
            note('obj')
print(f'last tick {tick} npc rows {rows} point diffs {pdiff}')
for k in ('point', 'obj', 'retail-only', 'port-only', 'disallowed-snap', 'disallowed-glob'):
    print(f'first {k}: {first.get(k)}')
