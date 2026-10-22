#!/usr/bin/env python3
"""s5850: tabulate the distinct class-1 (+0x70==1) NPC spawn descriptors from a run log carrying `[spawn1] ... id= w=` lines
(tools/apply_s5812_npc_spawn_class.py) and mark which ones were torn down (`[ctr1] set ... id=0x..` lines from apply_s5809).
usage: dump_lv0_objective_targets.py RUN.LOG"""
import re, struct, sys
seen, killed, rep = {}, set(), {}
for l in open(sys.argv[1], errors="replace"):
    m = re.match(r"\[spawn1\] #\d+ desc=0x(\w+) npc=0x\w+ id=0x(\w+) w=(.*)", l)
    if m:
        rep[m.group(1)] = rep.get(m.group(1), 0) + 1
        seen.setdefault(m.group(1), (int(m.group(2), 16), [int(x, 16) for x in m.group(3).split()]))
    m = re.match(r"\[ctr1\] set #\d+ id=0x(\w+) val=1 a2=1", l)
    if m: killed.add(int(m.group(1), 16))
fl = lambda w: struct.unpack(">f", struct.pack(">I", w))[0]
print("distinct class-1 descriptors: %d, torn down (counter-1 sets): %d" % (len(seen), len(killed & {v[0] for v in seen.values()})))
print("desc      boolid kill spawns grp  posx posy posz")
for d, (i, w) in sorted(seen.items(), key=lambda x: x[1][0]):
    print("%s %#5x  %s  %d  %d  %.0f %.0f %.0f" % (d, i, "K" if i in killed else "-", rep[d], w[0x80 // 4], fl(w[4]), fl(w[5]), fl(w[6])))
