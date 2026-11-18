#!/usr/bin/env python3
"""s7575 do_break idiom-class census (re-run of s4818 on the current regen, plus divisor proof).
Every do_break( site in RecompiledFuncs/funcs_*.c is classified:
  DATA      enclosing fn is data-as-code (>=50% of instruction comments are .word/do_break) or a known gap/RSP symbol
  B6-DEAD   break 6 (INT_MIN/-1) whose divisor's straight-line def is zero-extended/non-negative or a constant != -1
  B6-DIVU   break 6 that guards a divu (cannot overflow; dead by ISA)
  B7-CONST  break 7 whose divisor is a straight-line nonzero constant
  B7-LIVE   break 7 with a data-dependent divisor (fires iff the guest divides by zero; retail would raise Break too)
  B6-LIVE   break 6 with a possibly-negative data divisor
  GUARDED   a PATCH line precedes the do_break in the same block (already rewritten, e.g. musyxKeyOnVoice)
  OTHER     non-break mnemonic in a real-code fn (listed individually)
--controls: plants synthetic sites (constant-zero divisor, lhu divisor for break 6, data divisor) through the same
classifier and requires the expected classes. Exit 0 iff controls pass (when asked) and no OTHER/B6-LIVE is unlisted.
Usage: s7575_break_census.py [--controls] [--tsv OUT] [RecompiledFuncs dir]"""
import sys, re, pathlib, collections
args = [a for a in sys.argv[1:]]
CTL = "--controls" in args
tsv = None
if "--tsv" in args:
    tsv = args[args.index("--tsv") + 1]; del args[args.index("--tsv"):args.index("--tsv") + 2]
IRD = None
if "--ir" in args:
    IRD = args[args.index("--ir") + 1]; del args[args.index("--ir"):args.index("--ir") + 2]
