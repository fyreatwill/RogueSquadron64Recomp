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
                 r"([^\n]*do_(?:swl|swr|sdl|sdr)\(rdram, [^,]+, (ctx->r\d+), ctx->r\d+\);)")
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
n = 0
for p in sorted(D.glob("funcs_*.c")):
    s = p.read_text()
    if "PATCH: s5660" in s or "do_s" not in s:
        continue
    out, last, cnt = [], 0, 0
    for m in pat.finditer(s):
        pcs = pc_re.findall(s[max(0, m.start() - 160):m.start()])
        pc = pcs[-1] if pcs else "0x0"
        hook = ("%s{ uint32_t s5660_a = U32(ADD32(%s, %s)) & ~3u; rs64_s5660_ustore(%su, s5660_a, 0u, '%s'); } /* PATCH: s5660 */\n"
                % (m.group(1), m.group(4), m.group(3), pc, W[m.group(2)]))  # s7784: group(4) = base reg (was group(5) = stored value)
        out.append(s[last:m.start()]); out.append(hook); out.append(m.group(0)); last = m.end(); cnt += 1
    if not cnt:
        continue
    out.append(s[last:])
    s = "".join(out).replace('#include "funcs.h"\n', '#include "funcs.h"\nextern void rs64_s5660_ustore(uint32_t, uint32_t, uint32_t, char);\n', 1)
    p.write_text(s); n += cnt
print("s5660 unaligned store census: %d sites" % n)
