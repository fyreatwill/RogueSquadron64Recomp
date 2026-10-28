"""s6588: log (and optionally skip) streamTerrainGridCellsByDistance cells whose 30-byte record table
pointer (*(t0+4), used at 0x80042D7C) is NULL. s6587 crash: lb 0x3/0x4($v1) with v1=NULL+idx*30 -> far 0x22/0x5e
(idx 1/3). ROGUESQ_TBLNULL_LOG=1 logs t0, tbl, cell addr (s2), cell halfword, idx, a0/a1; ROGUESQ_TBLNULL_SKIP=1
also skips the cell (goto L_80043020). Unset = bit-identical."""
from pathlib import Path
P = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
T = P.read_text()
if "s6588 tblnull" in T:
    print("already"); raise SystemExit(0)
a = "    // 0x80042D84: addu        $v1, $v1, $v0\n    ctx->r3 = ADD32(ctx->r3, ctx->r2);\n"
assert T.count(a) == 1, T.count(a)
patch = r'''    if (MEM_W(0X4, ctx->r8) == 0 && ctx->r3 == ctx->r2 + 0 ) {} /* PATCH: s6588 tblnull (placeholder-free) */
'''
patch = r'''    { /* PATCH: s6588 tblnull */
      static int e = -1, n = 0; if (e < 0) { e = getenv("ROGUESQ_TBLNULL_SKIP") ? 2 : (getenv("ROGUESQ_TBLNULL_LOG") ? 1 : 0); }
      if (e && ((uint32_t)MEM_W(0X4, ctx->r8) & 0x7FFFFFFFu) == 0) {
        if (n++ < 40) fprintf(stderr, "[tblnull] n=%d t0=%08X tbl=%08X cellp=%08X cellh=%04X off=%u a0=%d a1=%08X s6=%08X\n", n, (uint32_t)ctx->r8, (uint32_t)MEM_W(0X4, ctx->r8), (uint32_t)ctx->r18, (unsigned)MEM_HU(0, ctx->r18), (unsigned)ctx->r2, (int)(int8_t)ctx->r4, (uint32_t)ctx->r5, (uint32_t)ctx->r22);
        if (e == 2) goto L_80043020;
      }
    }
'''
T = T.replace(a, a + patch, 1)
P.write_text(T); print("ok")
