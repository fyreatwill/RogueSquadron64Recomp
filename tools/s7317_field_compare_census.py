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
  D. 24-BIT TRUNCATION (s7321): `and d, s, M` with M a constant register (lui/ori) or `sll t, s, k ; srl d, t, k`, where the kept-bit
     mask M (= 2^(32-k)-1 for the shift pair) lacks bit 24 but keeps bits 16..21 (M & 0x01000000 == 0 and M & 0x003F0000 == 0x003F0000; single-bit flag tests are not address masks): heap
     pointers 0x80000000-0x807FFFFF survive it as their physical address, a spill pointer 0x81xxxxxx loses bit 24 and aliases low RDRAM.
     Whole program (any non-constant source); src=f+0xNN marks a holder-field load. Masks keeping bit 24 (0x1FFFFFFF K0_TO_PHYS) are
     not listed. Lists the first 4 consumers of d.
  E. KSEG RE-TAG (s7322): `or/addu/xor d, x, K` with K a constant register whose low 24 bits are zero and top byte 0x80-0xBF (lui 0x8000,
     0xA000, ...): a value rebuilt into a KSEG pointer. x provenance: D (a class-D truncation result: already covered), narrow (andi,
     lhu/lh/lbu/lb, srl by 8..31: <= 24 significant bits, a spill pointer could not survive it), fpu (mfc1: the compiler's float->unsigned
     idiom `trunc.w ; mfc1 ; or 0x80000000` for values >= 2^31, a scalar), index (sll by < 8: a scaled index, with `lw off(d) ; jr` a jump
     table at 0x80000000+off), field/word (a full
     word: bit 24 intact if it was a physical address) or other (arg / unknown). Lists the first 4 consumers of d. Constants with nonzero
     low 24 bits (`lui 0x8013 ; addu at, at, idx` global-table indexing) are counted per provenance, not listed.
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
KNOWN_E = {  # s7322: narrow / other re-tags read by hand
    "0x80092608": "relocateSndPointer `(p & 0xFF000000) ^ 0x80000000` != 0 test = s6993 mask site 0x800925FC (patched, PTRMASK)",
    "0x80092614": "relocateSndPointer second test vs 0xB0000000 ROM tag = s6993 mask site 0x800925FC (patched, PTRMASK)",
    "0x800137CC": "renderLitMeshFaceGroup F5 DL command word 0xBD000000 | (byte & 0xFF): scalar, not an address",
    "0x80014618": "renderLitMeshFaceGroup F5 DL command word 0xBD000000 | (byte & 0xFF): scalar, not an address",
}
def e_verdict(op, K, prov, pc, uses):
    """s7322: evaluated class-E verdict; None = unclassified (exit 1)."""
    if pc in KNOWN_E: return "known: " + KNOWN_E[pc]
    if prov == "fpu": return "scalar: float->unsigned / sign idiom (mfc1 source)"
    if prov == "index" and any(u.startswith("BASE:lw") for u in uses): return "jump table at 0x%08X+off (scaled index)" % K
    if prov == "D": return "paired: class-D truncation result (s7321 runtime: 0 spill sources)"
    if prov == "word":  # full 32-bit source: or/xor/addu with K touch bits 24..31 only through K, so bit 24 survives iff K lacks it
        heap, spill = 0x00400000, 0x01200000  # physical forms; KSEG0 forms behave the same for or/xor/addu with bit-24-free K
        f = {"or": lambda x: x | K, "xor": lambda x: x ^ K, "addu": lambda x: (x + K) & 0xFFFFFFFF}[op]
        if all((f(v) & 0x01000000) == (v & 0x01000000) for v in (heap, spill, heap | 0x80000000, spill | 0x80000000)):
            return "spill-equal: full-word source keeps bit 24"
    return None
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
RECOMP_FUNC void s7322FakeRetag(uint8_t* rdram, recomp_context* ctx) {
    // 0x80005000: lw          $v1, 0x10($s1)
    // 0x80005004: lui         $t4, 0xFF
    // 0x80005008: ori         $t4, $t4, 0xFFFF
    // 0x8000500C: and         $v0, $v1, $t4
    // 0x80005010: lui         $at, 0x8000
    // 0x80005014: or          $a0, $v0, $at
    // 0x80005018: sw          $zero, 0x0($a0)
    // 0x8000501C: lhu         $t5, 0x4($s1)
    // 0x80005020: lui         $t6, 0x8000
    // 0x80005024: addu        $a1, $t5, $t6
    // 0x80005028: lw          $t7, 0x8($s1)
    // 0x8000502C: lui         $t8, 0x8000
    // 0x80005030: addu        $a2, $t7, $t8
    // 0x80005034: andi        $t9, $a3, 0xFF
    // 0x80005038: lui         $at, 0x8013
    // 0x8000503C: addu        $at, $at, $t9
RECOMP_FUNC void s7321FakeTrunc(uint8_t* rdram, recomp_context* ctx) {
    // 0x80004000: lw          $a0, 0xB0($s1)
    // 0x80004004: lui         $at, 0xFF
    // 0x80004008: ori         $at, $at, 0xFFFF
    // 0x8000400C: and         $v0, $a0, $at
    // 0x80004010: sw          $v0, 0x4($s2)
    // 0x80004014: lui         $t0, 0x1FFF
    // 0x80004018: ori         $t0, $t0, 0xFFFF
    // 0x8000401C: and         $v1, $a0, $t0
    // 0x80004020: sll         $t1, $a2, 8
    // 0x80004024: srl         $t2, $t1, 8
    // 0x80004028: sll         $t3, $a2, 3
    // 0x8000402C: srl         $t4, $t3, 3
"""

def imm(s): return int(s, 0)

def trunc_alias(M):
    return (M & 0x01000000) == 0 and (M & 0x003F0000) == 0x003F0000

def scan(srcs, offs, C=None, D=None, E=None, G=None):
    A, B = [], []
    E = [] if E is None else E
    G = {} if G is None else G
    C = [] if C is None else C
    D = [] if D is None else D
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
            if new is None and len(a) >= 2:
                if op == "andi": new = ("n", "andi0x%X@%s" % (imm(a[2]), pc))
                elif op in ("lhu", "lh", "lbu", "lb"): new = ("n", "%s@%s" % (op, pc))
                elif op == "srl" and len(a) == 3 and 8 <= imm(a[2]) < 23: new = ("n", "srl%s@%s" % (a[2], pc))
                elif op == "lw": new = ("w", "lw %s@%s" % (a[1], pc))
                elif op == "mfc1": new = ("u", "mfc1@%s" % pc)
                elif op == "sll" and len(a) == 3 and imm(a[2]) < 8: new = ("i", "sll%s@%s" % (a[2], pc))
            if op in ("or", "addu", "xor") and len(a) == 3 and "$zero" not in (a[1], a[2]):
                for x, y in ((a[1], a[2]), (a[2], a[1])):
                    tx, ty = reg.get(x), reg.get(y)
                    if ty and ty[0] == "c" and not (tx and tx[0] == "c") and 0x80 <= (ty[1] >> 24) <= 0xBF:
                        if not tx: prov, det = "other", x
                        elif tx[0] == "D": prov, det = "D", "D%d" % tx[1]
                        elif tx[0] in ("n", "t"): prov, det = "narrow", tx[1] if tx[0] == "n" else "srl%d@%s" % (tx[1], tx[2])
                        elif tx[0] == "u": prov, det = "fpu", tx[1]
                        elif tx[0] == "i": prov, det = "index", tx[1]
                        elif tx[0] in ("f", "w"): prov, det = "word", ("f+0x%X(%s)" % (tx[1], tx[3])) if tx[0] == "f" else tx[1]
                        else: prov, det = "other", "%s:%s" % (x, tx[0])
                        if ty[1] & 0x00FFFFFF == 0:
                            E.append([fn, pc, op, ty[1], prov, det, []]); new = ("E", len(E) - 1)
                        else:
                            G[prov] = G.get(prov, 0) + 1
                        break
            def srcname(r):
                t = reg.get(r)
                return ("f+0x%X(%s)" % (t[1], t[3])) if t and t[0] == "f" else r
            if op == "and" and len(a) == 3 and "$zero" not in (a[1], a[2]):
                for x, y in ((a[1], a[2]), (a[2], a[1])):
                    tx, ty = reg.get(x), reg.get(y)
                    if ty and ty[0] == "c" and not (tx and tx[0] == "c"):
                        if trunc_alias(ty[1]):
                            D.append([fn, pc, "and", ty[1], srcname(x), x, []]); new = ("D", len(D) - 1)
                        break
            if op == "sll" and len(a) == 3 and imm(a[2]) >= 8 and not (reg.get(a[1], ("",))[0] == "c"):
                new = ("s", imm(a[2]), pc, srcname(a[1]), a[1])
            if op == "srl" and len(a) == 3 and reg.get(a[1], ("",))[0] == "s" and reg[a[1]][1] == imm(a[2]):
                k = imm(a[2]); M = (1 << (32 - k)) - 1
                if trunc_alias(M):
                    D.append([fn, pc, "sll%d+srl@%s" % (k, reg[a[1]][2]), M, reg[a[1]][3], reg[a[1]][4], []]); new = ("D", len(D) - 1)
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
                isbase = bool(MEM.match(x))
                x = MEM.match(x).group(2) if isbase else x
                tx = reg.get(x)
                if tx and tx[0] == "E" and isbase and len(E[tx[1]][-1]) < 4: E[tx[1]][-1].append("BASE:%s@%s" % (op, pc)); continue
                if tx and tx[0] == "d" and len(C[tx[1]][-1]) < 4: C[tx[1]][-1].append("%s@%s" % (op, pc))
                if tx and tx[0] == "D" and len(D[tx[1]][-1]) < 4: D[tx[1]][-1].append("%s@%s" % (op, pc))
                if tx and tx[0] == "E" and len(E[tx[1]][-1]) < 4: E[tx[1]][-1].append("%s@%s" % (op, pc))
            if op in ("jal", "jalr"):
                for k, v in reg.items():
                    if v[0] == "d" and k in ("$a0", "$a1", "$a2", "$a3") and len(C[v[1]][-1]) < 4: C[v[1]][-1].append("arg%s>%s" % (k, a[0] if a else "?"))
                    if v[0] == "D" and k in ("$a0", "$a1", "$a2", "$a3") and len(D[v[1]][-1]) < 4: D[v[1]][-1].append("arg%s>%s" % (k, a[0] if a else "?"))
                    if v[0] == "E" and k in ("$a0", "$a1", "$a2", "$a3") and len(E[v[1]][-1]) < 4: E[v[1]][-1].append("arg%s>%s" % (k, a[0] if a else "?"))
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
        C, D, E, G = [], [], [], {}; A, B = scan([("self", SELFTEST)], {0x40, 0xB0, 0x78}, C, D, E, G)
        byp = {x[1]: x for x in E}
        okE = byp.get("0x80005014", [0] * 7)[4] == "D" and any(u.startswith("BASE:sw@") for u in byp["0x80005014"][-1]) and \
              byp.get("0x80005024", [0] * 7)[4] == "narrow" and byp.get("0x80005030", [0] * 7)[4] == "word" and \
              "0x8000503C" not in byp and G.get("narrow", 0) == 1 and \
              e_verdict("or", 0x80000000, "D", "0x80005014", []) and e_verdict("addu", 0x80000000, "narrow", "0x80005024", []) is None and \
              e_verdict("addu", 0x80000000, "word", "0x80005030", []) and e_verdict("or", 0x81000000, "word", "x", []) is None
        okD = any(x[1] == "0x8000400C" and x[4] == "f+0xB0($s1)" and x[3] == 0xFFFFFF and any(u.startswith("sw@") for u in x[-1]) for x in D) and \
              any(x[1] == "0x80004024" and x[3] == 0xFFFFFF for x in D) and \
              not any(x[1] in ("0x8000401C", "0x8000402C") for x in D)  # 0x1FFFFFFF and a 29-bit shift pair keep bit 24
        ok = any(x[0] == "s7317FakeTopByte" and x[4] == 0x80 and not spill_equal(x[7], x[5], x[3], x[4]) for x in A) and \
             any(x[0] == "s7317FakeTopByte" and x[4] == 0x8 and spill_equal(x[7], x[5], x[3], x[4]) for x in A) and \
             any(x[0] == "s7317FakeFieldOrder" and x[5] == "f+0x78" for x in B) and \
             any(c[0] == "s7320FakeFieldDiff" and c[7] == "f+0x78($s2)" and any(u.startswith("sltiu@") for u in c[-1]) for c in C) and \
             not any(c[2] == "0x80003018" for c in C) and okD and okE  # constant subtrahend is not a pointer difference
        print("SELFTEST A=%d B=%d C=%d D=%d E=%d %s" % (len(A), len(B), len(C), len(D), len(E), "PASS" if ok else "FAIL")); return 0 if ok else 2
    offs = set()
    for ln in open(sys.argv[1]):
        m = re.match(r"^\s+LIVE \S+ owner=[0-9A-F]+\+0x([0-9A-F]+) ", ln)
        if m: offs.add(int(m.group(1), 16))
    srcs = [(p.name, p.read_text(errors="surrogateescape")) for p in sorted(GEN.glob("funcs_*.c"))]
    C, D, E, G = [], [], [], {}; A, B = scan(srcs, offs, C, D, E, G)
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
    print("D 24-bit truncations (mask lacks bit 24, keeps bits 16-21): %d (holder-field source %d)" % (len(D), sum(x[4].startswith("f+") for x in D)))
    for i, (fn, pc, how, M, src, r, uses) in enumerate(D):
        print("  D %d %s %s@%s mask=0x%X src=%s reg=%s uses=%s" % (i, fn, how, pc, M, src, r, ";".join(uses) or "-"))
    from collections import Counter
    print("E KSEG re-tags (K low 24 bits zero): %d by provenance %s; global-base adds (not listed) %s" % (len(E), dict(Counter(x[4] for x in E)), G))
    vc = Counter()
    for i, (fn, pc, op, K, prov, det, uses) in enumerate(E):
        v = e_verdict(op, K, prov, pc, uses); bad += v is None; vc[(v or "UNCLASSIFIED").split(":")[0]] += 1
        print("  E %d %s %s@%s K=0x%08X src=%s %s uses=%s => %s" % (i, fn, op, pc, K, prov, det, ";".join(uses) or "-", v or "UNCLASSIFIED"))
    print("E verdicts: %s" % dict(vc))
    print("A sites whose outcome differs heap vs spill + E re-tags, unclassified: %d" % bad)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
