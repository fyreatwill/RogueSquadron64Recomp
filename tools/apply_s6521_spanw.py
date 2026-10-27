"""s6521: span-grid (0x80130DB0..+0x2000) writer census via the s5798 per-store hook.
Adds the range to every funcs_*.c RS64_S5798_ST macro and an early branch in rs64_s5798_st (funcs_13.c).
Env ROGUESQ_SPANW=1: per-PC counts split by grid column (<32 / >=32) and by stored value 0x80, an ever-written
bitmap, and the current count of 0x80 bytes per column half, dumped every 32768 grid stores. Observation only."""
from pathlib import Path
import re
D = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s6521 spanw"
n = 0
for p in sorted(D.glob("funcs_*.c")):
    t = p.read_text()
    if "RS64_S5798_ST" not in t or MARK in t:
        continue
    new, k = re.subn(r"(_a5798 = \(uint32_t\)\(\(base\) \+ \(off\)\); if \()", r"\1(uint32_t)(_a5798 - 0x80130DB0u) < 0x2000u || ", t, count=1)
    if k:
        new = new.replace("#define RS64_S5798_ST", "/* " + MARK + " */\n#define RS64_S5798_ST", 1)
        p.write_text(new); n += 1
print("macro patched in", n, "files")
P = D / "funcs_13.c"
T = P.read_text()
if "s6521_note" in T:
    print("handler already present"); raise SystemExit(0)
helper = r'''/* PATCH: s6521 spanw helper */
static struct { uint32_t pc, n, nx32, n80, n80x32, ra; } s6521_t[96]; static int s6521_np;
static uint8_t s6521_wr[0x2000]; static uint32_t s6521_total, s6521_dumps;
static void s6521_note(uint8_t* rdram, recomp_context* ctx, uint32_t pc, uint32_t a, int w) {
    static int e = -1;
    if (e < 0) { const char* s = getenv("ROGUESQ_SPANW"); e = (s && s[0]) ? 1 : 0; }
    if (!e) return;
    uint32_t off = a - 0x80130DB0u, col = off & 63u; int x32 = col >= 32;
    uint32_t v = (uint32_t)(uint8_t)MEM_B(0, (gpr)(int32_t)a);
    int i; for (i = 0; i < s6521_np; i++) if (s6521_t[i].pc == pc) break;
    if (i == s6521_np) { if (i >= 96) return; s6521_np++; s6521_t[i].pc = pc; s6521_t[i].ra = (uint32_t)ctx->r31;
        fprintf(stderr, "[spanw] first pc=%08x ra=%08x a=%08x col=%u w=%d v=%02x\n", pc, (uint32_t)ctx->r31, a, col, w, v); }
    s6521_t[i].n++; s6521_t[i].nx32 += x32;
    if (w == 1 && v == 0x80) { s6521_t[i].n80++; s6521_t[i].n80x32 += x32; }
    for (int b = 0; b < w && off + b < 0x2000u; b++) s6521_wr[off + b] = 1;
    if ((++s6521_total & 0x7FFFu) == 0 && s6521_dumps < 400) {
        s6521_dumps++;
        uint32_t cur80[2] = {0, 0}, wr[2] = {0, 0};
        for (uint32_t k = 0; k < 0x2000u; k++) { int h = (k & 63u) >= 32; wr[h] += s6521_wr[k];
            if ((uint8_t)MEM_B(0, (gpr)(int32_t)(0x80130DB0u + k)) == 0x80) cur80[h]++; }
        fprintf(stderr, "[spanw] dump=%u total=%u grid80_lo=%u grid80_hi=%u everwritten_lo=%u everwritten_hi=%u\n", s6521_dumps, s6521_total, cur80[0], cur80[1], wr[0], wr[1]);
        for (int j = 0; j < s6521_np; j++) fprintf(stderr, "[spanw]   pc=%08x n=%u nx32=%u n80=%u n80x32=%u\n", s6521_t[j].pc, s6521_t[j].n, s6521_t[j].nx32, s6521_t[j].n80, s6521_t[j].n80x32);
    }
}
'''
anchor = "void rs64_s5798_st(uint8_t* rdram, recomp_context* ctx, uint32_t pc, uint32_t a, int w, const char* fn) {\n"
assert T.count(anchor) == 1
T = T.replace(anchor, helper + anchor + "    if ((uint32_t)(a - 0x80130DB0u) < 0x2000u) { s6521_note(rdram, ctx, pc, a, w); return; } /* PATCH: s6521 spanw */\n", 1)
P.write_text(T); print("handler added")
