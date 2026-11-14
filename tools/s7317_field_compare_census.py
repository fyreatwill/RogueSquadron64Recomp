#!/usr/bin/env python3
"""s7317: the struct-field edge of the spill-pointer bound class (after s6993 masks, s7315 constants, s7316 global words).

Two idioms over the original MIPS comments in N64Recomp/RecompiledFuncs (linear pass per function, delay-slot dedup, values killed
on any redefinition and on calls except callee-saved):
  A. TOP-BYTE SHIFT: `srl/sra d, s, k` with k >= 23 (extracts the address top byte / KSEG bits). Every such site whose result reaches
     a compare with a nonzero constant or a beq/bne against a constant register is listed: it is the shift form of the
     `(p & 0xFF000000) == 0x80000000` test that s6993 patched in its mask form. Address-agnostic, whole program.
  B. FIELD ORDER COMPARE: `lw d, off(base)` with a register base and off in the holder-field set (offsets of words that held live
     spill pointers in a dd8 21:9 L4 flight, tools/s7317_spill_holders.py --all output), then slt/sltu of d against another
     non-constant register. Lists the site and the other operand's provenance (another field load at offset o / unknown).
  C. FIELD POINTER DIFFERENCE (s7320): `subu d, x, y` where x or y is such a holder-field load and the other is non-constant;
     lists the other operand's provenance and the first 4 consumers of d (compare / shift / store / call arg).
Output: one line per site; an A site is spill-equal when every heap-range and spill-range KSEG0 pointer gives the same compare
outcome there (evaluated, not judged); exit 1 if any A site is not spill-equal and not in KNOWN_A; B sites are listed for manual classification (exit status unaffected).
--selftest runs both detectors on planted snippets (positive controls). Usage: s7317_field_compare_census.py <holders_all.txt> [--selftest]"""
import pathlib, re, sys

GEN = pathlib.Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs"
INS = re.compile(r"^\s*// (0x[0-9A-F]{8}): (\w+)\s*(.*)$")
FN = re.compile(r"^RECOMP_FUNC void (\w+)\(")
MEM = re.compile(r"^(-?0x[0-9A-Fa-f]+|-?\d+)\((\$\w+)\)$")
SAVED = ("$s0", "$s1", "$s2", "$s3", "$s4", "$s5", "$s6", "$s7", "$fp", "$sp", "$gp")
KNOWN_A = {}  # pc -> verdict, filled after reading each flagged site
SELFTEST = """RECOMP_FUNC void s7317FakeTopByte(uint8_t* rdram, recomp_context* ctx) {
    // 0x80001000: lw          $a0, 0x40($s1)
    // 0x80001004: srl         $v0, $a0, 24
    // 0x80001008: addiu       $at, $zero, 0x80
    // 0x8000100C: bne         $v0, $at, L_80001020
    // 0x80001010: srl         $v1, $a0, 28
    // 0x80001014: addiu       $at, $zero, 0x8
    // 0x80001018: bne         $v1, $at, L_80001020
RECOMP_FUNC void s7317FakeFieldOrder(uint8_t* rdram, recomp_context* ctx) {
    // 0x80002000: lw          $a0, 0xB0($s1)
    // 0x80002004: lw          $a1, 0x78($s1)
    // 0x80002008: sltu        $v0, $a0, $a1
RECOMP_FUNC void s7320FakeFieldDiff(uint8_t* rdram, recomp_context* ctx) {
    // 0x80003000: lw          $a0, 0xB0($s1)
    // 0x80003004: lw          $a1, 0x78($s2)
    // 0x80003008: subu        $v0, $a0, $a1
    // 0x8000300C: sltiu       $at, $v0, 0x100
    // 0x80003010: lw          $t0, 0x40($s3)
    // 0x80003014: addiu       $t1, $zero, 0x10
    // 0x80003018: subu        $t2, $t0, $t1
"""

def imm(s): return int(s, 0)

