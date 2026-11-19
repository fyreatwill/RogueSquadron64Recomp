#!/usr/bin/env python3
"""s7316: retail pointer-vs-DATA-word bound census (the s7315 method limit: s7315 reads only lui-built constants, so a bound
held in a global word, e.g. a heap end or arena top, is invisible to it). Reads the original MIPS comments in the live
RecompiledFuncs tree; per function, a linear pass tracks registers that hold lui/addiu/ori constants and registers loaded
with `lw` from a constant address (a global word G). Every `slt`/`sltu` whose one operand is G and whose other operand is not
a constant is a site. With --ram <rdram dump(s)> (ROGUESQ_RDRAM_DUMP_DIR files, host order ^3), each G is read at runtime:
a G holding a KSEG0 pointer (0x80000000..0x81400000) makes the site a pointer-bound test that needs a VERDICT; a scalar G
(counts, sizes, timers) is classed automatically. Exit 1 if a pointer-valued site is unclassified.
Method limit: linear pass, no CFG (a constant base set on one path is assumed on all later paths); G loaded through a
register base (struct field) is not followed. Usage: tools/s7316_data_bound_census.py [--ram f.bin ...] [--all] [--selftest]"""
import pathlib, re, struct, subprocess, sys

GEN = pathlib.Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs"
INS = re.compile(r"^\s*// (0x[0-9A-F]{8}): (\w+)\s*(.*)$")
FN = re.compile(r"^RECOMP_FUNC void (\w+)\(")
MEM = re.compile(r"^(-?0x[0-9A-Fa-f]+|-?\d+)\((\$\w+)\)$")
SPILL_TOP = 0x81400000
# G address -> verdict for pointer-valued globals (s7316 run: L1 16:9 dd2 OSMEM 12, spill 0x81000000 live, 29 dumps).
GV = {
    0x801163D4: "DL pool limit word (allocateDisplayListBuffer); compared with DL write pointers from the same pool. Pool is "
                "carved at init from the main heap (runtime 0x80917B28..0x80B66720), never spill-served (spill max req 0x8000)",
    0x8011DC58: "DL chunk pointer of the same pool, compared with the 0x801163D4 limit; same range, below 16 MB",
    0x801163B0: "frame RDP-init DL pointer (emitFrameRdpInitDl), compared with the pool limit; same pool",
    0x8010FF18: "heap head block (initMainHeap/coalesceFreeHeapBlocks chain walk); spill blocks never join the chain: the "
                "rs_free hook returns on rs64_s6569_isspill before the walk, and rs_malloc only spills after the heap fails",
}
VERDICT = {}  # (function, G address) -> per-site override
SELFTEST = """RECOMP_FUNC void s7316FakeArenaTop(uint8_t* rdram, recomp_context* ctx) {
    // 0x80001000: lui         $v0, 0x8011
    // 0x80001004: lw          $v0, -0xE8($v0)
    // 0x80001008: sltu        $v1, $a0, $v0
"""
def imm(s): return int(s, 0)

