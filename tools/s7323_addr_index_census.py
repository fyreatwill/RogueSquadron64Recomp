#!/usr/bin/env python3
"""s7323 spill-addr-index: class F of the spill-pointer audit (classes A-E: tools/s7317_field_compare_census.py).

An ADDRESS-DERIVED TABLE INDEX: `srl/sra d, s, k` with 8 <= k <= 22 of a non-constant s (optionally after a phys mask
`and s, x, 0x1FFFFFFF`-class or `subu/addu` with 0x80000000-class constant: those keep the shape), then d (scaled by sll/addu with
itself) reaches a MEMORY BASE use, either directly or after `addu t, d, base` with a constant register (lui/ori: a global table) or
any other register (a pointer table base). A spill pointer 0x81xxxxxx then indexes 16 MB/2^k entries in, past the end of a table
sized for 8 MB of RDRAM (2^23 >> k entries), and the access lands after the table. Bounded when an andi / and-with-constant /
srl-by->=23-total / sltiu|slti|sltu|slt read of the index occurs before the memory use (hash, mask or range check).

Source provenance of s (what got shifted): narrow (andi, lhu/lh/lbu/lb, a previous srl, sll by >=8 then srl, mfhi/mflo product,
mfc1 float: none can hold a 32-bit KSEG pointer with bit 24 meaningful, or are scalars) vs word (lw), arg (an $a0-$a3 / callee-saved
read before any def in the function), other (computed: addu/subu/or of non-constants).

Verdicts (exit 1 if any site is UNCLASSIFIED):
  bounded       -- masked or range-checked before the memory use
  scalar        -- narrow / fpu / product source
  small-table   -- k <= 22 but the shifted value is masked to < 2^23 before the shift (covered by bounded/narrow)
  probe         -- unbounded, word/arg/other source: listed in tools/s7323_aindex_sites.txt for the s7318 runtime classifier
                   (idx 768+, cross = the source is a spill pointer). Not a defect by itself.
--selftest runs planted positive and negative snippets. Usage: s7323_addr_index_census.py [--selftest] [--sites out.txt]"""
import pathlib, re, sys
from collections import Counter

GEN = pathlib.Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs"
INS = re.compile(r"^\s*// (0x[0-9A-F]{8}): (\w+)\s*(.*)$")
FN = re.compile(r"^RECOMP_FUNC void (\w+)\(")
MEM = re.compile(r"^(-?0x[0-9A-Fa-f]+|-?\d+)\((\$\w+)\)$")
SAVED = ("$s0", "$s1", "$s2", "$s3", "$s4", "$s5", "$s6", "$s7", "$fp", "$sp", "$gp")
ARGS = ("$a0", "$a1", "$a2", "$a3") + SAVED
LOADS = ("lw", "lh", "lhu", "lb", "lbu", "sw", "sh", "sb", "lwc1", "swc1", "ldc1", "sdc1", "lwl", "lwr", "swl", "swr", "ld", "sd")
KMAX = 31 if "--top" in sys.argv else 22
NARROWOPS = ("andi", "lhu", "lh", "lbu", "lb", "mfhi", "mflo", "mfc1", "slt", "sltu", "slti", "sltiu")