def scan(srcs, offs, C=None):
    A, B = [], []
    C = [] if C is None else C
    for name, text in srcs:
        fn, reg, seen = None, {}, set()
        for line in text.splitlines():
            m = FN.match(line)
            if m: fn, reg, seen = m.group(1), {}, set(); continue
            m = INS.match(line)
            if not m or fn is None: continue
            pc, op, args = m.groups()
            if pc in seen: continue
            seen.add(pc)
            a = [x.strip() for x in args.split(",")] if args else []
            d = a[0] if a else None
            new = None
            if op == "lui" and len(a) == 2: new = ("c", (imm(a[1]) << 16) & 0xFFFFFFFF)
            elif op in ("addiu", "ori") and len(a) == 3 and (a[1] == "$zero" or reg.get(a[1], ("",))[0] == "c"):
                b = 0 if a[1] == "$zero" else reg[a[1]][1]; v = imm(a[2])
                new = ("c", (b | (v & 0xFFFF)) if op == "ori" else (b + v) & 0xFFFFFFFF)
            elif op == "lw" and len(a) == 2:
                mm = MEM.match(a[1])
                if mm and mm.group(2) not in ("$sp",) and reg.get(mm.group(2), ("",))[0] != "c" and imm(mm.group(1)) in offs:
                    new = ("f", imm(mm.group(1)), pc, mm.group(2))
            elif op in ("srl", "sra") and len(a) == 3 and imm(a[2]) >= 23:
                new = ("t", imm(a[2]), pc, reg.get(a[1], ("?",)), op)
            elif op in ("addu", "or") and len(a) == 3 and a[2] == "$zero" and a[1] in reg:
                new = reg[a[1]]
            # uses
            if op in ("beq", "bne") and len(a) == 3:
                for x, y in ((a[0], a[1]), (a[1], a[0])):
                    tx, ty = reg.get(x), reg.get(y)
                    if tx and tx[0] == "t" and ty and ty[0] == "c" and ty[1] != 0:
                        A.append((fn, tx[2], pc, op, ty[1], tx[1], tx[3][0], tx[4]))
            if op in ("sltiu", "slti", "xori") and len(a) == 3 and reg.get(a[1], ("",))[0] == "t" and imm(a[2]) not in (0, 1):
                t = reg[a[1]]; A.append((fn, t[2], pc, op, imm(a[2]), t[1], t[3][0], t[4]))
            if op in ("slt", "sltu") and len(a) == 3:
                for x, y in ((a[1], a[2]), (a[2], a[1])):
                    tx, ty = reg.get(x), reg.get(y)
                    if tx and tx[0] == "t" and ty and ty[0] == "c" and ty[1] not in (0, 1):
                        A.append((fn, tx[2], pc, op, ty[1], tx[1], tx[3][0], tx[4]))
                    if tx and tx[0] == "f" and y != "$zero" and not (ty and ty[0] == "c"):
                        B.append((fn, tx[2], pc, op, tx[1], ("f+0x%X" % ty[1]) if ty and ty[0] == "f" else "other"))
                        break
            # class C consumers: every later read of a difference register
            srcs_ = a if op.startswith(("s", "b")) and op not in ("sll", "srl", "sra", "sllv", "srlv", "srav", "slt", "sltu", "slti", "sltiu", "sub", "subu") else a[1:]
            for x in srcs_:
                x = MEM.match(x).group(2) if MEM.match(x) else x
                tx = reg.get(x)
                if tx and tx[0] == "d" and len(C[tx[1]][-1]) < 4: C[tx[1]][-1].append("%s@%s" % (op, pc))
            if op in ("jal", "jalr"):
                for k, v in reg.items():
                    if v[0] == "d" and k in ("$a0", "$a1", "$a2", "$a3") and len(C[v[1]][-1]) < 4: C[v[1]][-1].append("arg%s>%s" % (k, a[0] if a else "?"))
            if op in ("subu", "sub") and len(a) == 3 and "$zero" not in (a[1], a[2]):
                tx, ty = reg.get(a[1]), reg.get(a[2])
                fx, fy = bool(tx and tx[0] == "f"), bool(ty and ty[0] == "f")
                if (fx and not (ty and ty[0] == "c")) or (fy and not (tx and tx[0] == "c")):
                    f, o = (tx, ty) if fx else (ty, tx)
                    prov = ("f+0x%X(%s)" % (o[1], o[3])) if o and o[0] == "f" else "other"
                    C.append([fn, f[2], pc, op, f[1], f[3], "p" if fx else "q", prov, a[1], a[2], []])
                    new = ("d", len(C) - 1)
            if d and d.startswith("$") and not op.startswith(("s", "b", "j")) or op in ("slt", "sltu", "slti", "sltiu", "sll", "srl", "sra", "sllv", "srlv", "srav", "sub", "subu"):
                reg.pop(d, None)
            if new is not None and d: reg[d] = new
            if op in ("jal", "jalr"): reg = {k: v for k, v in reg.items() if k in SAVED}
    return A, B

