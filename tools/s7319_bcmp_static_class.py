#!/usr/bin/env python3
"""s7319 spill-holder-field-compare: static close-out of the class-B field-order compares (s7317 census, 182 sites).
s7318 executed 119/182 sites at runtime (4 runs: dd8 21:9 L4 x2, L1, L12) with 0 spill-vs-heap cross compares. This tool classes
the 63 sites no run executed. Each site carries a manual verdict (read from the original MIPS in N64Recomp/RecompiledFuncs) and the
verdict's class has a mechanical signature that is re-checked here against the generated code:
  SCALAR classes: the compared field is a size / count / index / id / time / printf precision, never a pointer.
  SAME classes:   pointer vs pointer into ONE object (zlib window, TLUT pool, one rs-heap freelist) -> ordering is base-invariant.
  H-cross (pointer vs a pointer/bound from another allocation) would be the defect class; none is assigned.
Controls: every class signature must accept all its own sites AND reject at least one site of another class (else it is vacuous);
the 63 sites must equal exactly the never-executed set of the given s7318 tables, and 119 + 63 must cover all 182 sites.
Usage: s7319_bcmp_static_class.py <bcmp table>...   (exit 1 on any failed signature, coverage gap or vacuous signature)"""
import glob, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent
GEN = ROOT.parents[1] / "N64Recomp" / "RecompiledFuncs"
INS = re.compile(r"^\s*// (0x[0-9A-F]{8}): (.*)$")

def has(pat): return lambda w, f, s: any(re.search(pat, t) for t in w)
def fn(*names): return lambda w, f, s: f in names
def both(a, b): return lambda w, f, s: a(w, f, s) and b(w, f, s)
def ctr_table(w, f, s):  # signed compare of an int counter table entry: sll idx,2 ; addu ; lw x,0x0(..)
    return s[3] == "slt" and any(re.search(r"sll \$(\w+), \$\1, 2$", t) for t in w) and any(re.search(r"lw \$\w+, 0x0\(\$", t) for t in w)
def inflate_same(w, f, s):  # both operands from window fields 0x24/0x28/0x2C/0x30 of one inflate_blocks_state base
    offs = {m.group(2): m.group(3) for t in w for m in [re.search(r"lw \$(\w+), (0x2[48C]|0x30)\(\$(\w+)\)", t)] if m}
    return f.startswith("inflate") and len(set(offs.values())) == 1 and len(offs) >= 1
def counted(w, f, s):  # an operand is a loop counter / index: addiu r,r,1 or sll ..,r,2
    regs = {s[6], s[7]}
    return any(re.search(r"addiu (\$\w+), \1, 0x1$", t) and re.search(r"addiu (\$\w+)", t).group(1) in regs for t in w) or \
           any(re.search(r"sll \$\w+, (\$\w+), 2$", t) and re.search(r"sll \$\w+, (\$\w+), 2$", t).group(1) in regs for t in w)
