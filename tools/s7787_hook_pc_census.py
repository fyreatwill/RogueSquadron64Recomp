#!/usr/bin/env python3
"""s7787 gate: every pc LITERAL passed to a diagnostic hook must name the instruction it sits beside.
s7786 found the s4765 spin rewrite dropping a pc comment, so s4307 tagged two loads with the previous instruction's pc. This
generalises the check to every hook family in the generated tree.
Per generated function, each `rs64_*(...)` / `RS64_*(...)` call whose arguments contain a top-level 0x8XXXXXXXu literal (the
first such argument is taken as the hook's pc), and every `g_rs64_last_guest_pc = 0x...u;`, is classified against the
`// 0x<pc>: <op>` comments around it:
  EQ     literal == the current comment pc
  PRE    literal == the NEXT comment pc (hook emitted just before its instruction)
  DS     literal == the most recent branch/jump comment pc (current pc is its delay slot; N64Recomp emits the
         delay slot first, so a call-site hook after it names the jal/jr)
  TARGET literal == the operand of the jal/j just executed (hook names the callee entry)
  FUNC   literal == the enclosing function's entry pc (entry/return events)
  ENTRY  before the function's first pc comment, literal == the function's first pc
  KNOWN  family listed in KNOWN_SITE (passes a site constant on purpose)
  BAD    anything else (listed)
Also lists pc-less instruction comments (`// <op> ...` with no 0x pc) inside function bodies (s7786 found 2 from spin2).
Usage: s7787_hook_pc_census.py [--controls] [RecompiledFuncs dir]. Exit 0 iff hooks>0 and bad=0.
--controls: a planted EQ / off-by-4 / off-by-16 / PRE / DS / pc-less snippet must score EQ / BAD / BAD / PRE / DS / pcless=1,
else exit 3."""
import collections, pathlib, re, sys

PCC = re.compile(r"^\s*// 0x([0-9A-Fa-f]{8}):\s+(\S+)\s*(\S*)")
PCLESS = re.compile(r"^\s*// (?!0x)(?:addiu|addu|lw|lbu|lhu|lb|lh|sw|sb|sh|lui|ori|andi|beq|bne|beql|bnel|jal|jr|j|nop|sll|srl|"
                    r"sra|slt|sltu|slti|sltiu|subu|and|or|xor|nor|mult|multu|div|divu|mflo|mfhi|lwc1|swc1|ldc1|sdc1|ld|sd)\s+\S")
FN = re.compile(r"^(?:RECOMP_FUNC void (\w+)\(|void (\w+)\(uint8_t\* rdram, recomp_context\* ctx\) \{)")
CALL = re.compile(r"\b((?:rs64|RS64)_\w+)\(")
LASTPC = re.compile(r"g_rs64_last_guest_pc = 0x([0-9A-Fa-f]{8})u;")
LIT = re.compile(r"^0x(8[0-9A-Fa-f]{7})u$")
BRANCH = {"beq", "bne", "beql", "bnel", "blez", "bgtz", "bltz", "bgez", "blezl", "bgtzl", "bltzl", "bgezl", "bltzal", "bgezal",
          "bc1t", "bc1f", "bc1tl", "bc1fl", "j", "jal", "jr", "jalr", "b", "bal"}
# (family, literal) -> reason: hooks that pass a non-adjacent SITE ID on purpose (s7787 classified every one; keep this tight).
KNOWN_SITE = {
    **{(f, pc): "s2122/s7574 key-on divide witness: names the break-7 trap pc of the divide it guards (site id)"
       for f in ("rs64_s2122_m5_keyon_event", "rs64_s7574_keyon") for pc in (0x80090CEC, 0x80090D30, 0x80090D74, 0x80090DB8)},
    ("rs64_s2122_m5_keyon_event", 0x80090DE8): "s2122 key-on normal-tail event: names the epilogue's first lw (site id)",
    **{("rs64_tctr", pc): "s6826 fps60 float trace: one id per traced field, emitted together at 0x800C6D40"
       for pc in (0x800C6D44, 0x800C6D48, 0x800C6D4C)},
}


def call_args(ln, start):
    """Top-level comma-split args of the call whose '(' is at ln[start-1]; None if the call does not close on this line."""
    depth, cur, args = 1, [], []
    for ch in ln[start:]:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                args.append("".join(cur).strip()); return args
        if ch == "," and depth == 1:
            args.append("".join(cur).strip()); cur = []
        else:
            cur.append(ch)
    return None


def hooks_in(ln):
    out = []
    for m in CALL.finditer(ln):
        if m.group(1).startswith(("RS64_RAM", "RS64_U")):
            continue
        a = call_args(ln, m.end())
        if not a:
            continue
        for x in a:
            lm = LIT.match(x)
            if lm:
                out.append((m.group(1), int(lm.group(1), 16))); break
    for m in LASTPC.finditer(ln):
        out.append(("g_rs64_last_guest_pc", int(m.group(1), 16)))
    return out


