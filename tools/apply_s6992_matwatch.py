"""s6992: write-watch on the material-node pool (createMaterialPool 0x80021F38: rs_malloc(0x3000) = 512 nodes x 0x18,
base published at 0x80128EF4; free-list head 0x80128EF8; node +0 next, +4 prev).

Why: s6991 L15 (level 15, dd4 21:9 FPS60) SIGBUS at guest 0x800223DC (allocOrEvictMaterialNode `sw $zero,4($v0)`):
the free-list head node's +0 next pointer read 0xC5E753DF (a float, about -7402.5), so something outside the material
code wrote into a free node. This names that writer.

Mechanism: the s5798 per-store hook (generated sw/sh/sb/swc1/sd/sdc1). The macro range gains the pool range
[g_rs64_s6992_lo, +0x3000) and the publish word 0x80128EF4; the handler re-reads the base on every publish store.
Env ROGUESQ_MATWATCH=1 (also turns g_rs64_store_diag on: name contains WATCH).
Log: [matw] base=... on every publish; [matw-own] first 6 stores from the material functions 0x80021DF4..0x80022A00
(POSITIVE CONTROL: buildMaterialFreeList links all 512 nodes, so it must fire at every publish); [matw-for] every
foreign store (pc outside that range), first 4 per distinct pc plus every 256th, with node index, offset, value, fn, tid.
Blind to host writers (memcpy/DMA/C patches): a corrupted node with no [matw-for] line means a non-store writer.
Idempotent; mirrored in fixup_game_funcs_vendored.py's apply list."""
from pathlib import Path
import re
D = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s6992 matwatch"
n = 0
for p in sorted(D.glob("funcs_*.c")):
    t = p.read_text()
    if "#define RS64_S5798_ST" not in t or MARK in t:
        continue
    new, k = re.subn(r"(_a5798 = \(uint32_t\)\(\(base\) \+ \(off\)\); if \()",
                     r"\1(uint32_t)(_a5798 - g_rs64_s6992_lo) < 0x3000u || _a5798 == 0x80128EF4u || ", t, count=1)
    if k:
        new = new.replace("#define RS64_S5798_ST", "/* " + MARK + " */\nextern uint32_t g_rs64_s6992_lo;\n#define RS64_S5798_ST", 1)
        p.write_text(new); n += 1