SELFTEST = """RECOMP_FUNC void s7323FakeUnbounded(uint8_t* rdram, recomp_context* ctx) {
    // 0x80006000: lw          $a0, 0x10($s1)
    // 0x80006004: srl         $v0, $a0, 12
    // 0x80006008: sll         $v0, $v0, 2
    // 0x8000600C: lui         $at, 0x8013
    // 0x80006010: addu        $at, $at, $v0
    // 0x80006014: lw          $t0, 0x40($at)
RECOMP_FUNC void s7323FakeBounded(uint8_t* rdram, recomp_context* ctx) {
    // 0x80007000: lw          $a0, 0x10($s1)
    // 0x80007004: srl         $v0, $a0, 12
    // 0x80007008: andi        $v0, $v0, 0x3FF
    // 0x8000700C: sll         $v0, $v0, 2
    // 0x80007010: lui         $at, 0x8013
    // 0x80007014: addu        $at, $at, $v0
    // 0x80007018: lw          $t0, 0x40($at)
RECOMP_FUNC void s7323FakeScalar(uint8_t* rdram, recomp_context* ctx) {
    // 0x80008000: lhu         $a0, 0x10($s1)
    // 0x80008004: srl         $v0, $a0, 8
    // 0x80008008: sll         $v0, $v0, 2
    // 0x8000800C: addu        $t1, $s2, $v0
    // 0x80008010: lw          $t0, 0x0($t1)
    // 0x80008014: sra         $t2, $a1, 16
    // 0x80008018: sll         $t2, $t2, 2
    // 0x8000801C: addu        $t3, $s3, $t2
    // 0x80008020: sw          $zero, 0x0($t3)
    // 0x80008024: srl         $t4, $a2, 16
    // 0x80008028: addu        $t5, $t4, $a3
RECOMP_FUNC void s7323FakeSeg(uint8_t* rdram, recomp_context* ctx) {
    // 0x80009000: lui         $at, 0x3F00
    // 0x80009004: and         $t0, $a0, $at
    // 0x80009008: srl         $t1, $t0, 22
    // 0x8000900C: lui         $t2, 0x8013
    // 0x80009010: addu        $t2, $t2, $t1
    // 0x80009014: lw          $t3, 0x0($t2)
    // 0x80009018: lui         $at, 0x00FC
    // 0x8000901C: and         $t4, $a1, $at
    // 0x80009020: nop
    // 0x80009024: srl         $t5, $t4, 18
    // 0x80009028: lui         $t6, 0x8013
    // 0x8000902C: addu        $t6, $t6, $t5
    // 0x80009030: lw          $t7, 0x0($t6)
"""

def imm(s): return int(s, 0)

