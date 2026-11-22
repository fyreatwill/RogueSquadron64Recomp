#!/usr/bin/env python3
"""s5660: the s5654 store census hooks rs64_m5_writer_parity, which is NOT emitted before the 421 unaligned
store sites (do_swl/do_swr/do_sdl/do_sdr) -- the only unhooked game store forms.  This adds the same
rs64_s5654_vstore call (width 'L'/'R'/'l'/'r', pc from the preceding disassembly comment) before each, so
a bulk fill via unaligned stores becomes visible.  Diagnostic only.  Idempotent.
ORIGIN: not a mitigation -- names the writer of the voice-read rail data (H1 of s5660).
Usage: apply_s5660_unaligned_store_census.py [RecompiledFuncs dir]
"""
import sys, re, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
pat = re.compile(r"^(\s*)do_(swl|swr|sdl|sdr)\(rdram, (\S+), (ctx->r\d+), (ctx->r\d+)\);[^\n]*\n", re.M)
pc_re = re.compile(r"// (0x[0-9A-Fa-f]{8}):")
W = {"swl": "L", "swr": "R", "sdl": "l", "sdr": "r"}
# s7784: repair pass for trees patched before the fix. The hook used to take its address from the STORED VALUE register
# (do_swl(rdram, off, base, val): group(5)) instead of the base register, so every unaligned-store census since s5660
# (s5654/s6843 store watch, s7779/s7781/s7783 FB-arena) saw value+offset, not the destination. Rewrites each existing hook so
# its register equals the base register of the do_s* call on the next line. Idempotent (a repaired hook is left alone).
rep = re.compile(r"(\{ uint32_t s5660_a = U32\(ADD32\()(ctx->r\d+)(, [^)]+\)\) & ~3u; rs64_s5660_ustore\([^\n]*PATCH: s5660 \*/\n)"
                 r"([^\n]*do_(?:swl|swr|sdl|sdr)\(rdram, [^,]+, (ctx->r\d+), (?:ctx->r\d+|0)\);)")
nrep = 0
for p in sorted(D.glob("funcs_*.c")):
    s = p.read_text()
    if "PATCH: s5660" not in s:
        continue
    k = [0]
    def fix(m):
        if m.group(2) == m.group(5):
            return m.group(0)
        k[0] += 1
        return m.group(1) + m.group(5) + m.group(3) + m.group(4)
    s2 = rep.sub(fix, s)
    if k[0]:
        p.write_text(s2); nrep += k[0]
print("s5660 base-register repair: %d hooks rewritten" % nrep)
# s7785: line-based and idempotent per SITE (was per file: a file already carrying "PATCH: s5660" never got new sites), and the
# stored value may be the literal 0 (swl $zero: the generator prints "0", not ctx->r0; 0x8002A098 was the one unhooked site, so
# the store watch was blind to it). The do_s* call may sit inside a later s7488 "{ RS64_S7488_UST(...); do_swl(...); }" line.
call = re.compile(r"do_(swl|swr|sdl|sdr)\(rdram, ([^,]+), (ctx->r\d+), (?:ctx->r\d+|0)\);")
n = 0
for p in sorted(D.glob("funcs_*.c")):
    s = p.read_text()
    if "do_s" not in s:
        continue
    lines = s.split("\n"); out = []; cnt = 0; pc = "0x0"
    for i, ln in enumerate(lines):
        m = pc_re.search(ln)
        if m and ln.lstrip().startswith("//"):
            pc = m.group(1)
        c = call.search(ln)
        if c and not (out and "PATCH: s5660" in out[-1]):
            ind = ln[:len(ln) - len(ln.lstrip())]
            out.append("%s{ uint32_t s5660_a = U32(ADD32(%s, %s)) & ~3u; rs64_s5660_ustore(%su, s5660_a, 0u, '%s'); } /* PATCH: s5660 */"
                       % (ind, c.group(3), c.group(2), pc, W[c.group(1)]))  # s7784: base reg (was the stored value)
            cnt += 1
        out.append(ln)
    if not cnt:
        continue
    s = "\n".join(out)
    if "extern void rs64_s5660_ustore(" not in s:
        s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\nextern void rs64_s5660_ustore(uint32_t, uint32_t, uint32_t, char);\n', 1)
    p.write_text(s); n += cnt
print("s5660 unaligned store census: %d sites" % n)
