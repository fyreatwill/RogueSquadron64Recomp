#!/usr/bin/env python3
"""s7785 gate (class audit, generalises s7784): every diagnostic STORE hook that reports an address must report the address of
the store it instruments, i.e. its ADD32(ctx->rN, OFF) must equal the (base, offset) of the guest store at the same pc.
s7784 found tools/apply_s5660_unaligned_store_census.py passing the VALUE register (all 404 swl/swr/sdl/sdr hooks). This gate
checks every hook family in the generated tree with one rule, keyed by pc:
  hooks: any call  f('X', 0xPCu, U32(ADD32(ctx->rN, OFF)), ...)  (writer_parity, probe_submit_gate_store, f5_store_shadow_post,
         lowfield_store, ...), the s5660 form  ADD32(ctx->rN, OFF)) & ~3u; rs64_s5660_ustore(0xPCu, and the macros
         RS64_S5798_ST(0xPCu, OFF, ctx->rN, w) / RS64_S7488_UST(0xPCu, k, ctx->rN, OFF, w).
  stores: MEM_W/H/B/D(OFF, ctx->rN) = ..., SD(..., OFF, ctx->rN) and do_swl/swr/sdl/sdr(rdram, OFF, ctx->rN, val).
A hook is ok when the pc's store has the same (reg, offset); bad when it differs; nostore when the pc has no store (a load-hook or
a hook family this gate does not model: reported, not failed, unless the family is a known store hook).
Usage: s7785_store_hook_reg_census.py [--controls] [RecompiledFuncs dir]. Exit 0 iff hooks>0, every guest store is watched, and bad=0 and known-family nostore=0 (s4984 fixed-address atomic stores are listed as abs:<family>, exempt).
--controls (iron rule 1): planted good/value-register/offset-mutant snippets must score ok=2 / bad=1 / bad=1, else exit 3."""
import collections, pathlib, re, sys

PCC = re.compile(r"^\s*// 0x([0-9A-Fa-f]{8}):\s+(\S+)")
ST_MEM = re.compile(r"\bMEM_[WHBD]\((-?0X[0-9A-Fa-f]+|-?\d+), (ctx->r\d+)\) =")
ST_ABS = re.compile(r"__atomic_store_n\(\(uint(?:8|16|32|64)_t\*\)\(rdram \+ 0x[0-9A-Fa-f]+u\)")  # s4984 fixed-address atomic stores
ST_SD = re.compile(r"\bSD\([^;]*?, (-?0X[0-9A-Fa-f]+|-?\d+), (ctx->r\d+)\);")
ST_UN = re.compile(r"\bdo_s(?:wl|wr|dl|dr)\(rdram, (-?0X[0-9A-Fa-f]+|-?\d+), (ctx->r\d+), (?:ctx->r\d+|0)\);")
HK_FN = re.compile(r"\b(rs64_\w+)\('[A-Za-z]', 0x([0-9A-Fa-f]{8})u, U32\(ADD32\((ctx->r\d+), (-?0X[0-9A-Fa-f]+|-?\d+)\)\)")
HK_UN = re.compile(r"ADD32\((ctx->r\d+), (-?0X[0-9A-Fa-f]+|-?\d+)\)\) & ~3u; (rs64_s5660_ustore)\(0x([0-9A-Fa-f]{8})u")
HK_58 = re.compile(r"\b(RS64_S5798_ST)\(0x([0-9A-Fa-f]{8})u, (-?0X[0-9A-Fa-f]+|-?\d+), (ctx->r\d+), \d+\)")
HK_74 = re.compile(r"\b(RS64_S7488_UST)\(0x([0-9A-Fa-f]{8})u, \d+, (ctx->r\d+), (-?0X[0-9A-Fa-f]+|-?\d+), \d+\)")
STORE_OPS = {"sb", "sh", "sw", "sd", "swl", "swr", "sdl", "sdr", "swc1", "sdc1"}
UNW = []   # guest stores with no store-watch hook (writer_parity / s5660): the s6843 STORE_WATCH is blind to them
KNOWN = {"rs64_m5_writer_parity", "rs64_probe_submit_gate_store", "rs64_f5_store_shadow_post", "rs64_s5660_ustore",
         "RS64_S5798_ST", "RS64_S7488_UST", "rs64_m5_lowfield_store"}


def norm(o):
    return int(o, 0) if not o.upper().startswith(("0X", "-0X")) else int(o, 16)


FUNC = re.compile(r"^(?:RECOMP_FUNC|void|static void)\b[^;]*\(uint8_t\* rdram, recomp_context\* ctx\)")


def scan(text):
    res = collections.defaultdict(lambda: [0, 0, 0]); bad = []
    chunks = re.split(r"(?m)^(?=RECOMP_FUNC\b|void \w+\(uint8_t\* rdram, recomp_context\* ctx\) \{)", text)
    for ch in chunks:
        scan_fn(ch, res, bad)
    return res, bad


