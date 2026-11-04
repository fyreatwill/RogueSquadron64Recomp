#!/usr/bin/env python3
"""s6880 G1d: the span-table store bound (s6049) also covers wide frames at dd 1.
s6879 widened the footprint at dd 1 and copied the s6037 64x64 window clamp, but not this bound, which s6049 gated on ROGUESQ_DRAW_DISTANCE != 1.
21:9 lvl1 then crashed 5/5 in streamTerrainGridCellsByDistance at 0x80042D6C on a wild cell pointer (s2 = 0xFE7E017F, odd, so the map base itself).
A wide frame (rs64_s6879_fpk != 1) now skips any store outside the two tables, as dd != 1 does. k = 1 stays retail. ROGUESQ_G1D_SPANBOUND=0 = old.
Runs last in RS64_REPLAY: apply_s6493_stream_cum anchors on the s6049 text. Idempotent.  Usage: apply_s6880_widebound.py [RecompiledFuncs dir]
"""
import re, sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
HEAD = "{ /* PATCH: s6049 tablebound */ static int on6049 = -1; static unsigned n6049;\n"
NEWHEAD = "{ /* PATCH: s6049 tablebound */ /* PATCH: s6880 widebound */ extern int rs64_s6880_wide(void); static int on6049 = -1; static unsigned n6049;\n"
GATE = re.compile(r'if \(on6049 && \(uint32_t\)\(U32\(ctx->(r\d+)\) - 0x80130DB0u\) >= 0x2000u\) \{ ((?:g_s6493\[\d\]\+\+; )?)if \(n6049\+\+ < 8\) (fprintf\(stderr, "\[spanbound\] skip addr=0x%08X pc=0x([0-9A-F]{8})\\n", \(unsigned\)U32\(ctx->r\d+\)\);) \}')
LOG = (r'if ((on6049 || rs64_s6880_wide()) && (uint32_t)(U32(ctx->\1) - 0x80130DB0u) >= 0x2000u) { \2if (n6049++ < 8 || !(n6049 & 0xFFFFu)) { \3 '
       r'const int64_t h6880 = (int64_t)(int32_t)0x80132000; fprintf(stderr, "[spanbound6880] pc=0x\4 n=%u win=%d,%d,%d,%d r4=%d r5=%d r6=%d\n", n6049, (int32_t)MEM_W(0xDB0, h6880), (int32_t)MEM_W(0xDB4, h6880), (int32_t)MEM_W(0xDB8, h6880), (int32_t)MEM_W(0xDBC, h6880), (int32_t)ctx->r4, (int32_t)ctx->r5, (int32_t)ctx->r6); } }')
def apply9(text):
    if "PATCH: s6880 widebound" in text: return text, 0
    n = text.count(HEAD)
    text, m = GATE.subn(LOG, text)
    assert n > 0 and m == n, "s6880 anchors %d %d" % (n, m)
    return text.replace(HEAD, NEWHEAD), m

if __name__ == "__main__":
    p = D / "funcs_9.c"; t = p.read_text(); t2, n = apply9(t)
    if n: p.write_text(t2)
    print("funcs_9.c s6880 widebound x%d" % n)
