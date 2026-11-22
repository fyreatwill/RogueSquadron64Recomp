#!/usr/bin/env python3
"""s7786 gate (load-side twin of s7785): every diagnostic LOAD hook must report the address and width of the load it instruments.
Keyed by pc inside each generated function:
  loads: ctx->X = MEM_W|MEM_WU|MEM_H|MEM_HU|MEM_B|MEM_BU|LD(ctx->rN, OFF)  and  do_lwl/do_lwr(rdram, dst, ctx->rN, OFF)
  hooks: RS64_S7484_LD(0xPCu, ctx->rN, OFF, w)            (s7484 UAF load watch; must precede the load on its line)
         RS64_S7487_LWX(0xPCu, k, ctx->rN, OFF, isl)      (s7487 lwl/lwr watch; isl=1 for lwl, 0 for lwr)
         s4575_a = U32(ADD32(ctx->rN, OFF)); ... rs64_s4307_synth_read(rdram, 0xPCu, s4575_a, ...)  (s4307; address taken first)
A hook is ok when (reg, off, width/isl) match the pc's load and it is evaluated before the load overwrites its destination.
Coverage: every guest load op (lw lwu lh lhu lb lbu ld lwc1 ldc1 lwl lwr) must carry its family's watch: s7484 for the aligned
forms, s7487 for lwl/lwr (s4307-joined sites count as watched only if s7484 also wraps them). Unwatched loads are listed.
Usage: s7786_load_hook_reg_census.py [--controls] [RecompiledFuncs dir]. Exit 0 iff hooks>0, bad=0, unwatched=0.
--controls: planted good / destination-register mutant / offset mutant / width mutant / after-load mutant snippets must score
ok=2 / bad=1 / bad=1 / bad=1 / bad=1, else exit 3."""
import collections, pathlib, re, sys

PCC = re.compile(r"^\s*// 0x([0-9A-Fa-f]{8}):\s+(\S+)\s*(\S*)")
LD_MEM = re.compile(r"(ctx->(?:[rf]\d+(?:\.\w+)?|f_odd\[[^\]]*\])) = (MEM_W|MEM_WU|MEM_H|MEM_HU|MEM_B|MEM_BU|LD)\((ctx->r\d+), (-?0X[0-9A-Fa-f]+|-?\d+)\)")
LD_UN = re.compile(r"(ctx->r\d+) = do_(lwl|lwr)\(rdram, ctx->r\d+, (ctx->r\d+), (-?0X[0-9A-Fa-f]+|-?\d+)\)")
HK_84 = re.compile(r"RS64_S7484_LD\(0x([0-9A-Fa-f]{8})u, (ctx->r\d+), (-?0X[0-9A-Fa-f]+|-?\d+), (\d+)\)")
HK_87 = re.compile(r"RS64_S7487_LWX\(0x([0-9A-Fa-f]{8})u, \d+, (ctx->r\d+), (-?0X[0-9A-Fa-f]+|-?\d+), ([01])\)")
HK_43 = re.compile(r"s4575_a = U32\(ADD32\((ctx->r\d+), (-?0X[0-9A-Fa-f]+|-?\d+)\)\);.*?rs64_s4307_synth_read\(rdram, 0x([0-9A-Fa-f]{8})u")
LD_AT = re.compile(r"(ctx->r\d+) = rs64_s4984_load_\w+\(rdram\)")
OPW = {"lw": 4, "lwu": 4, "lwc1": 4, "lh": 2, "lhu": 2, "lb": 1, "lbu": 1, "ld": 8, "ldc1": 8}
WID = {"MEM_W": 4, "MEM_WU": 4, "MEM_H": 2, "MEM_HU": 2, "MEM_B": 1, "MEM_BU": 1, "LD": 8, "lwl": 1, "lwr": 0}
LOAD_OPS = {"lw", "lwu", "lh", "lhu", "lb", "lbu", "ld", "lwc1", "ldc1", "lwl", "lwr"}
UNW = collections.Counter(); UNW_EX = []


def norm(o):
    return int(o, 16) if o.upper().lstrip("-").startswith("0X") and not o.startswith("-") else (
        -int(o[1:], 16) if o.upper().startswith("-0X") else int(o))


def scan(text, res, bad):
    for ch in re.split(r"(?m)^(?=RECOMP_FUNC\b|void \w+\(uint8_t\* rdram, recomp_context\* ctx\) \{)", text):
        scan_fn(ch, res, bad)