def scan_fn(text, res, bad):
    stores, ops, hooks, absst = {}, {}, [], set()
    pc = None
    for ln in text.splitlines():
        m = PCC.match(ln)
        if m:
            pc = int(m.group(1), 16); ops[pc] = m.group(2); continue
        for r in (ST_MEM, ST_SD, ST_UN):
            s = r.search(ln)
            if s and pc is not None and pc not in stores:
                stores[pc] = (s.group(2), norm(s.group(1)))
        if ST_ABS.search(ln) and pc is not None:
            absst.add(pc)
        for m in HK_FN.finditer(ln):
            hooks.append((m.group(1), int(m.group(2), 16), m.group(3), norm(m.group(4))))
        for m in HK_UN.finditer(ln):
            hooks.append((m.group(3), int(m.group(4), 16), m.group(1), norm(m.group(2))))
        for m in HK_58.finditer(ln):
            hooks.append((m.group(1), int(m.group(2), 16), m.group(4), norm(m.group(3))))
        for m in HK_74.finditer(ln):
            hooks.append((m.group(1), int(m.group(2), 16), m.group(3), norm(m.group(4))))
    watched = {h[1] for h in hooks if h[0] in ("rs64_m5_writer_parity", "rs64_s5660_ustore")}
    for spc in stores:
        if ops.get(spc, "") in STORE_OPS:
            res["_stores"][0] += 1
            if spc not in watched:
                res["_stores"][1] += 1
                if len(UNW) < 12: UNW.append("%08X %s %s+%#x" % (spc, ops[spc], stores[spc][0], stores[spc][1]))
    for fam, hpc, reg, off in hooks:
        st = stores.get(hpc)
        if st is None and hpc in absst:
            res["abs:" + fam][0] += 1; continue   # s4984 atomic store: address is a constant (lui $at), not a register
        if st is None or ops.get(hpc, "") not in STORE_OPS:
            res[fam][2] += 1; continue
        if st == (reg, off):
            res[fam][0] += 1
        else:
            res[fam][1] += 1; bad.append("%s pc=%08X hook=%s+%#x store=%s+%#x" % (fam, hpc, reg, off, st[0], st[1]))


def controls():
    good = ("    // 0x8000D5A8: swl         $a0, 0x0($v1)\n"
            "    { uint32_t s5660_a = U32(ADD32(ctx->r3, 0X0)) & ~3u; rs64_s5660_ustore(0x8000D5A8u, s5660_a, 0u, 'L'); } /* PATCH: s5660 */\n"
            "    { RS64_S7488_UST(0x8000D5A8u, 178, ctx->r3, 0X0, 1); do_swl(rdram, 0X0, ctx->r3, ctx->r4); }\n")
    val = good.replace("ADD32(ctx->r3, 0X0)) & ~3u", "ADD32(ctx->r4, 0X0)) & ~3u", 1)
    off = ("    // 0x8001A0A0: sw          $s6, 0x1A0($sp)\n"
           "    if (x) rs64_m5_writer_parity('W', 0x8001A0A0u, U32(ADD32(ctx->r29, 0X1A4)), 0u);\n"
           "    { MEM_W(0X1A0, ctx->r29) = ctx->r22; RS64_S5798_ST(0x8001A0A0u, 0X1A0, ctx->r29, 4); }\n")
    def tot(t):
        r, _ = scan(t); r.pop("_stores", None); return tuple(sum(v[i] for v in r.values()) for i in range(3))
    g, v, o = tot(good), tot(val), tot(off)
    okc = g == (2, 0, 0) and v == (1, 1, 0) and o == (1, 1, 0)
    print("controls: good=%s value_reg=%s offset_mut=%s %s" % (g, v, o, "PASS" if okc else "FAIL"))
    return okc


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--controls" in sys.argv and not controls():
        return 3
    d = pathlib.Path(args[0] if args else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    tot = collections.defaultdict(lambda: [0, 0, 0]); bads = []
    for p in sorted(d.glob("funcs_*.c")):
        r, b = scan(p.read_text(errors="replace"))
        for k, v in r.items():
            for i in range(3):
                tot[k][i] += v[i]
        bads += ["%s: %s" % (p.name, x) for x in b]
    sw = tot.pop("_stores", [0, 0, 0])
    nh = sum(sum(v) for v in tot.values()); nb = sum(v[1] for v in tot.values()); kn = sum(tot[k][2] for k in KNOWN if k in tot)
    KNOWN.update("abs:" + k for k in list(KNOWN))
    print("stores=%d unwatched=%d (no writer_parity/s5660 hook: STORE_WATCH blind)" % (sw[0], sw[1]))
    for u in UNW:
        print("UNWATCHED", u)
    for k in sorted(tot):
        print("family %-30s ok=%d bad=%d nostore=%d%s" % (k, tot[k][0], tot[k][1], tot[k][2], "" if k in KNOWN else " (unmodelled)"))
    print("hooks=%d bad=%d known_nostore=%d" % (nh, nb, kn))
    for s in bads[:12]:
        print("BAD", s)
    return 0 if nh > 0 and nb == 0 and kn == 0 and sw[1] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
