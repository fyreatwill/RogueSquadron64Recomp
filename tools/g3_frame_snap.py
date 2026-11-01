#!/usr/bin/env python3
"""s6752 G3: compare per-game-frame state, retail (rs64_oracle --exec-trace + RS64_XTRACE_MEM) vs port
(ROGUESQ_RAND_TRACE + ROGUESQ_XTRACE_MEM), from the same rngSeed poke.
Rows used: frame ticks TICKS (after timeSnapshotFiller; dumps = snapshot struct at sp+0x10 and globals), NPC entry
0x8006BEC8 (a3 = NPC), gate call 0x8006C010 (dumps = $a0 object, NPC point at sp+0x18, globals) and gate result
0x8006C018 (v0). Tick k in one arm is paired with tick k in the other; within a tick, gate calls are keyed by NPC.
usage: g3_frame_snap.py RETAIL_ORACLE_LOG PORT_RAND_TXT [ticks=30]"""
import struct, sys

TICKS = {0x800AF374, 0x800C6674, 0x800FA730}  # jal timeSnapshotFiller + 8 (cinematic, phase accumulator, runInMissionFrame)
ENTRY, GCALL, GRES = 0x8006BEC8, 0x8006C010, 0x8006C018


def f32(w):
    return struct.unpack(">f", struct.pack(">I", w))[0]


def parse(path, retail):
    ticks, cur, npc = [], None, None
    for l in open(path, errors="replace"):
        if retail:
            if not l.startswith("[xtrace] "):
                continue
            f = l.split()[1:]
            pc = int(f[4][3:], 16)
            v0, a3, ra = int(f[5][3:], 16), int(f[6][3:], 16), int(f[2], 16)
            mem = f[7:]
        else:
            f = l.split()
            if len(f) < 4:
                continue
            pc, v0 = int(f[2], 16), int(f[3], 16)
            a3, ra, mem = v0, pc, f[4:]
        dumps = [[int(x, 16) for x in m.split(":")[1].split(",")] for m in mem if m.startswith("m=")]
        if pc in TICKS:
            if ra != pc:  # other overlay's code at the same VA ($ra = jal+8 only for the snapshot return)
                continue
            cur = {"vi": int(f[1]), "pc": pc, "dumps": dumps, "gates": {}, "order": []}
            ticks.append(cur)
        elif cur is None:
            continue
        elif pc == ENTRY:
            npc = a3
        elif pc == GCALL:
            cur["gates"][npc] = {"dumps": dumps, "res": None}
            cur["order"].append(npc)
        elif pc == GRES and npc in cur["gates"]:
            cur["gates"][npc]["res"] = v0 & 0xFF
    return ticks


def fmt(ws, floats=True):
    return " ".join(f"{f32(w):.4g}" if floats else f"{w:08x}" for w in ws)


r, p = parse(sys.argv[1], True), parse(sys.argv[2], False)
n = int(sys.argv[3]) if len(sys.argv) > 3 else 30
print(f"ticks retail {len(r)} port {len(p)}")
for k in range(min(n, len(r), len(p))):
    a, b = r[k], p[k]
    sa, sb = a["dumps"][0] if a["dumps"] else [], b["dumps"][0] if b["dumps"] else []
    diff = [i for i in range(min(len(sa), len(sb))) if sa[i] != sb[i]]
    print(f"tick {k:3d} {a['pc']:08x}/{b['pc']:08x} vi {a['vi']}/{b['vi']}  snap diff words {diff}")
    print(f"   R snap {fmt(sa, False)}\n   P snap {fmt(sb, False)}")
    if len(a["dumps"]) > 1 and len(b["dumps"]) > 1:
        ga, gb = a["dumps"][1], b["dumps"][1]
        gd = [i for i in range(min(len(ga), len(gb))) if ga[i] != gb[i]]
        print(f"   glob 8011A880 diff words {gd[:16]}")
    for npc in a["order"]:
        ga, gb = a["gates"][npc], b["gates"].get(npc)
        if gb is None:
            print(f"   npc {npc:08x}: retail only, res {ga['res']}")
            continue
        pa, pb = (ga["dumps"][1] if len(ga["dumps"]) > 1 else []), (gb["dumps"][1] if len(gb["dumps"]) > 1 else [])
        oa, ob = (ga["dumps"][0] if ga["dumps"] else []), (gb["dumps"][0] if gb["dumps"] else [])
        od = [i for i in range(min(len(oa), len(ob))) if oa[i] != ob[i]]
        flag = "  " if ga["res"] == gb["res"] else "!="
        print(f" {flag} npc {npc:08x} res {ga['res']}/{gb['res']}  pt R[{fmt(pa)}] P[{fmt(pb)}]  obj diff {od}")
        if od:
            print(f"      R obj {fmt(oa)}\n      P obj {fmt(ob)}")
    for npc in b["order"]:
        if npc not in a["gates"]:
            print(f"   npc {npc:08x}: port only, res {b['gates'][npc]['res']}")