def scan(srcs):
    sites = []
    for name, text in srcs:
        fn, reg, seen = None, {}, set()
        for line in text.splitlines():
            m = FN.match(line)
            if m: fn, reg, seen = m.group(1), {}, set(); continue
            m = INS.match(line)
            if not m or fn is None: continue
            pc, op, args = m.groups()
            if pc in seen: continue   # delay slots are printed twice
            seen.add(pc)
            a = [x.strip() for x in args.split(",")] if args else []
            d = a[0] if a else None
            if op == "lui": reg[d] = ("c", (imm(a[1]) << 16) & 0xFFFFFFFF); continue
            if op in ("addiu", "ori") and len(a) == 3 and reg.get(a[1], ("",))[0] == "c":
                b = reg[a[1]][1]; v = imm(a[2])
                reg[d] = ("c", (b | v) if op == "ori" else (b + v) & 0xFFFFFFFF); continue
            if op == "lw" and len(a) == 2:
                mm = MEM.match(a[1])
                if mm and reg.get(mm.group(2), ("",))[0] == "c":
                    reg[d] = ("g", (reg[mm.group(2)][1] + imm(mm.group(1))) & 0xFFFFFFFF, pc); continue
            if op in ("slt", "sltu") and len(a) == 3:
                for side, (x, y) in (("rs", (a[1], a[2])), ("rt", (a[2], a[1]))):
                    gx, gy = reg.get(x), reg.get(y, ("",))
                    if gx and gx[0] == "g" and gy[0] != "c" and y != "$zero":
                        sites.append(dict(fn=fn, pc=pc, op=op, g=gx[1], ldpc=gx[2], side=side, other=y))
            # any other write to d kills its tracked value (stores/branches have no destination register)
            if d and d.startswith("$") and not op.startswith(("s", "b", "j")) or op in ("slt", "sltu", "slti", "sltiu", "sll", "srl", "sra", "sllv", "srlv", "srav", "sub", "subu"):
                reg.pop(d, None)
            if op in ("jal", "jalr"): reg = {k: v for k, v in reg.items() if k in ("$s0","$s1","$s2","$s3","$s4","$s5","$s6","$s7","$fp","$sp","$gp")}
    return sites

def ramword(rams, g):
    vals = []
    for r in rams:
        p = g & 0x1FFFFFFF
        if p + 4 > len(r): vals.append(None); continue
        vals.append(struct.unpack_from("<I", r, p)[0])  # rdram is host order with ^3 swizzle -> aligned words read as LE u32
    return vals

def main():
    argv = sys.argv[1:]
    rams = []
    if "--ram" in argv:
        i = argv.index("--ram"); files = []
        for f in argv[i + 1:]:
            if f.startswith("--"): break
            files.append(f)
        # s7658: *.zst dumps (the retained scratch/s7316/ram set) are read through zstd -dc
        rams = [subprocess.run(["zstd", "-dc", f], capture_output=True, check=True).stdout if f.endswith(".zst")
                else pathlib.Path(f).read_bytes() for f in files]
    if "--selftest" in argv:
        s = scan([("selftest", SELFTEST)])
        ok = len(s) == 1 and s[0]["g"] == 0x8010FF18
        print("selftest", "PASS" if ok else "FAIL", s); return 0 if ok else 1
    srcs = [(f.name, f.read_text(errors="replace")) for f in sorted(GEN.glob("funcs_*.c"))]
    sites = scan(srcs)
    unc = 0; byg = {}
    for s in sites:
        vals = ramword(rams, s["g"]) if rams else []
        ptr = any(v is not None and 0x80000000 <= v < SPILL_TOP for v in vals)
        v = VERDICT.get((s["fn"], s["g"])) or GV.get(s["g"])
        if any(x is not None and 0x81000000 <= x < SPILL_TOP for x in vals): v = None; s["spill"] = 1  # H-reject candidate
        # s7658: a G no dump covers (truncated dump) has no runtime value: it stays unclassified, not "scalar ()"
        if v is None and rams and not ptr and any(x is not None for x in vals): v = "scalar G at runtime (" + ",".join("%X" % x for x in vals if x is not None) + ")"
        if v is None: unc += 1
        s["v"] = v; s["vals"] = vals
        byg.setdefault(s["g"], []).append(s)
    for g in sorted(byg):
        for s in byg[g]:
            if "--all" in argv or not s["v"] or (s is byg[g][0] and not s["v"].startswith("scalar")):
                print("%08X %-40s %s %s %s(ld %s) other=%s vals=%s :: %s" % (g, s["fn"], s["pc"], s["op"], s["side"], s["ldpc"], s["other"],
                      ",".join("%08X" % x for x in s["vals"] if x is not None), s["v"] or "UNCLASSIFIED"))
    nsp = sum(1 for x in sites if x.get("spill"))
    print("sites=%d globals=%d unclassified=%d spill_valued_sites=%d ram_dumps=%d" % (len(sites), len(byg), unc, nsp, len(rams)))
    return 1 if unc else 0
sys.exit(main())
