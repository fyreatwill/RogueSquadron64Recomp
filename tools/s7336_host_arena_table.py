#!/usr/bin/env python3
"""s7336: host-arena layout census. Every host allocator that hands guest addresses to the game, modelled from its source
(env -> [base, end)), swept over the accepted env range, and checked for:
  OVERLAP   two host arenas share bytes, or a host arena starts below the guest top 0x80000000|osMemSize
  GUARD     an arena ends above rs64_ram_top (RS64_RAM_TOP pointer guards / RT64 reads reject it; rs_free's s6086 early return
            `ptr >= RS64_RAM_TOP` also swallows frees of it, so a spill block there leaks)
  RSP24     an arena the RCP reads directly (DL chunks, bigarena terrain pool) ends above 0x81000000 (24-bit segment span)
Sources mirrored (keep in sync):
  guest top     lib/N64ModernRuntime/librecomp/src/recomp.cpp s6114/s6130 (OSMEM_MB 4..16 else 8) + s6567 RAMTOP_MB (mb<t<=24)
  dd>1 bundle   src/main/main.cpp ~12503 (setenv overwrite=0: OSMEM 12; if >8 SPILL_HI 1 + RAMTOP 24; RAMTOP 16; MALLOC_SPILL,
                DLPOOLX, DLPOOLX_MB 4)
  DLPOOLX       upstream_compat.cpp rs64_s6099_alloc / rs64_s7335_dlpool_cap / rs64_s7336 clamp
  spill         upstream_compat.cpp rs64_s6587_spill_base / rs64_s7326_spill_cap / rs64_s7336 ram_top widen
  bigarena      upstream_compat.cpp rs64_s6086_divert: [ram_top, ram_top + poolx*184) (opt-in ROGUESQ_BIGARENA)
Usage: s7336_host_arena_table.py [--old] [--control]   --old models the pre-s7336 code (expect findings); exit 1 on any finding.
--control: the pre-s7336 model must flag the two known combos (positive control); exit 1 if it does not."""
import itertools, sys

RSP_TOP = 0x81000000


def layout(env, old=False):
    e = dict(env)
    dd = float(e.get("ROGUESQ_DRAW_DISTANCE", "1"))
    if dd > 1.0:  # main.cpp dd bundle (overwrite=0)
        e.setdefault("ROGUESQ_OSMEM_MB", "12")
        if int(e["ROGUESQ_OSMEM_MB"]) > 8:
            e.setdefault("ROGUESQ_SPILL_HI", "1"); e.setdefault("ROGUESQ_RAMTOP_MB", "24")
        e.setdefault("ROGUESQ_RAMTOP_MB", "16"); e.setdefault("ROGUESQ_MALLOC_SPILL", "1")
        e.setdefault("ROGUESQ_DLPOOLX", "1"); e.setdefault("ROGUESQ_DLPOOLX_MB", "4")
    mb = int(e.get("ROGUESQ_OSMEM_MB", "8"))
    if mb < 4 or mb > 16: mb = 8
    top = 0x80000000 + (mb << 20); ram_top = top
    tm = int(e.get("ROGUESQ_RAMTOP_MB", "0"))
    if mb < tm <= 24: ram_top = 0x80000000 + (tm << 20)
    ar = {"guest": (0x80000000, top)}
    sp = None
    if e.get("ROGUESQ_MALLOC_SPILL", "0") not in ("", "0"):
        b = 0x81000000 if e.get("ROGUESQ_SPILL_HI", "0") not in ("", "0") else 0x80800000
        if not old and b == 0x80800000 and top > b: b = 0x81000000  # s7336: legacy base under the guest top moves up
        smb = 8 if b == 0x81000000 else 4
        v = int(e.get("ROGUESQ_SPILL_MB", "0"))
        if 1 <= v <= 16: smb = v
        cap = smb << 20
        if not old and b == 0x81000000 and ram_top <= b:  # s7336: widen ram_top to cover the arena (librecomp max 24 MB)
            ram_top = min(b + cap, 0x81800000)
            if b + cap > ram_top: cap = ram_top - b
        if b == 0x81000000 and ram_top > b and b + cap > ram_top: cap = ram_top - b
        if b != 0x81000000 and cap > 0x400000: cap = 0x400000
        if not old and b != 0x81000000: ram_top = max(ram_top, b + cap)  # s7336: legacy spill without RAMTOP_MB 16
        sp = (b, b + cap); ar["spill"] = sp
    if e.get("ROGUESQ_DLPOOLX", "0") not in ("", "0"):
        m = int(e.get("ROGUESQ_DLPOOLX_MB", "1"))
        m = max(1, min(8, m)); cap = m << 20
        if e.get("ROGUESQ_S7335_CLAMP", "1") != "0":
            lim = RSP_TOP - top if top < RSP_TOP else 0
            if not old and sp and sp[0] < RSP_TOP:  # s7336: never below a legacy spill arena either
                lim = min(lim, RSP_TOP - max(sp[1], top))
            if cap > lim: cap = lim & ~0xFFFF
        if not old: ram_top = max(ram_top, RSP_TOP)  # s7336: widen to the DL arena end
        ar["dlpool"] = (RSP_TOP - cap, RSP_TOP)
    if e.get("ROGUESQ_BIGARENA", "0") not in ("", "0"):
        n = int(e.get("ROGUESQ_DD_POOLX", "4096")); ar["bigarena"] = (ram_top, ram_top + ((n * 184 + 15) & ~15))
    return ar, ram_top, top


