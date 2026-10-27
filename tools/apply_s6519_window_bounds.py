"""s6519: extend [ret-sum] with the request window (0x80132DB0 x0, +4 w, +8 y0, +C h) and the table dims
(0x80136DC0+0x38 W, +0x3A H) so EMPTY calls bucket in-bounds vs out-of-bounds offline. Observation only."""
from pathlib import Path
P = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
T = P.read_text()
MARK = "PATCH: s6519 window bounds"
if MARK in T:
    print("s6519 already applied"); raise SystemExit(0)
old = 'npass=%u\\n", s6505_key, ctx->r2 == 0 ? "EMPTY" : "ok", '
assert T.count(old) == 1
new = ('npass=%u win=%d,%d,%d,%d tbl=%u,%u /* ' + MARK + ' */\\n", s6505_key, ctx->r2 == 0 ? "EMPTY" : "ok", ')
T = T.replace(old, new)
old2 = 's6513_nclear, s6513_nskip, s6513_npass); /* PATCH: s6518 ret-sum */'
assert T.count(old2) == 1
new2 = ('s6513_nclear, s6513_nskip, s6513_npass, (int)MEM_W(0, (int64_t)(int32_t)0x80132DB0u), (int)MEM_W(0, (int64_t)(int32_t)0x80132DB4u), '
        '(int)MEM_W(0, (int64_t)(int32_t)0x80132DB8u), (int)MEM_W(0, (int64_t)(int32_t)0x80132DBCu), '
        '(unsigned)MEM_HU(0, (int64_t)(int32_t)0x80136DF8u), (unsigned)MEM_HU(0, (int64_t)(int32_t)0x80136DFAu)); /* PATCH: s6518 ret-sum */')
T = T.replace(old2, new2)
P.write_text(T); print("s6519 applied")