print("macro patched in", n, "files")
P = D / "funcs_13.c"
T = P.read_text()
helper = r'''/* PATCH: s6992 matwatch helper */
#include <pthread.h>
extern uint32_t rs64_phase_ord(void);
uint32_t g_rs64_s6992_lo = 0x7FFF0000u;
static int s6992_en(void) { static int en = -1; if (en < 0) { const char* e = getenv("ROGUESQ_MATWATCH"); en = (e && e[0] && e[0] != '0') ? 1 : 0; } return en; }
static void s6992_note(uint8_t* rdram, recomp_context* ctx, uint32_t pc, uint32_t a, int w, const char* fn) {
    static unsigned own = 0, forn = 0, npc = 0; static uint32_t pcs[256]; static unsigned cnt[256];
    if (!s6992_en()) return;
    uint64_t tid = 0; pthread_threadid_np(NULL, &tid);
    uint32_t off = a - g_rs64_s6992_lo, val = (uint32_t)MEM_W(0, (gpr)(int32_t)(a & ~3u));
    if (a == 0x80128EF4u) {
        g_rs64_s6992_lo = val ? val : 0x7FFF0000u; own = 0;
        fprintf(stderr, "[matw] base=%08X pc=%08X fn=%s tid=%llu phase=%u foreign_so_far=%u\n", val, pc, fn, (unsigned long long)tid, rs64_phase_ord(), forn);
        return;
    }
    if (pc >= 0x80021DF4u && pc < 0x80022A00u) {
        if (++own <= 6) fprintf(stderr, "[matw-own] n=%u pc=%08X fn=%s node=%u off=%02X val=%08X\n", own, pc, fn, off / 0x18, off %% 0x18, val);
        return;
    }
    forn++;
    unsigned k = 0; while (k < npc && pcs[k] != pc) k++;
    if (k == npc && npc < 256) { pcs[npc] = pc; cnt[npc] = 0; npc++; }
    unsigned c = k < 256 ? ++cnt[k] : 0;
    if (pc == 0x800496A8u && c <= 4) { /* s6992c: hudDisplayUpdateWorker TLUT copy: which id, is it inside the TLUT table? */
        uint32_t v = (uint32_t)MEM_W(0x14, ctx->r16), id = (uint32_t)MEM_HU(6, (gpr)(int32_t)v), did = (uint32_t)MEM_HU(4, (gpr)(int32_t)v);
        uint32_t tb = (uint32_t)MEM_W(0, (gpr)(int32_t)0x80128EFCu), tc = (uint32_t)MEM_HU(0, (gpr)(int32_t)0x80128F04u);
        uint32_t bk = (uint32_t)MEM_W(0, (gpr)(int32_t)0x80128F00u), nb = (uint32_t)MEM_HU(0, (gpr)(int32_t)0x80128EF0u), used = 0;
        for (uint32_t q = 0; q < tc && q < 4096; q++) used += MEM_W(0, (gpr)(int32_t)(tb + q * 4)) != 0;
        fprintf(stderr, "[matw-tlut] desc=%08X data_id=%u tlut_id=%u tlut_tab=%08X tlut_cnt=%u used=%u entry_addr=%08X entry=%08X buckets=%08X nb=%u dst=%08X\n",
                v, did, id, tb, tc, used, tb + id * 4, (uint32_t)MEM_W(0, (gpr)(int32_t)(tb + id * 4)), bk, nb, (uint32_t)ctx->r18);
        { uint32_t lt = (uint32_t)MEM_W(0, (gpr)(int32_t)0x8011A444u), e0 = (uint32_t)MEM_HU(0, (gpr)(int32_t)(lt + did * 4)), e2 = (uint32_t)MEM_HU(2, (gpr)(int32_t)(lt + did * 4));
          uint32_t rs = (uint32_t)MEM_W(0, (gpr)(int32_t)0x80128F08u), ra = rs + e2 * 0x24; char b[200]; int o = 0;
          for (int q = 0; q < 9; q++) o += snprintf(b + o, sizeof b - o, " %08X", (uint32_t)MEM_W(0, (gpr)(int32_t)(ra + q * 4)));
          fprintf(stderr, "[matw-rec] lut=%08X e0=%04X e2=%u recs=%08X rec=%08X words:%s\n", lt, e0, e2, rs, ra, b); }
    }
    if (c <= 4 || (c & 255) == 0)
        fprintf(stderr, "[matw-for] n=%u pc=%08X fn=%s pc_n=%u ra=%08X addr=%08X node=%u off=%02X w=%d val=%08X head=%08X tid=%llu phase=%u\n",
                forn, pc, fn, c, (uint32_t)ctx->r31, a, off / 0x18, off %% 0x18, w, val, (uint32_t)MEM_W(0, (gpr)(int32_t)0x80128EF8u),
                (unsigned long long)tid, rs64_phase_ord());
}
'''.replace("%%", "%")
anchor = "void rs64_s5798_st(uint8_t* rdram, recomp_context* ctx, uint32_t pc, uint32_t a, int w, const char* fn) {\n"
assert T.count(anchor) == 1
if "s6992_note" in T:
    print("handler already present")
else:
    T = T.replace(anchor, helper + anchor + "    if (a == 0x80128EF4u || (uint32_t)(a - g_rs64_s6992_lo) < 0x3000u) { s6992_note(rdram, ctx, pc, a, w, fn); return; } /* " + MARK + " */\n", 1)
    P.write_text(T); print("handler added")