def scan(srcs):
    """Returns the list of sites: [fn, shpc, k, prov, srcdesc, usepc, useop, base, bounded_by, kind]."""
    out = []
    for _, text in srcs:
        fn, reg, seen, defd = None, {}, set(), set()
        for line in text.splitlines():
            m = FN.match(line)
            if m: fn, reg, seen, defd = m.group(1), {}, set(), set(); continue
            m = INS.match(line)
            if not m or fn is None: continue
            pc, op, args = m.groups()
            if pc in seen: continue
            seen.add(pc)
            a = [x.strip() for x in args.split(",")] if args else []
            d = a[0] if a else None
            new = None
            def prov(r):
                t = reg.get(r)
                if t is None: return ("arg", r) if r in ARGS and r not in defd else ("other", r)
                if t[0] == "c": return ("const", "0x%X" % t[1])
                if t[0] == "w": return ("word", t[1])
                if t[0] == "n": return ("narrow", t[1])
                if t[0] == "p": return t[1]          # phys-masked / KSEG-offset: keeps the source provenance
                if t[0] == "x": return ("narrow", "idx@%s" % t[1][1])
                return ("other", "%s:%s" % (r, t[0]))
            # ---- uses of an index register (before redefinition)
            if op in LOADS and len(a) == 2:
                mm = MEM.match(a[1])
                if mm and reg.get(mm.group(2), ("",))[0] == "x":
                    x = reg[mm.group(2)][1]
                    out.append([fn, x[1], x[2], x[3][0], x[3][1], pc, op, x[5] or "reg", x[4], x[7] if len(x) > 7 else None])
                    x[6] = True
            if op in ("andi", "slt", "sltu", "slti", "sltiu") or (op == "and" and len(a) == 3):
                for r in a[1:]:
                    t = reg.get(r)
                    if t and t[0] == "x" and not t[1][4]:
                        if op == "and" and not any(reg.get(o, ("",))[0] == "c" for o in a[1:]): continue
                        t[1][4] = "%s@%s" % (op, pc)
                        if op == "andi": t[1].append(imm(a[2]))
                        elif op == "and": t[1].append(next(reg[o][1] for o in a[1:] if reg.get(o, ("",))[0] == "c"))
            # ---- definitions
            if op in ("andi", "and") and len(a) == 3 and any(reg.get(r, ("",))[0] == "x" for r in a[1:]) and \
               (op == "andi" or any(reg.get(r, ("",))[0] == "c" for r in a[1:])):
                new = next(reg[r] for r in a[1:] if reg.get(r, ("",))[0] == "x")  # masked index: still an index, bounded
            elif op == "lui" and len(a) == 2: new = ("c", (imm(a[1]) << 16) & 0xFFFFFFFF)
            elif op in ("addiu", "ori") and len(a) == 3 and (a[1] == "$zero" or reg.get(a[1], ("",))[0] == "c"):
                b = 0 if a[1] == "$zero" else reg[a[1]][1]; v = imm(a[2])
                new = ("c", (b | (v & 0xFFFF)) if op == "ori" else (b + v) & 0xFFFFFFFF)
            elif op in ("srl", "sra") and len(a) == 3 and reg.get(a[1], ("",))[0] != "c":
                k = imm(a[2]); t = reg.get(a[1])
                if 8 <= k <= KMAX and not (t and t[0] == "x"):
                    # x record: [fn, shpc, k, prov, bounded_by, base, used]
                    p = prov(a[1])
                    if p[0] == "const": p = ("narrow", "const")
                    new = ("x", [fn, pc, k, p, None, None, False])
                    if t and t[0] == "s":  # sll a,b ; srl d,a,k : the field extract (b << j) >> k keeps 32-j bits
                        new[1][3] = ("narrow", "sll%d+%s%d" % (t[1], op, k)) if t[1] >= 9 else prov(a[1])
                elif t and t[0] == "x":
                    new = t  # further shift of an index: still the index (deeper)
                else:
                    new = ("n", "%s%d@%s" % (op, k, pc))
            elif op == "sll" and len(a) == 3 and reg.get(a[1], ("",))[0] == "x" and imm(a[2]) < 8:
                new = reg[a[1]]  # scale
            elif op == "sll" and len(a) == 3 and imm(a[2]) >= 8 and reg.get(a[1], ("",))[0] != "c":
                new = ("s", imm(a[2]))
            elif op in ("addu", "subu", "or") and len(a) == 3 and "$zero" not in (a[1], a[2]):
                tx, ty = reg.get(a[1]), reg.get(a[2])
                xs = [t for t in (tx, ty) if t and t[0] == "x"]
                if xs and op == "addu":
                    x = xs[0][1]; other = ty if tx is xs[0] else tx
                    if a[1] == a[2]: new = xs[0]
                    elif other and other[0] == "x": new = xs[0]
                    else:
                        if x[5] is None:
                            x[5] = ("0x%08X" % other[1]) if other and other[0] == "c" else ("reg:" + (a[2] if tx is xs[0] else a[1]))
                        new = xs[0]
                elif op in ("addu", "subu") and any(t and t[0] == "c" and (t[1] >> 24) in (0x80, 0xA0, 0x7F, 0x60) and t[1] & 0xFFFFFF == 0 for t in (tx, ty)):
                    r = a[2] if (tx and tx[0] == "c") else a[1]
                    new = ("p", prov(r))  # KSEG offset removal keeps the provenance
            elif op == "and" and len(a) == 3:
                for x, y in ((a[1], a[2]), (a[2], a[1])):
                    ty = reg.get(y)
                    if ty and ty[0] == "c" and reg.get(x, ("",))[0] != "c":
                        new = ("p", prov(x)) if ty[1] & 0x01FF0000 == 0x01FF0000 else ("n", "and0x%X@%s" % (ty[1], pc))
                        break
            elif op == "lw" and len(a) == 2: new = ("w", "lw %s@%s" % (a[1], pc))
            elif op in ("addu", "or") and len(a) == 3 and a[2] == "$zero" and a[1] in reg: new = reg[a[1]]
            if new is None and op in NARROWOPS and len(a) >= 2: new = ("n", "%s@%s" % (op, pc))
            if d and d.startswith("$") and not op.startswith(("s", "b", "j")) or op in ("slt", "sltu", "slti", "sltiu", "sll", "srl", "sra", "sllv", "srlv", "srav", "sub", "subu"):
                reg.pop(d, None); defd.add(d)
            if new is not None and d: reg[d] = new
            if op in ("jal", "jalr"):
                reg = {k: v for k, v in reg.items() if k in SAVED}
                defd |= {"$a0", "$a1", "$a2", "$a3", "$v0", "$v1"}
    return out

