#!/usr/bin/env python3
"""s6751 G3: align guest rand() call sequences, retail (rs64_oracle --exec-trace, $ra = jal+8) vs port
(ROGUESQ_RAND_TRACE, jal address). Both start at the same seed poke, so call index i returns the same value in
both arms; the first index whose caller differs is where the game logic diverges.
Marker rows (port site / retail pc = a probe PC, e.g. 0x8006BEC8 entry with $a3, 0x8006C018 gate $v0) are split off
and listed per game frame around the divergence for the --npc-site caller.
usage: g3_rand_align.py RETAIL_ORACLE_LOG PORT_RAND_TXT [context]"""
import collections, sys

RAND = 0x80003430
MARKERS = {0x8006BEC8: "npc_entry a3", 0x8006C018: "dc34_gate v0"}

def load(path, retail):
    rows, marks = [], []
    for l in open(path, errors="replace"):
        if retail:
            if not l.startswith("[xtrace] "):
                continue
            f = l.split()[1:]
        else:
            f = l.split()
        if len(f) < 4:
            continue
        frame, site, val = int(f[1]), int(f[2], 16), int(f[3], 16)
        if retail and len(f) >= 7:
            pc = int(f[4][3:], 16)
            if pc != RAND:
                marks.append((len(rows), frame, pc, int(f[6 if pc == 0x8006BEC8 else 5][3:], 16)))
                continue
        elif not retail and site in MARKERS:
            marks.append((len(rows), frame, site, val))
            continue
        rows.append((len(rows), frame, site - 8 if retail else site, val))
    return rows, marks

(r, rm), (p, pm) = load(sys.argv[1], True), load(sys.argv[2], False)
ctx = int(sys.argv[3]) if len(sys.argv) > 3 else 12
n = min(len(r), len(p))
print(f"retail calls {len(r)}  port calls {len(p)}  compared {n}")
bad_seed = next((i for i in range(n) if r[i][3] != p[i][3]), None)
print("first seed mismatch:", bad_seed)
div = next((i for i in range(n) if r[i][2] != p[i][2]), None)
print("first caller mismatch at index", div)
if div is not None:
    r0, p0 = r[0][1], p[0][1]
    for i in range(max(0, div - ctx), min(n, div + ctx)):
        mark = "  " if r[i][2] == p[i][2] else "!="
        print(f"{mark} {i:6d}  retail vi+{r[i][1]-r0:5d} {r[i][2]:08x}   port us+{p[i][1]-p0:5d} {p[i][2]:08x}")
    # per-frame call-site multiset up to the divergence frame, frame by frame
    def frames(rows, upto):
        d = collections.OrderedDict()
        for i, fr, s, _ in rows[:upto]:
            d.setdefault(fr, []).append(s)
        return list(d.values())
    fr_r, fr_p = frames(r, div + 1), frames(p, div + 1)
    print(f"frames with calls before divergence: retail {len(fr_r)} port {len(fr_p)}")
    print("calls per frame (first 12) retail:", [len(x) for x in fr_r[:12]])
    print("calls per frame (first 12) port:  ", [len(x) for x in fr_p[:12]])
    print("last 4 frames before divergence, retail:", [len(x) for x in fr_r[-4:]], "port:", [len(x) for x in fr_p[-4:]])

    if rm or pm:
        # one line per game frame: NPC (low 16 bits of $a3) : gate result (- = gate not evaluated), * = called rand
        # at 0x8006C0FC/0x8006C110 (with its call index). Marker rows keep their file (execution) order.
        for name, rows, marks, f0 in (("retail", r, rm, r0), ("port", p, pm, p0)):
            lo, hi = rows[max(0, div - 30)][1], rows[min(len(rows) - 1, div + 20)][1]
            ev = [(m[0], 0, k, m) for k, m in enumerate(marks) if lo <= m[1] <= hi]
            ev += [(x[0], 1, 0, x) for x in rows if lo <= x[1] <= hi and x[2] in (0x8006C0FC, 0x8006C110)]
            ev.sort(key=lambda e: (e[0], e[1], e[2]))
            print(f"--- {name}: per frame NPC:gate (* = rand at 0x8006C0FC/0x8006C110, #index)")
            line, cur = {}, None
            for _, kind, _, x in ev:
                fr = x[1] - f0
                line.setdefault(fr, [])
                if kind == 0 and x[2] == 0x8006BEC8:
                    line[fr].append(f"{x[3] & 0xFFFF:04x}:-")
                elif kind == 0 and line[fr]:
                    line[fr][-1] = line[fr][-1][:-1] + str(x[3] & 0xFF)
                elif kind == 1 and line[fr]:
                    line[fr][-1] += f"*#{x[0]}"
            for fr in sorted(line):
                print(f"   f+{fr:4d}  " + " ".join(line[fr]))
