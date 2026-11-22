#!/usr/bin/env python3
"""s7785: which retained store-watch logs carry rows attributed to an s5660 unaligned-store pc (swl/swr/sdl/sdr)?
Before s7784 those hooks reported value+offset instead of base+offset (tools/s7784_ustore_base_census.py), so any such row
before the fix is a VALUE that fell in the watch range (H-false-hit) and any null over a range is blind to real unaligned
writers (H-missed). Rows parsed: [swatch] pc=, [swatch-pt] pc=, [s7781] pc= / cst pc=, [vstore] new pc=, [vstore-rail] pc=.
Usage: s7785_ustore_fallout.py [--controls] LOG...   (pc set from N64Recomp/RecompiledFuncs/funcs_*.c)
Prints per log: rows=<all pc rows> u_rows=<rows with an unaligned pc> u_pcs=<distinct> top pcs, plus per tag counts.
--controls (iron rule 1): a planted unaligned-pc row must count u_rows=1 and an aligned-pc row 0, else exit 3."""
import pathlib, re, sys, collections

ROW = re.compile(r"\[(swatch|swatch-pt|s7781|vstore|vstore-rail)\][^\n]*?\bpc=([0-9A-Fa-f]{8})")
FUNCS = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")


def pcset():
    s = set()
    for p in FUNCS.glob("funcs_*.c"):
        s.update(int(m, 16) for m in re.findall(r"rs64_s5660_ustore\(0x([0-9A-Fa-f]+)u", p.read_text(errors="replace")))
    return s


def scan(lines, U):
    rows = 0; tag = collections.Counter(); upc = collections.Counter(); utag = collections.Counter()
    for ln in lines:
        m = ROW.search(ln)
        if not m:
            continue
        rows += 1; tag[m.group(1)] += 1
        pc = int(m.group(2), 16)
        if pc in U:
            upc[pc] += 1; utag[m.group(1)] += 1
    return rows, tag, upc, utag


def main():
    U = pcset()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    print("unaligned_pcs=%d" % len(U))
    if "--controls" in sys.argv:
        u = min(U)
        r = scan(["[swatch] swap=3 pc=%08X n=1 bytes=4 lo=1 hi=5" % u, "[swatch] swap=3 pc=DEADBEE0 n=1 bytes=4 lo=1 hi=5"], U)
        ok = r[0] == 2 and sum(r[2].values()) == 1
        print("controls: rows=%d u_rows=%d %s" % (r[0], sum(r[2].values()), "PASS" if ok else "FAIL"))
        if not ok:
            return 3
    for a in args:
        with open(a, errors="replace") as f:
            rows, tag, upc, utag = scan(f, U)
        print("%s rows=%d u_rows=%d u_pcs=%d tags=%s utags=%s top=%s" % (a, rows, sum(upc.values()), len(upc), dict(tag), dict(utag),
              ",".join("%08X:%d" % kv for kv in upc.most_common(6))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