KNOWN_F = {  # s7323: every probe / OVERFLOW / ALIAS / bounded-check site read by hand (source is not a pointer)
    "0x8000DF60": "appendRdpStateDl material flags word: (a1 & 0x01C00000) >> 20 is a 3-bit mode field (sibling field 0x0E000000 >> 23 at 0x8000DF90); 8-entry table 0x8003775C",
    "0x80015070": "processSceneNode float->int (trunc.w.s/mfc1, bltzl rounding) >> 9 then slti 0x40 range check: scalar",
    "0x8001506C": "processSceneNode float->int (trunc.w.s/mfc1, bltzl rounding) >> 9 then slti 0x40 range check: scalar",
    "0x80024A48": "data_gap_80024A0C instruction-word decoder: sra 23 & 0x1FE of the fetched opcode word -> jump table: scalar",
    "0x80025B68": "data_gap_80024A0C COP2 (mfc2) result of (x & 0xFF00): scalar",
    "0x8005B048": "loadSkyHorizonHob HOB record header: (w & 0x3F000000) >> 22 is the record length added to the cursor (use beyond the j is a linear-scan artefact)",
    "0x8006228C": "measureTextSlotStringLayout glyph code >> 16 with sltiu range check: scalar",
    "0x8008AC40": "evaluateSoundMacroCurveTable 16.16 curve position, sltiu range check: scalar",
    "0x8008ADD4": "soundMacroSetVoiceVolume 16.16 volume, sltiu range check: scalar",
    "0x80093590": "decodeAdpcmSampleBlock ADPCM header byte (w >> 24) & 0xF predictor index: sample data",
    "0x80093A8C": "decodeAdpcmSampleBlock ADPCM header byte (w >> 24) & 0xF predictor index: sample data",
    "0x80094144": "computeVoiceVolumePanCoefficients 23-bit pan/volume fraction (sll10/srl10 low part -> lerp): v >> 22 table 0x800A4DE8",
    "0x800941B4": "computeVoiceVolumePanCoefficients 0x7FFFFF - pan: same 23-bit fraction",
    "0x80094220": "computeVoiceVolumePanCoefficients 0x7FFFFF - pan: same 23-bit fraction",
    "0x80094264": "computeVoiceVolumePanCoefficients 23-bit pan fraction argument a3",
    "0x800C9118": "decodeJpegScanToImage 16.16 fixed-point sample coordinate >> 16 into the scan buffer",
    "0x800C9258": "decodeJpegScanToImage 16.16 fixed-point sample coordinate", "0x800C944C": "decodeJpegScanToImage 16.16 fixed-point sample coordinate",
    "0x800C951C": "decodeJpegScanToImage 16.16 fixed-point sample coordinate", "0x800C974C": "decodeJpegScanToImage 16.16 fixed-point sample coordinate",
    "0x800C99B0": "decodeJpegScanToImage 16.16 fixed-point sample coordinate",
}
HEAPS = [0x80000000 | (b << 16) | lo for b in range(0x80) for lo in (0, 0xFFFC)]
SPILLS = [0x81000000 | (b << 16) | lo for b in range(0x40) for lo in (0, 0xFFFC)]
def evalidx(s, p):
    """Index the site computes from pointer p: (p [& srcmask]) >> k [& boundmask]."""
    fn, shpc, k, pv, sd, usepc, useop, base, bnd, bm = s
    m = re.match(r"and0x([0-9A-F]+)@", sd)
    if m: p &= int(m.group(1), 16)
    v = p >> k
    return v & bm if bm is not None else v