# ---- s6992b: texture-arena bounds watch (same hook). Arena = [*0x8011A850, *0x8011A854) set by
# buildAndRegisterDefaultMaterial (0x80017CF8/0x80017D00); texture data bumps UP from *0x8011A7D8 (lo), TLUTs bump DOWN
# from *0x8011A7D0 (hi) in texPackTlutSlotOrAlloc / getTextureAttrBySlot / allocTextureTlutBlock / loadTextureToMemory,
# with no visible lower-bound test. Logs [texar] on every store to those words: first 24, every 128th, and the first 24
# where hi < base, hi < lo, or lo > end (the overrun). Positive control: the 0x80017CF8 base publish must log.
MARK2 = "PATCH: s6992b texarena"
n = 0
for p in sorted(D.glob("funcs_*.c")):
    t = p.read_text()
    if "#define RS64_S5798_ST" not in t or MARK2 in t:
        continue
    new, k = re.subn(r"(_a5798 = \(uint32_t\)\(\(base\) \+ \(off\)\); if \()",
                     r"\1(uint32_t)(_a5798 - 0x8011A7D0u) < 0xCu || (uint32_t)(_a5798 - 0x8011A850u) < 8u || ", t, count=1)
    if k:
        new = new.replace("#define RS64_S5798_ST", "/* " + MARK2 + " */\n#define RS64_S5798_ST", 1)
        p.write_text(new); n += 1
print("s6992b macro patched in", n, "files")
T = P.read_text()
if "s6992b_note" not in T:
    helper2 = r'''/* PATCH: s6992b texarena helper */
static void s6992b_note(uint8_t* rdram, recomp_context* ctx, uint32_t pc, uint32_t a, const char* fn) {
    static unsigned n = 0, bad = 0;
    if (!s6992_en()) return;
    n++;
    uint32_t base = (uint32_t)MEM_W(0, (gpr)(int32_t)0x8011A850u), end = (uint32_t)MEM_W(0, (gpr)(int32_t)0x8011A854u);
    uint32_t hi = (uint32_t)MEM_W(0, (gpr)(int32_t)0x8011A7D0u), lo = (uint32_t)MEM_W(0, (gpr)(int32_t)0x8011A7D8u);
    int over = (a == 0x8011A7D0u || a == 0x8011A7D8u) && base && (hi < base || hi < lo || lo > end);
    if (n <= 24 || (n & 127) == 0 || (over && ++bad <= 24))
        fprintf(stderr, "[texar] n=%u pc=%08X fn=%s addr=%08X base=%08X end=%08X lo=%08X hi=%08X free=%d over=%d pool=%08X phase=%u\n",
                n, pc, fn, a, base, end, lo, hi, (int)(hi - lo), over, g_rs64_s6992_lo, rs64_phase_ord());
}
'''
    T = T.replace(anchor, helper2 + anchor + "    if ((uint32_t)(a - 0x8011A7D0u) < 0xCu || (uint32_t)(a - 0x8011A850u) < 8u) { s6992b_note(rdram, ctx, pc, a, fn); return; } /* " + MARK2 + " */\n", 1)
    P.write_text(T); print("s6992b handler added")

# ---- s6992d: fixed-address watch on the L15 21:9 dd4 bad HUD texture descriptor 0x80B1CB4C (+0x00..+0x30), deterministic
# across s6992 runs W15/X15/Y15 (tlut_id at +6 read 4184 vs tlut_cnt 2000). Logs [descw2] for every store (first 300).
MARK3 = "PATCH: s6992d descw2"
n = 0
for p in sorted(D.glob("funcs_*.c")):
    t = p.read_text()
    if "#define RS64_S5798_ST" not in t or MARK3 in t:
        continue
    new, k = re.subn(r"(_a5798 = \(uint32_t\)\(\(base\) \+ \(off\)\); if \()", r"\1(uint32_t)(_a5798 - 0x80B1CB40u) < 0x40u || ", t, count=1)
    if k:
        new = new.replace("#define RS64_S5798_ST", "/* " + MARK3 + " */\n#define RS64_S5798_ST", 1)
        p.write_text(new); n += 1
