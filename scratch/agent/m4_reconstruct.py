#!/usr/bin/env python3
import re
import sys

HEX = r"[0-9A-Fa-f]+"
ROW = re.compile(r"\[m4-accum\] task=(\d+) phase=(\d+) stage=(10|11|12)(.*)")
LANE = re.compile(r"l(\d+):v4=(%s) v0=(%s) v6=(%s) v29=(%s) acch=(%s) accm=(%s) accl=(%s)" % (HEX, HEX, HEX, HEX, HEX, HEX, HEX))

def s16(v):
    return v - 0x10000 if v & 0x8000 else v

def u16(v):
    return v & 0xffff

def reconstruct(acch, accm, accl, v4, v0):
    acc = (acch << 32) | (accm << 16) | accl
    result = ((acc >> 16) + s16(v4) * s16(v0)) & 0xffffffff
    new_h = (result >> 16) & 0xffff
    new_m = result & 0xffff
    if s16(new_h) < 0:
        saturated = new_h != 0xffff or s16(new_m) >= 0
        out = 0x8000 if saturated else new_m
    else:
        saturated = new_h != 0 or s16(new_m) < 0
        out = 0x7fff if saturated else new_m
    return new_h, new_m, out, saturated

def synthetic():
    cases = [
        ("saturation", (0xffff, 0x0000, 0x0000, 0x0000, 0x0000), 0x0000, 0x8000),
        ("in-range", (0xffff, 0x8000, 0x0000, 0x0000, 0x0000), 0x8000, 0x8000),
    ]
    for name, args, expected_pre, expected_post in cases:
        h, m, out, saturated = reconstruct(*args)
        vge = out
        ok = (m == expected_pre and out == expected_post and vge == expected_post)
        print("CONTROL %s pre=%04X post=%04X vge=%04X saturated=%d %s" %
              (name, m, out, vge, saturated, "PASS" if ok else "FAIL"))
        if not ok:
            raise SystemExit("synthetic control failed")

def main(path):
    rows = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = ROW.search(line)
            if not m:
                continue
            key = (int(m.group(1)), int(m.group(2)))
            lanes = {}
            for lm in LANE.finditer(m.group(4)):
                vals = [int(x, 16) for x in lm.groups()]
                lanes[vals[0]] = dict(zip(("v4", "v0", "v6", "v29", "acch", "accm", "accl"), vals[1:]))
            rows.setdefault(key, {}).setdefault(int(m.group(3)), []).append(lanes)
    triplets = 0
    endpoints = {"pre": 0, "post": 0, "vge": 0}
    saturated = 0
    total = 0
    for key, stages in rows.items():
        n = min(len(stages.get(10, [])), len(stages.get(11, [])), len(stages.get(12, [])))
        for i in range(n):
            a, b, c = stages[10][i], stages[11][i], stages[12][i]
            if set(a) != set(b) or set(a) != set(c):
                continue
            triplets += 1
            for lane in sorted(a):
                x = a[lane]
                h, m, out, sat = reconstruct(x["acch"], x["accm"], x["accl"], x["v4"], x["v0"])
                observed_post = b[lane]["v6"]
                observed_vge = c[lane]["v6"]
                total += 1
                saturated += int(sat)
                endpoints["pre"] += int(m == 0x8000)
                endpoints["post"] += int(out == 0x8000)
                endpoints["vge"] += int(observed_vge == 0x8000)
                if out != observed_post:
                    print("MISMATCH task=%d phase=%d row=%d lane=%d predicted=%04X observed=%04X" %
                          (key[0], key[1], i, lane, out, observed_post))
    synthetic()
    print("REAL triplets=%d lanes=%d saturated=%d pre_8000=%d post_8000=%d observed_vge_8000=%d" %
          (triplets, total, saturated, endpoints["pre"], endpoints["post"], endpoints["vge"]))
    if not triplets or not total:
        raise SystemExit("no complete triplets extracted")

if __name__ == "__main__":
    main(sys.argv[1])