def verdict(s):
    """Evaluated: scalar (narrow source); then for a pointer-capable source, every heap and spill KSEG0 pointer is run through the
    index expression. k <= 22: OVERFLOW if a spill index exceeds the largest heap index (else bounded-safe: lands inside the table's
    heap range). k >= 23 (top-byte index, segment / KSEG tables): ALIAS if a spill index differs from the heap index (else spill-equal).
    Range checks (slt*) without a mask leave the outcome to the check: bounded-check, read by hand if a spill index would pass it."""
    fn, shpc, k, pv, sd, usepc, useop, base, bnd, bm = s
    if pv == "narrow" and not sd.startswith("and0x"): return "scalar"
    if bnd and bm is None: return "bounded-check"
    hi = {evalidx(s, p) for p in HEAPS}; sp = {evalidx(s, p) for p in SPILLS}
    m = re.match(r"and0x([0-9A-F]+)@", sd); top = k >= 23 or bool(m and int(m.group(1), 16) & 0xFE000000)
    if not top: return "bounded-safe" if max(sp) <= max(hi) else ("OVERFLOW" if bnd or sd.startswith("and0x") else "probe")
    return "spill-equal" if sp <= hi and len(hi) == 1 else ("spill-equal" if sp == hi else "ALIAS")

def main():
    if "--selftest" in sys.argv:
        S = scan([("self", SELFTEST)])
        V = {(x[0], x[1]): (verdict(x), x) for x in S}
        ok = V.get(("s7323FakeUnbounded", "0x80006004"), ("",))[0] == "probe" and V.get(("s7323FakeSeg", "0x80009008"), ("",))[0] == "ALIAS" and \
             V.get(("s7323FakeSeg", "0x80009024"), ("",))[0] == "bounded-safe" and V[("s7323FakeUnbounded", "0x80006004")][1][7] == "0x80130000" and \
             V.get(("s7323FakeBounded", "0x80007004"), ("",))[0] == "bounded-safe" and \
             V.get(("s7323FakeScalar", "0x80008004"), ("",))[0] == "scalar" and \
             V.get(("s7323FakeScalar", "0x80008014"), ("",))[0] == "probe" and V[("s7323FakeScalar", "0x80008014")][1][3] == "arg" and \
             not any(x[1] == "0x80008024" for x in S)  # no memory use -> not an index
        for x in S: print("  ", verdict(x), x)
        print("SELFTEST F=%d %s" % (len(S), "PASS" if ok else "FAIL")); return 0 if ok else 2
    srcs = [(p.name, p.read_text(errors="surrogateescape")) for p in sorted(GEN.glob("funcs_*.c"))]
    S = scan(srcs)
    # one row per shift site (first memory use)
    by = {}
    for s in S: by.setdefault(s[1], s)
    vc = Counter(); pc_ = Counter()
    rows = []
    for shpc, s in sorted(by.items()):
        v = verdict(s)
        if v in ("probe", "OVERFLOW", "ALIAS", "bounded-check"):
            v = ("known:" + v) if shpc in KNOWN_F else ("UNCLASSIFIED:" + v)
        vc[v.split(":")[0] if v.startswith("known") else v] += 1
        if "probe" in v: pc_[s[3]] += 1
        rows.append((v, s))
    print("F address-derived table index (srl/sra 8..22 -> memory base): %d shift sites, %d mem uses" % (len(by), len(S)))
    print("F verdicts: %s; raw unbounded word/arg/other sources before the hand read %s" % (dict(vc), dict(pc_)))
    for v, s in rows:
        fn, shpc, k, pv, sd, usepc, useop, base, bnd, kind = s
        print("  F %s %s >>%d@%s src=%s:%s use=%s@%s base=%s %s%s" % (v, fn, k, shpc, pv, sd, useop, usepc, base, ("by " + bnd) if bnd else "",
              (" => " + KNOWN_F[shpc]) if v.startswith("known") else ""))
    if "--sites" in sys.argv:
        out = pathlib.Path(sys.argv[sys.argv.index("--sites") + 1])
        R = []
        for v, s in rows:
            if v.startswith("UNCLASSIFIED"): R.append(s)
        with out.open("w") as f:
            f.write("# s7323 class-F unbounded address-derived index sites (tools/s7323_addr_index_census.py). idx(768+i) shiftpc srcreg fn k prov src base use\n")
            for i, s in enumerate(R):
                f.write("%d %s %s %s %d %s %s %s %s@%s\n" % (768 + i, s[1], "?", s[0], s[2], s[3], s[4].replace(" ", ""), s[7], s[6], s[5]))
        print("wrote %d probe sites -> %s" % (len(R), out))
    bad = sum(n for v, n in vc.items() if v.startswith("UNCLASSIFIED"))
    print("F unclassified: %d" % bad)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
