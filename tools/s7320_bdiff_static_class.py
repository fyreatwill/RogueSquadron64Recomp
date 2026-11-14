#!/usr/bin/env python3
"""s7320 spill-holder-pointer-diff: static close-out of the class-C field pointer differences (tools/s7320_bdiff_sites.txt, 155 sites).
The s7320 runtime run (ROGUESQ_S7318_BCMP over tools/apply_s7320_bdiff_probe.py hooks, dd8 21:9 L4) executed 98/155 sites with 0
spill-minus-heap cross subtractions. This tool classes the sites no run executed. Each site carries a manual verdict (read from the
original MIPS in N64Recomp/RecompiledFuncs) whose class has a mechanical signature re-checked against the generated code:
  SCALAR: the subtracted field is a count / size / health / timer / index / printf width, never a pointer (or the subtraction is a
          strength-reduced multiply x*(2^k-1) of an index: `sll a, x, k ; subu d, a, x ; sll d, d, j`).
  SAME:   pointer minus pointer into ONE object (zlib window fields 0x24-0x30 of one inflate state, zlib next_in before/after, one
          rs-heap freelist block): the difference is base-invariant, so a spill-placed object gives retail's value.
  H-cross (a pointer minus a pointer/bound from another allocation) would be the defect class; none is assigned.
Controls: every class signature must accept all its own sites AND reject at least one site of another class (else vacuous); the
classified set must equal exactly the never-executed set of the given tables (class C rows, idx >= 256).
Usage: s7320_bdiff_static_class.py <bcmp table>...   (exit 1 on any failed signature, coverage gap or vacuous signature)"""
import glob, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent
GEN = ROOT.parents[1] / "N64Recomp" / "RecompiledFuncs"
INS = re.compile(r"^\s*// (0x[0-9A-F]{8}): (.*)$")

def has(pat): return lambda w, f, s: any(re.search(pat, t) for t in w)
def fn(*names): return lambda w, f, s: f in names
def both(a, b): return lambda w, f, s: a(w, f, s) and b(w, f, s)
def mul_idiom(w, f, s):  # rt was shifted into rs (x<<k - x) and d is scaled again: index * constant, not a pointer
    rt = re.escape(s[9])
    return s[10].startswith("sll@") and any(re.search(r"sll \$\w+, %s, \d+$" % rt, t) for t in w)
def inflate_same(w, f, s):  # field and other operand both from window fields 0x24/0x28/0x2C/0x30 of one inflate state base
    bases = {m.group(2) for t in w for m in [re.search(r"lw \$\w+, (0x2[48C]|0x30)\(\$(\w+)\)", t)] if m}
    return f.startswith("inflate") and s[4] in ("0x24", "0x28", "0x2C", "0x30") and len(bases) == 1
CLASSES = {  # name: (kind, signature, sites)
    "heap-freelist":  ("SAME",   both(fn("buildHeapFreeList"), has(r"addiu \$t0, \$a0, 0x10")), [258]),
    "heap-size":      ("SCALAR", both(fn("allocRsHeapBlock"), lambda w, f, s: s[4] == "0x8"), [268]),
    "asset-pos":      ("SCALAR", both(fn("processAssetLoadStep"), has(r"lw \$\w+, 0x(60|68)\(\$s0\)")), [263, 264]),
    "mul-idiom":      ("SCALAR", mul_idiom, [270, 271, 280, 284, 286, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 319, 325]),
    "health-timer":   ("SCALAR", lambda w, f, s: f in ("getNpcCurrentHealth", "getNpcMissingHealth") or
                                 any(re.search(r"lhu \$\w+, 0x6\(", t) for t in w), [278, 279, 329, 330, 334, 335, 336]),
    "musyx-samples":  ("SCALAR", both(fn("musyxRenderVoiceSamples"), has(r"lw \$\w+, 0x(38|3C|40)\(\$s1\)")), [294, 295, 298]),
    "cp0-timer":      ("SCALAR", has(r"mfc0 \$\w+, (Count|Compare)"), [342, 343]),
    "inflate-window": ("SAME",   inflate_same, [347, 348, 349, 350, 351, 352, 370, 374, 376, 378, 379, 380]),
    "inflate-avail":  ("SCALAR", both(fn("inflate_blocks"), lambda w, f, s: s[4] == "0x4"), [353]),
    "inflate-input":  ("SAME",   both(fn("inflateSync"), has(r"sw \$a2, 0x0\(\$s0\)")), [344]),
    "huft-count":     ("SCALAR", fn("huft_build_recomp"), [391, 392, 393]),
    "printf-prec":    ("SCALAR", fn("_Genld"), [400, 401, 402, 403, 404, 405, 406]),
}

def main(tables):
    S = {int(l.split()[0]): l.split() for l in open(ROOT / "s7320_bdiff_sites.txt") if not l.startswith("#")}
    ex = set()
    for p in tables:
        for l in open(p):
            if l.strip() and not l.startswith("#") and int(l.split()[0]) >= 256: ex.add(int(l.split()[0]))
    un = sorted(set(S) - ex)
    funcs = []
    for path in sorted(glob.glob(str(GEN / "*.c"))):
        cur = None
        for l in open(path, errors="replace"):
            if l.startswith("RECOMP_FUNC"): cur = [l.split("(")[0].split()[-1], []]; funcs.append(cur)
            elif cur:
                m = INS.match(l)
                if m and (not cur[1] or cur[1][-1][0] != int(m.group(1), 16)): cur[1].append((int(m.group(1), 16), re.sub(r"\s+", " ", m.group(2).strip())))
    def window(i):
        s = S[i]; pc = int(s[1], 16)
        hits = [(name, [x[1] for x in ins[max(0, j - 16):j + 6]]) for name, ins in funcs
                for j, (p, t) in enumerate(ins) if p == pc and t.startswith(s[3] + " ")]
        hits.sort(key=lambda h: h[0] != s[2])  # prefer the copy named like the census site (duplicate-VA copies exist)
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
              " ".join("#%d:%s" % (i, S[i][2]) for i in sites if i not in own) or "all"))
    kinds = {}
    for i in owner: kinds[CLASSES[owner[i]][0]] = kinds.get(CLASSES[owner[i]][0], 0) + 1
    print("runtime-executed %d + static %d = %d/%d sites; static kinds %s; H-cross 0" % (len(ex & set(S)), len(owner), len(ex & set(S)) + len(owner), len(S), kinds))
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