def check(ar, ram_top, top):
    f = []
    host = [(k, v) for k, v in ar.items() if k != "guest" and v[1] > v[0]]
    for (a, x), (b, y) in itertools.combinations(host, 2):
        if x[0] < y[1] and y[0] < x[1]: f.append("OVERLAP %s/%s" % (a, b))
    for k, v in host:
        if v[0] < top: f.append("OVERLAP %s/guest" % k)
        if k != "bigarena" and v[1] > ram_top: f.append("GUARD %s end %08X > ram_top %08X" % (k, v[1], ram_top))
        if k in ("dlpool",) and v[1] > RSP_TOP: f.append("RSP24 %s" % k)
    return f


AXES = {
    "ROGUESQ_DRAW_DISTANCE": ["1", "4"],
    "ROGUESQ_OSMEM_MB": [None, "4", "8", "12", "16", "20"],
    "ROGUESQ_RAMTOP_MB": [None, "16", "20", "24"],
    "ROGUESQ_SPILL_HI": [None, "0", "1"],
    "ROGUESQ_SPILL_MB": [None, "4", "8", "16"],
    "ROGUESQ_DLPOOLX_MB": [None, "1", "4", "8"],
    "ROGUESQ_MALLOC_SPILL": [None, "1"],
    "ROGUESQ_DLPOOLX": [None, "1"],
}
DEFAULTS = [{"ROGUESQ_DRAW_DISTANCE": d} for d in ("1", "2", "4", "8")] + [{"ROGUESQ_DRAW_DISTANCE": "4", "ROGUESQ_OSMEM_MB": "8"}]
CONTROLS = [  # known pre-s7336 findings
    ({"ROGUESQ_DRAW_DISTANCE": "4", "ROGUESQ_OSMEM_MB": "8", "ROGUESQ_DLPOOLX_MB": "8"}, "OVERLAP spill/dlpool"),
    ({"ROGUESQ_DRAW_DISTANCE": "4", "ROGUESQ_OSMEM_MB": "8", "ROGUESQ_SPILL_HI": "1"}, "GUARD spill"),
    ({"ROGUESQ_OSMEM_MB": "12", "ROGUESQ_MALLOC_SPILL": "1"}, "OVERLAP spill/guest"),
    ({"ROGUESQ_MALLOC_SPILL": "1", "ROGUESQ_DLPOOLX": "1"}, "GUARD"),
]


def sweep(old):
    keys = list(AXES); bad = {}; n = 0
    for vals in itertools.product(*(AXES[k] for k in keys)):
        env = {k: v for k, v in zip(keys, vals) if v is not None}
        n += 1
        for msg in check(*layout(env, old)):
            kind = msg.split(" ")[0] + " " + msg.split(" ")[1]
            bad.setdefault(kind, []).append(env)
    return n, bad


def fmt(ar):
    return " ".join("%s=%08X..%08X" % (k, v[0], v[1]) for k, v in ar.items())


if __name__ == "__main__":
    old = "--old" in sys.argv
    if "--control" in sys.argv:
        ok = True
        for env, want in CONTROLS:
            got = check(*layout(env, True)); hit = any(g.startswith(want) for g in got)
            fixed = check(*layout(env, False))
            print("control %-60s old=%s new=%s %s" % (env, got, fixed, "PASS" if hit and not fixed else "FAIL"))
            ok &= hit and not fixed
        sys.exit(0 if ok else 1)
    for env in DEFAULTS:
        ar, rt, top = layout(env, old); print("default %-50s %s ram_top=%08X %s" % (env, fmt(ar), rt, check(ar, rt, top) or "clean"))
    n, bad = sweep(old)
    print("sweep %d env combos (%s model): %d finding classes" % (n, "pre-s7336" if old else "current", len(bad)))
    for k, envs in sorted(bad.items()):
        print("  %-40s %5d combos, e.g. %s" % (k, len(envs), envs[0]))
    sys.exit(1 if bad else 0)
