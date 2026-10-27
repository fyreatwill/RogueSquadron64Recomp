"""s6518: uncapped one-line [ret-sum] per keyed streamTerrainGridCellsByDistance return
(key, EMPTY/ok, table d4, nclear/nskip/npass). The [span-filter] dump sits behind 100-EMPTY/8-ok caps."""
from pathlib import Path
P = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
T = P.read_text()
MARK = "PATCH: s6518 ret-sum"
if MARK in T:
    print("s6518 already applied"); raise SystemExit(0)
old = '    if (getenv("ROGUESQ_FORFACE_LOG")) { static int ne6493 = 0, nn6493 = 0; int emp = (ctx->r2 == 0);'
assert T.count(old) == 1
new = ('    if (s6505_key && getenv("ROGUESQ_FORFACE_LOG")) fprintf(stderr, "[ret-sum] key=%u %s d4=%08X nclear=%u nskip=%u npass=%u\\n", s6505_key, ctx->r2 == 0 ? "EMPTY" : "ok", '
       '(uint32_t)MEM_W(0, (int64_t)(int32_t)0x80136DC4u), s6513_nclear, s6513_nskip, s6513_npass); /* ' + MARK + ' */\n') + old
T = T.replace(old, new)
P.write_text(T); print("s6518 applied")