args = [a for a in args if a != "--controls"]
# s7575 legit -O2 deletions (value proofs, not UB): _Genld divisor const 10 on every path; loadAssetAndIterateSubchunks
# divides only after `beq $fp,$zero` skips. Anything else data-dependent missing from the IR = a blind do_break.
IR_OK = {0x80036AD4, 0x80036AEC, 0x800550C4}
D = pathlib.Path(args[0] if args else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
fn_re = re.compile(r'^(?:RECOMP_FUNC\s+)?void\s+(\w+)\(')
ins_re = re.compile(r'// 0x([0-9A-Fa-f]{8}): (\S+)\s*(.*)$')
lab_re = re.compile(r'^\s*L_[0-9A-Fa-f]+:')
DATA_NAMES = re.compile(r'^(data_gap_|static_\d+_|rspbootText|audioCompandS16$|__OSGlobalIntMask$)')
STORES = {"sw", "sh", "sb", "sd", "swc1", "sdc1", "swl", "swr", "sc", "scd", "sdl", "sdr", "swc2"}
NONNEG = {"lhu", "lbu", "andi", "srl", "sltu", "slt", "slti", "sltiu"}

def regs(ops): return [r.strip() for r in ops.split(",")]

def lastdef(ins, i, reg):
    """walk back from index i (exclusive) inside the fn, straight-line only (stop at a label)."""
    j = i - 1
    while j >= 0:
        kind, mn, ops = ins[j]
        if kind == "label": return None
        if kind == "ins" and mn not in ("nop",) and not mn.startswith("b") and mn not in STORES:
            r = regs(ops)
            if r and r[0] == reg and mn not in ("div", "divu", "mult", "multu", "mtlo", "mthi", "jr", "jal", "j", "jalr"):
                return (mn, ops)
        if kind == "ins" and mn in ("jal", "jalr"): return ("call", "")
        j -= 1
    return None

def dend_nonneg(ins, dv, reg):
    d = lastdef(ins, dv, reg)
    if d is None: return False
    cmn, cops = d; cr = regs(cops)
    if cmn in NONNEG: return True
    if cmn in ("addiu", "ori") and len(cr) == 3 and cr[1] == "$zero": return int(cr[2], 0) >= 0
    return False

def classify_fn(name, ins, sites, out):
    nI = sum(1 for k, _, _ in ins if k == "ins")
    nW = sum(1 for k, m, _ in ins if k == "ins" and m == ".word")
    nB = sum(1 for k, _, _ in ins if k == "brk")
    data = DATA_NAMES.match(name or "") or (nB + nW) >= 0.5 * max(nI, 1)
    for idx in sites:
        vram, loc, patched = ins[idx][1], ins[idx][2], False
        # instruction comment that produced this do_break = last ins before idx
        j = idx - 1
        while j >= 0 and ins[j][0] != "ins":
            if ins[j][0] == "patch": patched = True
            j -= 1
        mn, ops = (ins[j][1], ins[j][2]) if j >= 0 else ("?", "")
        cls, why = None, ""
        if data: cls = "DATA"
        elif patched: cls = "GUARDED"
        elif mn == "break" and ops.strip() in ("6", "7"):
            code = ops.strip()
            k = j - 1; dv = None
            while k >= 0 and k > j - 30:
                if ins[k][0] == "ins" and ins[k][1] in ("div", "divu", "ddiv", "ddivu"): dv = k; break
                k -= 1
            if dv is None: cls, why = "B%s-LIVE" % code, "no div found"
            else:
                dmn, dops = ins[dv][1], ins[dv][2]
                r = regs(dops); divisor = r[-1]
                if code == "6" and dmn in ("divu", "ddivu"): cls, why = "B6-DIVU", dmn
                elif code == "6" and dend_nonneg(ins, dv, r[1]): cls, why = "B6-DEAD", "dividend %s non-negative" % r[1]
                elif divisor == "$zero": cls, why = ("B%s-%s" % (code, "LIVE" if code == "7" else "DEAD")), "zero reg"
                else:
                    d = lastdef(ins, dv, divisor)
                    if d is None: cls, why = "B%s-LIVE" % code, "divisor %s def not straight-line" % divisor
                    else:
                        cmn, cops = d; cr = regs(cops)
                        const = None
                        if cmn in ("addiu", "ori", "addi") and len(cr) == 3 and cr[1] == "$zero":
                            const = int(cr[2], 0)
                            if cmn == "addiu" or cmn == "addi": const = (const + 0x8000) % 0x10000 - 0x8000
                        if cmn == "lui" and len(cr) == 2: const = int(cr[1], 0) << 16
                        if const is not None:
                            if code == "7": cls = "B7-CONST" if const != 0 else "B7-ZERO"
                            else: cls = "B6-DEAD" if const != -1 and (const & 0xFFFFFFFF) != 0xFFFFFFFF else "B6-LIVE"
                            why = "%s=%d" % (divisor, const)
                        elif code == "6" and cmn in NONNEG: cls, why = "B6-DEAD", "%s %s non-negative" % (divisor, cmn)
                        elif code == "6" and dend_nonneg(ins, dv, r[1]): cls, why = "B6-DEAD", "dividend %s non-negative" % r[1]
                        else: cls, why = "B%s-LIVE" % code, "%s <- %s %s" % (divisor, cmn, cops)
        else: cls, why = "OTHER", "%s %s" % (mn, ops)
        out.append((cls, name, vram, loc, mn + " " + ops.strip(), why))

def scan_text(text, fname, out):
    name = None; ins = []; sites = []; last_vram = None
    def flush():
        if name is not None and sites: classify_fn(name, ins, sites, out)
    for n, l in enumerate(text.splitlines(), 1):
        m = fn_re.match(l)
        if m:
            flush(); name = m.group(1); ins = []; sites = []; continue
        if lab_re.match(l): ins.append(("label", "", "")); continue
        m = ins_re.search(l)
        if m: last_vram = m.group(1); ins.append(("ins", m.group(2), m.group(3))); continue
        if "PATCH" in l and "do_break" not in l: ins.append(("patch", "", ""))
        if "do_break(" in l and "void do_break" not in l and "extern" not in l:
            sites.append(len(ins)); ins.append(("brk", last_vram, "%s:%d" % (fname, n)))
    flush()

out = []
for p in sorted(D.glob("funcs_*.c")): scan_text(p.read_text(errors="replace"), p.name, out)
cnt = collections.Counter(c for c, *_ in out)
print("[s7575-break] sites=%d" % len(out), " ".join("%s=%d" % kv for kv in sorted(cnt.items())))
byfn = collections.defaultdict(collections.Counter)
for c, fn, *_ in out: byfn[c][fn] += 1
for c in sorted(byfn):
    if c == "DATA": print("  DATA fns:", len(byfn[c]), ", ".join("%s:%d" % kv for kv in byfn[c].most_common()))
for c, fn, vram, loc, ins_, why in out:
    if c in ("OTHER", "B6-LIVE", "B7-ZERO", "GUARDED"): print("  %-8s %-36s 0x%s %-22s %-20s %s" % (c, fn, vram, loc, ins_, why))
print("  B7-LIVE divisor defs:", collections.Counter(w.split(" <- ")[-1].split()[0] if " <- " in w else w for c, *_, w in out if c == "B7-LIVE").most_common(12))
print("  B7-LIVE fns (%d):" % len(byfn["B7-LIVE"]), ", ".join("%s:%d" % kv for kv in sorted(byfn["B7-LIVE"].items())))
if tsv:
    with open(tsv, "w") as f:
        f.write("class\tfn\tvram\tloc\tins\twhy\n")
        for r in out: f.write("\t".join(r[:2]) + "\t0x" + "\t".join(r[2:]) + "\n")
rc = 0
if CTL:
    def mk(defl, div, code):
        return ("RECOMP_FUNC void ctlfn(uint8_t* rdram, recomp_context* ctx) {\n" + "    // 0x80000000: addiu $sp, $sp, -0x18\n" * 6 +
                "    // 0x80000004: %s\n    // 0x80000008: %s\n    // 0x8000000C: bnez $v0, .L\n    // 0x80000010: nop\n"
                "    // 0x80000014: break       %s\n    do_break(2147483668);\n}\n" % (defl, div, code))
    cases = [("addiu       $v0, $zero, 0x0", "div $zero, $v1, $v0", "7", "B7-ZERO"),
             ("addiu       $v0, $zero, 0x5", "div $zero, $v1, $v0", "7", "B7-CONST"),
             ("lw          $v0, 0x4($s0)", "div $zero, $v1, $v0", "7", "B7-LIVE"),
             ("lhu         $v0, 0x4($s0)", "div $zero, $v1, $v0", "6", "B6-DEAD"),
             ("lw          $v0, 0x4($s0)", "div $zero, $v1, $v0", "6", "B6-LIVE"),
             ("lw          $v0, 0x4($s0)", "divu $zero, $v1, $v0", "6", "B6-DIVU"),
             ("addiu       $v0, $zero, -0x1", "div $zero, $v1, $v0", "6", "B6-LIVE"),
             ("sll         $v0, $a0, 2", "div $zero, $v1, $v0", "7", "B7-LIVE"),
             ("lhu         $v1, 0x4($s0)", "div $zero, $v1, $v0", "6", "B6-DEAD")]
    ok = 0
    for defl, div, code, want in cases:
        o = []; scan_text(mk(defl, div, code), "ctl.c", o)
        got = o[0][0] if o else None; ok += got == want
        if got != want: print("  CTL FAIL", defl, div, code, "want", want, "got", got)
    # data-as-code control
    o = []; scan_text("RECOMP_FUNC void ctl2(uint8_t* rdram, recomp_context* ctx) {\n    // 0x80000000: .word 0x0\n    // 0x80000004: .word 0x0\n    // 0x80000008: break 7\n    do_break(1);\n}\n", "ctl.c", o)
    ok += o[0][0] == "DATA"; n = len(cases) + 1
    print("[s7575-break] controls %d/%d" % (ok, n)); rc |= ok != n

# ---- sibling class: divides with NO compiler break-7 check (silent on retail AND port, but MIPS lo for x/0 is
# -1/+1 (div) or 0xFFFFFFFF (divu) while the generated C S64(a)/S64(0) gives 0 on arm64: a silent divergence iff hit).
def unchecked(D):
    res = []
    for p in sorted(D.glob("funcs_*.c")):
        name = None; seq = []
        def fl():
            if name is None: return
            nI = sum(1 for k, *_ in seq if k == "ins"); nW = sum(1 for k, m, *_ in seq if k == "ins" and m == ".word")
            nB = sum(1 for k, *_ in seq if k == "brk")
            if DATA_NAMES.match(name) or (nB + nW) >= 0.5 * max(nI, 1): return
            for i, (k, m, o, v) in enumerate(seq):
                if k == "ins" and m in ("div", "divu", "ddiv", "ddivu"):
                    win = [s for s in seq[i + 1:i + 16] if s[0] == "ins"][:8]
                    if not any(s[1] == "break" and s[2].strip() == "7" for s in win):
                        res.append((name, v, m, o.strip(), p.name))
        for l in p.read_text(errors="replace").splitlines():
            mm = fn_re.match(l)
            if mm: fl(); name = mm.group(1); seq = []; continue
            mm = ins_re.search(l)
            if mm: seq.append(("ins", mm.group(2), mm.group(3), mm.group(1)))
            elif "do_break(" in l: seq.append(("brk", "", "", ""))
        fl()
    return res
U = unchecked(D)
# a delay-slot duplicate comment makes one instruction appear twice; dedupe by vram
U = sorted({(n, v, m, o, f) for n, v, m, o, f in U}, key=lambda r: r[1])
print("[s7575-nochk] unchecked divides (real code)=%d" % len(U), collections.Counter(m for _, _, m, _, _ in U))
for n, c in collections.Counter(n for n, *_ in U).most_common(): print("   %-40s %d" % (n, c))
if IRD:
    live = set()
    for f in pathlib.Path(IRD).glob("*.calls"):
        for l in f.read_text().split():
            live.add(int(l) & 0xFFFFFFFF)
    blind = [(c, fn, v) for c, fn, v, *_ in out if c in ("B7-LIVE", "B6-LIVE") and int(v, 16) not in live and int(v, 16) not in IR_OK]
    kept = sum(1 for c, fn, v, *_ in out if c in ("B7-LIVE", "B6-LIVE") and int(v, 16) in live)
    print("[s7575-ir] live-class kept=%d legit_deleted=%d BLIND=%d" % (kept, len(IR_OK), len(blind)))
    for b in blind[:40]: print("   BLIND", *b)
    rc |= bool(blind)
print("[s7575-break] rc=%d" % rc)
sys.exit(rc)
