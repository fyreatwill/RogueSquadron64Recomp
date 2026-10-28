"""s6591: write-watch on the terrain descriptor head 0x80136DC0..+0x40 via the s5798 per-store hook (same mechanism as s6521).
s6590 showed lvl7 dd4: load_level_hmp publishes desc+0/+4 (log line 145819) yet streamTerrainGridCellsByDistance later sees both NULL
(w8/wC intact). Env ROGUESQ_DESCWATCH=1 logs every generated store into the range: pc, enclosing fn, guest ra, stored value, thread,
phase, VI-ish seq. Positive control: the 0x80043E64 publish store must appear with the same value as [desc-st]. Does not see host
memset/DMA writers: a missing writer for a NULL desc means a non-store writer. Idempotent."""
from pathlib import Path
import re
D = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s6591 descwatch"
n = 0
for p in sorted(D.glob("funcs_*.c")):
    t = p.read_text()
    if "RS64_S5798_ST" not in t or MARK in t:
        continue
    new, k = re.subn(r"(_a5798 = \(uint32_t\)\(\(base\) \+ \(off\)\); if \()", r"\1(uint32_t)(_a5798 - 0x80136DC0u) < 0x40u || ", t, count=1)
    if k:
        new = new.replace("#define RS64_S5798_ST", "/* " + MARK + " */\n#define RS64_S5798_ST", 1)
        p.write_text(new); n += 1
print("macro patched in", n, "files")
P = D / "funcs_13.c"
T = P.read_text()
if "s6591_note" in T:
    print("handler already present"); raise SystemExit(0)
helper = r'''/* PATCH: s6591 descwatch helper */
#include <pthread.h>
extern uint32_t rs64_phase_ord(void);
static void s6591_note(uint8_t* rdram, recomp_context* ctx, uint32_t pc, uint32_t a, int w, const char* fn) {
    static int en = -1; static unsigned n = 0;
    if (en < 0) { const char* e = getenv("ROGUESQ_DESCWATCH"); en = (e && e[0] && e[0] != '0') ? 1 : 0; }
    if (!en || n >= 400) return;
    n++;
    uint64_t tid = 0; pthread_threadid_np(NULL, &tid);
    fprintf(stderr, "[descw] n=%u pc=%08X fn=%s ra=%08X addr=%08X w=%d val=%08X tid=%llu phase=%u\n", n, pc, fn, (uint32_t)ctx->r31, a, w,
            (uint32_t)MEM_W(0, (gpr)(int32_t)(a & ~3u)), (unsigned long long)tid, rs64_phase_ord());
}
'''
anchor = "void rs64_s5798_st(uint8_t* rdram, recomp_context* ctx, uint32_t pc, uint32_t a, int w, const char* fn) {\n"
assert T.count(anchor) == 1
T = T.replace(anchor, helper + anchor + "    if ((uint32_t)(a - 0x80136DC0u) < 0x40u) { s6591_note(rdram, ctx, pc, a, w, fn); return; } /* PATCH: s6591 descwatch */\n", 1)
P.write_text(T); print("handler added")