CLASSES = {  # name: (kind, signature, sites)
    "heap-size":      ("SCALAR", both(fn("findLargestFreeHeapChunk", "allocRsHeapBlock"), lambda w, f, s: s[4] in ("0x4", "0x8")), [0, 8]),
    "heap-freelist":  ("SAME",   both(fn("buildHeapFreeList"), has(r"addiu \$t0, \$a0, 0x10")), [2]),
    "asset-length":   ("SCALAR", both(fn("processAssetLoadStep"), has(r"lw \$(a2|v0), 0x(20|60)\(\$(v1|s0)\)")), [6, 7]),
    "frame-counter":  ("SCALAR", has(r"lw \$v1, -0x7764\(\$v1\)"), [19, 20]),
    "halfword":       ("SCALAR", has(r"lhu \$v0, "), [29]),
    "ctr-table":      ("SCALAR", ctr_table, [32, 33, 42, 43, 77, 98, 99, 100, 102, 103, 105, 108, 109, 118, 119, 120, 123]),
    "loop-count":     ("SCALAR", counted, [34, 40, 41]),
    "blob-offset":    ("SCALAR", both(fn("load_naboo_starfighter"), has(r"andi \$v0, \$(a1|v1), 0x3")), [36, 37, 38, 39]),
    "voice-handle":   ("SCALAR", has(r"-0x5100\("), [50, 51, 53, 57, 58, 59]),
    "voice-pitch":    ("SCALAR", has(r"sll \$a0, \$a3, 8|srl \$v0, \$v1, 8"), [52]),
    "sched-time":     ("SCALAR", both(fn("scheduleSceneFormatMessageTimed"), lambda w, f, s: s[3] == "slt"), [87]),
    "float-trunc":    ("SCALAR", has(r"mfc1 \$v0, \$f4"), [116]),
    "tlut-pool":      ("SAME",   both(fn("freeTextureTlutBlock"), has(r"-0x5830\(")), [127]),
    "inflate-window": ("SAME",   inflate_same, [131, 132, 133, 156]),
    "inflate-avail":  ("SCALAR", both(fn("inflate_blocks"), lambda w, f, s: s[4] == "0x4"), [134]),
    "huft-count":     ("SCALAR", fn("huft_build_recomp"), [158, 159]),
    "pfs-page":       ("SCALAR", both(lambda w, f, s: f.startswith("__osPfs"), lambda w, f, s: s[3] == "slt"), [163, 164, 165, 166, 167, 168]),
    "printf-prec":    ("SCALAR", both(fn("_Genld"), lambda w, f, s: s[4] in ("0x24", "0x28")), [170, 171, 172, 173, 174, 175, 176, 177]),
}
WIN = {127: 40}

def main(tables):
    S = {int(l.split()[0]): l.split() for l in open(ROOT / "s7318_bcmp_sites.txt") if not l.startswith("#")}
    ex = set()
    for p in tables:
        for l in open(p):
            if l.strip() and not l.startswith("#"): ex.add(int(l.split()[0]))
    un = sorted(set(S) - ex)
    # function-scoped instruction streams (two functions may share a VA: overlays)
    funcs = []
    for path in sorted(glob.glob(str(GEN / "*.c"))):
        cur = None
        for l in open(path, errors="replace"):
            if l.startswith("RECOMP_FUNC"): cur = [l.split("(")[0].split()[-1], []]; funcs.append(cur)
            elif cur:
                m = INS.match(l)
                if m and (not cur[1] or cur[1][-1][0] != int(m.group(1), 16)): cur[1].append((int(m.group(1), 16), re.sub(r"\s+", " ", m.group(2).strip())))
    def window(i):
        s = S[i]; pc = int(s[1], 16); k = WIN.get(i, 16)
        hits = [(name, [x[1] for x in ins[max(0, j - k):j + 6]]) for name, ins in funcs
                for j, (p, t) in enumerate(ins) if p == pc and t.startswith(s[3] + " ")]
        hits.sort(key=lambda h: h[0] != s[2])  # prefer the copy named like the census site (duplicate VA copies exist)
        return hits[0] if hits else (None, [])
    owner = {i: c for c, (_, _, sites) in CLASSES.items() for i in sites}
    bad = 0
    miss = sorted(set(un) - set(owner)); extra = sorted(set(owner) - set(un))
    if miss or extra: print("COVERAGE FAIL unclassified=%s classified-but-executed=%s" % (miss, extra)); bad += 1
    W = {i: window(i) for i in owner}
    for c, (kind, sig, sites) in CLASSES.items():
        own = [i for i in sites if W[i][0] and sig(W[i][1], W[i][0], S[i])]
        rej = [i for i in owner if owner[i] != c and W[i][0] and not sig(W[i][1], W[i][0], S[i])]
        ok = len(own) == len(sites) and rej
        bad += not ok
        print("%-5s %-6s %-15s %2d/%-2d own, rejects %2d foreign  %s" % ("ok" if ok else "FAIL", kind, c, len(own), len(sites), len(rej),
              " ".join("#%d:%s" % (i, S[i][2]) for i in sites)))
    kinds = {}
    for i in owner: kinds[CLASSES[owner[i]][0]] = kinds.get(CLASSES[owner[i]][0], 0) + 1
    print("runtime-executed %d + static %d = %d/%d sites; static kinds %s; H-cross 0" % (len(ex & set(S)), len(owner), len(ex & set(S)) + len(owner), len(S), kinds))
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