print("s6992d macro patched in", n, "files")
T = P.read_text()
if "s6992d_note" not in T:
    helper3 = r'''/* PATCH: s6992d descw2 helper */
static void s6992d_note(uint8_t* rdram, recomp_context* ctx, uint32_t pc, uint32_t a, int w, const char* fn) {
    static unsigned n = 0;
    if (!s6992_en() || ++n > 300) return;
    uint64_t tid = 0; pthread_threadid_np(NULL, &tid);
    fprintf(stderr, "[descw2] n=%u pc=%08X fn=%s addr=%08X off=%02X w=%d word=%08X hw6=%u tid=%llu phase=%u\n", n, pc, fn, a, a - 0x80B1CB4Cu, w,
            (uint32_t)MEM_W(0, (gpr)(int32_t)(a & ~3u)), (uint32_t)MEM_HU(0, (gpr)(int32_t)0x80B1CB52u), (unsigned long long)tid, rs64_phase_ord());
}
'''
    T = T.replace(anchor, helper3 + anchor + "    if ((uint32_t)(a - 0x80B1CB40u) < 0x40u) { s6992d_note(rdram, ctx, pc, a, w, fn); return; } /* " + MARK3 + " */\n", 1)
    P.write_text(T); print("s6992d handler added")

# ---- s6992e: pc-keyed hook on the terrain-texture worker's TLUT copy store (0x800496A8, constant-folded per site), so the
# tlut id / destination is logged whatever memory it lands in (retail-settings control arm, where it misses the pool).
MARK4 = "PATCH: s6992e tlutw"
n = 0
for p in sorted(D.glob("funcs_*.c")):
    t = p.read_text()
    if "#define RS64_S5798_ST" not in t or MARK4 in t:
        continue
    new, k = re.subn(r"(_a5798 = \(uint32_t\)\(\(base\) \+ \(off\)\); if \()", r"\1(pc) == 0x800496A8u || ", t, count=1)
    if k:
        new = new.replace("#define RS64_S5798_ST", "/* " + MARK4 + " */\n#define RS64_S5798_ST", 1)
        p.write_text(new); n += 1
print("s6992e macro patched in", n, "files")
T = P.read_text()
if "s6992e_note" not in T:
    helper4 = r'''/* PATCH: s6992e tlutw helper */
static void s6992e_note(uint8_t* rdram, recomp_context* ctx, uint32_t a) {
    static unsigned n = 0, bad = 0;
    if (!s6992_en()) return;
    if ((a & 0x1Fu) != 0) return; /* first word of each 8-word copy only */
    n++;
    uint32_t v = (uint32_t)MEM_W(0x14, ctx->r16), id = (uint32_t)MEM_HU(6, (gpr)(int32_t)v), did = (uint32_t)MEM_HU(4, (gpr)(int32_t)v);
    uint32_t tb = (uint32_t)MEM_W(0, (gpr)(int32_t)0x80128EFCu), tc = (uint32_t)MEM_HU(0, (gpr)(int32_t)0x80128F04u);
    int oob = id >= tc;
    if (n <= 8 || (oob && ++bad <= 12) || (n & 1023) == 0)
        fprintf(stderr, "[tlutw] n=%u desc=%08X data_id=%u tlut_id=%u tlut_cnt=%u oob=%d dst=%08X tab=%08X pool=%08X phase=%u\n",
                n, v, did, id, tc, oob, a, tb, g_rs64_s6992_lo, rs64_phase_ord());
}
'''
    T = T.replace(anchor, helper4 + anchor + "    if (pc == 0x800496A8u) { s6992e_note(rdram, ctx, a); if ((uint32_t)(a - g_rs64_s6992_lo) >= 0x3000u) return; } /* " + MARK4 + " */\n", 1)
    P.write_text(T); print("s6992e handler added")