def scan(text, name, cnt, bad, pcless):
    lines = text.splitlines()
    fn_first = None; in_fn = False
    seq = []          # (lineno, pc, op) comments of the current function
    pend = []         # (lineno, family, lit, idx_of_current_comment) awaiting the next comment
    def last_branch(ci, curpc):
        """pc of the most recent branch/jump comment before the current pc (skips N64Recomp's duplicated delay-slot comment)."""
        for j in range(ci, max(-1, ci - 4), -1):
            if seq[j][1] != curpc:
                return seq[j][1] if seq[j][2] in BRANCH else None
        return None
    def last_target(ci):
        """jal/j operand of the most recent jump comment within 3 comments (hook names the callee entry)."""
        for j in range(ci, max(-1, ci - 3), -1):
            if seq[j][2] in ("jal", "j") and seq[j][3].startswith("0x"):
                return int(seq[j][3], 16)
        return None
    def flush(next_pc):
        for (i, fam, lit, ci) in pend:
            cur = seq[ci] if ci is not None else None
            if cur is None:
                k = "ENTRY" if (lit == fn_first or lit == next_pc) else "BAD"
            elif lit == cur[1]:
                k = "EQ"
            elif next_pc is not None and lit == next_pc:
                k = "PRE"
            elif lit == last_branch(ci, cur[1]):
                k = "DS"
            elif lit == last_target(ci):
                k = "TARGET"
            elif lit == fn_first:
                k = "FUNC"
            elif (fam, lit) in KNOWN_SITE:
                k = "KNOWN"
            else:
                k = "BAD"
            cnt[fam][k] += 1
            if k == "BAD":
                bad.append((name, i + 1, fam, "0x%08X" % lit, "0x%08X" % cur[1] if cur else None))
        pend.clear()
    for i, ln in enumerate(lines):
        fm = FN.match(ln)
        if fm:
            flush(None); seq = []; fn_first = None; in_fn = True
            # first pc of the function = first comment after the header
            for ln2 in lines[i + 1:i + 400]:
                m2 = PCC.match(ln2)
                if m2:
                    fn_first = int(m2.group(1), 16); break
            continue
        m = PCC.match(ln)
        if m:
            pc = int(m.group(1), 16)
            flush(pc)
            seq.append((i, pc, m.group(2), m.group(3))); continue
        if in_fn and PCLESS.match(ln):
            pcless.append((name, i + 1, ln.strip()[:80]))
        for fam, lit in hooks_in(ln):
            pend.append((i, fam, lit, len(seq) - 1 if seq else None))
    flush(None)


def run(texts):
    cnt = collections.defaultdict(collections.Counter); bad = []; pcless = []
    for name, t in texts:
        scan(t, name, cnt, bad, pcless)
    return cnt, bad, pcless


def controls():
    hdr = "RECOMP_FUNC void f(uint8_t* rdram, recomp_context* ctx) {\n"
    cases = {
        "EQ": ("    // 0x80001000: sw $a0, 0x0($sp)\n    RS64_S5798_ST(0x80001000u, 0, ctx->r29, 4);\n"
               "    // 0x80001004: nop\n", "EQ"),
        "off4": ("    // 0x80001000: sw $a0, 0x0($sp)\n    // 0x80001004: nop\n    RS64_S5798_ST(0x80001000u, 0, ctx->r29, 4);\n"
                 "    // 0x80001008: nop\n", "BAD"),
        "off16": ("    // 0x80001000: sw $a0, 0x0($sp)\n    // 0x80001010: lhu $v1, 0x0($v1)\n"
                  "    rs64_f5_store_shadow_post('H', 0x80001000u, U32(ADD32(ctx->r1, 0)));\n    // 0x80001014: nop\n", "BAD"),
        "PRE": ("    // 0x80001000: nop\n    rs64_s4222_pc(rdram, 0x80001004u, 0u);\n    // 0x80001004: sw $v0, 0x0($at)\n", "PRE"),
        "DS": ("    // 0x80001000: jal 0x80002000\n    // 0x80001004: addiu $a2, $zero, 0x1\n"
               "    rs64_m5_frequency_caller(rdram, ctx, 0x80001000u);\n    // 0x80001008: nop\n", "DS"),
    }
    ok = True
    for k, (body, want) in cases.items():
        cnt, bad, _ = run([(k, hdr + "    // 0x80000FFC: nop\n" + body + "}\n")])
        got = [kk for c in cnt.values() for kk, v in c.items() if v]
        print("control %-5s want %-4s got %s" % (k, want, got)); ok &= got == [want]
    _, _, pl = run([("pcless", hdr + "    // 0x80001000: nop\n    // lbu         $t0, 0x0($a0)\n}\n")])
    print("control pcless want 1 got %d" % len(pl)); ok &= len(pl) == 1
    return ok


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--controls" in sys.argv and not controls():
        print("CONTROLS FAILED"); return 3
    d = pathlib.Path(args[0] if args else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    texts = [(p.name, p.read_text(errors="replace")) for p in sorted(d.glob("funcs_*.c"))]
    cnt, bad, pcless = run(texts)
    tot = collections.Counter()
    for fam, c in sorted(cnt.items(), key=lambda x: -sum(x[1].values())):
        tot.update(c)
        if set(c) - {"EQ"} or sum(c.values()) > 1000:
            print("%-40s %s" % (fam, dict(c)))
    print("TOTAL hooks=%d %s families=%d" % (sum(tot.values()), dict(tot), len(cnt)))
    for b in bad[:60]:
        print("BAD %s:%d %s lit=%s cur=%s" % b)
    for p in pcless[:20]:
        print("PCLESS %s:%d %s" % p)
    print("s7787 hooks=%d bad=%d pcless=%d" % (sum(tot.values()), len(bad), len(pcless)))
    return 0 if tot and not bad else 1


if __name__ == "__main__":
    sys.exit(main())