def scan_fn(text, res, bad):
    loads, ops, hooks = {}, {}, []
    pc = None
    for ln in text.splitlines():
        m = PCC.match(ln)
        if m:
            pc = int(m.group(1), 16); ops[pc] = m.group(2); continue
        if pc is None:
            continue
        lm = LD_MEM.search(ln) or LD_UN.search(ln)
        if lm and pc not in loads and ops.get(pc) in LOAD_OPS:
            loads[pc] = (lm.group(3), norm(lm.group(4)), WID[lm.group(2)], lm.group(1), lm.start())
        am = LD_AT.search(ln); jm = HK_43.search(ln)
        if am and jm and pc not in loads and ops.get(pc) in LOAD_OPS:   # s4984 atomic load: address = the s4575_a operand
            loads[pc] = (jm.group(1), norm(jm.group(2)), OPW[ops[pc]], am.group(1), am.start())
        for h in HK_84.finditer(ln):
            hooks.append(("RS64_S7484_LD", int(h.group(1), 16), h.group(2), norm(h.group(3)), int(h.group(4)), pc, h.start(), ln))
        for h in HK_87.finditer(ln):
            hooks.append(("RS64_S7487_LWX", int(h.group(1), 16), h.group(2), norm(h.group(3)), int(h.group(4)), pc, h.start(), ln))
        for h in HK_43.finditer(ln):
            hooks.append(("rs64_s4307_synth_read", int(h.group(3), 16), h.group(1), norm(h.group(2)), None, pc, h.start(), ln))
    watched = collections.defaultdict(set)
    for fam, hpc, reg, off, w, linepc, pos, ln in hooks:
        ld = loads.get(hpc)
        if ld is None:
            res[fam][2] += 1; bad.append("%s pc=%08X no load at that pc" % (fam, hpc)); continue
        lreg, loff, lw, dst, lpos = ld
        why = []
        if (reg, off) != (lreg, loff): why.append("addr hook=%s+%#x load=%s+%#x" % (reg, off, lreg, loff))
        if w is not None and w != lw: why.append("width hook=%d load=%d" % (w, lw))
        if linepc != hpc: why.append("hook under pc %08X" % linepc)
        elif pos > lpos and dst == reg: why.append("after load overwrote base %s" % reg)
        if why:
            res[fam][1] += 1; bad.append("%s pc=%08X %s" % (fam, hpc, "; ".join(why)))
        else:
            res[fam][0] += 1; watched[hpc].add(fam)
    for lpc, ld in loads.items():
        op = ops[lpc]; res["_loads"][0] += 1
        need = "RS64_S7487_LWX" if op in ("lwl", "lwr") else "RS64_S7484_LD"
        if need not in watched[lpc]:
            res["_loads"][1] += 1; UNW[op] += 1
            if len(UNW_EX) < 40: UNW_EX.append("%08X %s %s+%#x%s" % (lpc, op, ld[0], ld[1], " (s4307)" if watched[lpc] else ""))


def tot(t):
    r = collections.defaultdict(lambda: [0, 0, 0]); b = []
    scan(t, r, b); r.pop("_loads", None)
    return tuple(sum(v[i] for v in r.values()) for i in range(3))


def controls():
    good = ("    // 0x8008F9CC: lw          $v0, -0x6634($v0)\n"
            "    { RS64_S7484_LD(0x8008F9CCu, ctx->r2, -0X6634, 4); uint32_t s4575_a = U32(ADD32(ctx->r2, -0X6634)); ctx->r2 = MEM_W(ctx->r2, -0X6634); rs64_s4307_synth_read(rdram, 0x8008F9CCu, s4575_a, U32(ctx->r2)); }\n")
    dst = good.replace("RS64_S7484_LD(0x8008F9CCu, ctx->r2,", "RS64_S7484_LD(0x8008F9CCu, ctx->r5,", 1)
    off = good.replace("s4575_a = U32(ADD32(ctx->r2, -0X6634))", "s4575_a = U32(ADD32(ctx->r2, -0X6630))", 1)
    wid = good.replace("-0X6634, 4);", "-0X6634, 2);", 1)
    aft = ("    // 0x8004580C: lw          $v1, 0x60($v1)\n"
           "    { ctx->r3 = MEM_W(ctx->r3, 0X60); RS64_S7484_LD(0x8004580Cu, ctx->r3, 0X60, 4); }\n")
    g, d, o, w, a = tot(good), tot(dst), tot(off), tot(wid), tot(aft)
    okc = g == (2, 0, 0) and d == (1, 1, 0) and o == (1, 1, 0) and w == (1, 1, 0) and a == (0, 1, 0)
    print("controls: good=%s dst_reg=%s offset_mut=%s width_mut=%s after_load=%s %s" % (g, d, o, w, a, "PASS" if okc else "FAIL"))
    return okc


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--controls" in sys.argv and not controls():
        return 3
    UNW.clear(); UNW_EX.clear()
    d = pathlib.Path(args[0] if args else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    res = collections.defaultdict(lambda: [0, 0, 0]); bads = []
    for p in sorted(d.glob("funcs_*.c")):
        b = []; scan(p.read_text(errors="replace"), res, b); bads += ["%s: %s" % (p.name, x) for x in b]
    lw = res.pop("_loads", [0, 0])
    nh = sum(sum(v) for v in res.values()); nb = sum(v[1] + v[2] for v in res.values())
    print("loads=%d unwatched=%d by_op=%s" % (lw[0], lw[1], dict(UNW)))
    for u in UNW_EX[:12]:
        print("UNWATCHED", u)
    for k in sorted(res):
        print("family %-24s ok=%d bad=%d noload=%d" % (k, *res[k]))
    print("hooks=%d bad=%d" % (nh, nb))
    for s in bads[:12]:
        print("BAD", s)
    return 0 if nh > 0 and nb == 0 and lw[1] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