HEAP = (0x80000000, 0x80400000, 0x807FFFFC, 0x80BFFFFC)
SPILL = (0x81000000, 0x81200000, 0x813FFFFC)
def outcome(sh, k, op, c, p):
    v = (p >> k) if sh == "srl" else (((p - (1 << 32)) if p & 0x80000000 else p) >> k)
    c32 = c - (1 << 32) if c & 0x80000000 else c
    vs = v if sh == "sra" else v
    if op in ("beq", "bne"): return (v & 0xFFFFFFFF) == (c & 0xFFFFFFFF)
    if op == "xori": return (v ^ c) == 0
    if op in ("slti", "slt"): return (vs if sh == "sra" else v) < c32
    return (v & 0xFFFFFFFF) < (c & 0xFFFFFFFF)  # sltiu/sltu
def spill_equal(sh, k, op, c):
    """True when every heap-range and spill-range KSEG0 pointer gives the same compare outcome at this site."""
    return len({outcome(sh, k, op, c, p) for p in HEAP + SPILL}) == 1
def ptrshaped(k, c):  # constant a top-byte test of a KSEG pointer would use after a shift by k
    want = (0x80000000 >> k) & 0xFFFFFFFF
    return c in (want, want | 1) or (k >= 28 and c in (8, 0xA)) or c in (0x80, 0x81, 0x800, 0x8000)

def main():
    if "--selftest" in sys.argv:
        C = []; A, B = scan([("self", SELFTEST)], {0x40, 0xB0, 0x78}, C)
        ok = any(x[0] == "s7317FakeTopByte" and x[4] == 0x80 and not spill_equal(x[7], x[5], x[3], x[4]) for x in A) and \
             any(x[0] == "s7317FakeTopByte" and x[4] == 0x8 and spill_equal(x[7], x[5], x[3], x[4]) for x in A) and \
             any(x[0] == "s7317FakeFieldOrder" and x[5] == "f+0x78" for x in B) and \
             any(c[0] == "s7320FakeFieldDiff" and c[7] == "f+0x78($s2)" and any(u.startswith("sltiu@") for u in c[-1]) for c in C) and \
             not any(c[2] == "0x80003018" for c in C)  # constant subtrahend is not a pointer difference
        print("SELFTEST A=%d B=%d C=%d %s" % (len(A), len(B), len(C), "PASS" if ok else "FAIL")); return 0 if ok else 2
    offs = set()
    for ln in open(sys.argv[1]):
        m = re.match(r"^\s+LIVE \S+ owner=[0-9A-F]+\+0x([0-9A-F]+) ", ln)
        if m: offs.add(int(m.group(1), 16))
    srcs = [(p.name, p.read_text(errors="surrogateescape")) for p in sorted(GEN.glob("funcs_*.c"))]
    C = []; A, B = scan(srcs, offs, C)
    print("holder field offsets: %d (%s...)" % (len(offs), ",".join("0x%X" % o for o in sorted(offs)[:20])))
    bad = 0
    print("A top-byte shift compares: %d" % len(A))
    for fn, spc, pc, op, c, k, src, sh in A:
        ps = ptrshaped(k, c); eq = spill_equal(sh, k, op, c); unk = (not eq) and pc not in KNOWN_A; bad += unk
        print("  A %s %s@%s >>%d cmp@%s %s 0x%X src=%s %s %s%s" % (fn, sh, spc, k, pc, op, c, src, "PTR-SHAPED" if ps else "scalar",
              "spill-equal" if eq else "SPILL-DIFFERS", (" " + KNOWN_A[pc]) if pc in KNOWN_A else (" UNCLASSIFIED" if unk else "")))
    print("B field order compares: %d" % len(B))
    for fn, lpc, pc, op, o, other in B:
        print("  B %s lw+0x%X@%s %s@%s vs %s" % (fn, o, lpc, op, pc, other))
    print("C field pointer differences: %d" % len(C))
    for i, (fn, lpc, pc, op, o, base, side, other, rs, rt, uses) in enumerate(C):
        print("  C %d %s lw+0x%X(%s)@%s %s@%s %s,%s field=%s vs %s uses=%s" % (i, fn, o, base, lpc, op, pc, rs, rt, side, other, ";".join(uses) or "-"))
    print("A sites whose outcome differs heap vs spill, unclassified: %d" % bad)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
