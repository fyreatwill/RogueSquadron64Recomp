"""s5817: who sets bit 3 (destroy request) of a slot's +0x14? Static census found exactly two generated setters:
 A) destroyNpcSlotByIndex (funcs_8.c, 0x8003EDB4; taken when slot +0x1A depth != 0), 10 call sites -> log per distinct caller ra
 B) processGridCellByDistance (funcs_10.c, 0x80048F74; gated by lhu 0x0(..)&0x4000)
Logs under ROGUESQ_LOG_HUDBIT: [b3dest] entry of A (ra, index, vi), [b3set] A flag-set, [b3grid] B set, [b3hist] per-ra histogram every 256 events.
Control: A-entry total vs A-flag-set total vs [slotpost] flag8. Idempotent; mirrored into fixup."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
H8 = r'''/* PATCH: s5817 helpers */
#include <execinfo.h>
#include <dlfcn.h>
extern volatile uint32_t rs64_vi_n_g;
static struct { uint32_t ra, n, nset, nimm; } rs5817_ra[32]; static unsigned rs5817_nra, rs5817_tot, rs5817_set, rs5817_grid;
static int rs5817_en(void) { static int e = -1; if (e < 0) { const char* v = getenv("ROGUESQ_LOG_HUDBIT"); e = (v && v[0]) ? 1 : 0; } return e; }
static int rs5817_k(uint32_t ra) { for (unsigned i = 0; i < rs5817_nra && i < 32; i++) if (rs5817_ra[i].ra == ra) return i; if (rs5817_nra >= 32) return 31; rs5817_ra[rs5817_nra].ra = ra; return rs5817_nra++; }
static char rs5817_nm[32][64];
static void rs5817_hist(void) { for (unsigned i = 0; i < rs5817_nra && i < 32; i++) fprintf(stderr, "[b3hist] caller=%s entries=%u flagset=%u\n", rs5817_nm[i], rs5817_ra[i].n, rs5817_ra[i].nset); fprintf(stderr, "[b3hist] total entries=%u flagset=%u grid=%u\n", rs5817_tot, rs5817_set, rs5817_grid); }
static uint32_t rs5817_cur;
static void rs5817_entry(uint32_t ra, uint32_t idx) { void* bt[6]; int nb = backtrace(bt, 6); Dl_info di; uint32_t key = 0; const char* nm = "?"; if (nb > 2 && dladdr(bt[2], &di) && di.dli_saddr) { key = (uint32_t)(uintptr_t)di.dli_saddr; nm = di.dli_sname ? di.dli_sname : "?"; } rs5817_cur = key;
    int k = rs5817_k(key); if (rs5817_ra[k].n == 0) { strncpy(rs5817_nm[k], nm, 63); } rs5817_ra[k].n++; rs5817_tot++; if (rs5817_ra[k].n <= 3) fprintf(stderr, "[b3dest] caller=%s idx=%u vi=%u\n", nm, idx & 0xFFFF, rs64_vi_n_g); if ((rs5817_tot & 1023) == 0) rs5817_hist(); }
static void rs5817_flagset(uint32_t ra0, uint32_t slot, uint32_t w0, uint32_t fl, uint32_t age) { uint32_t ra = rs5817_cur; int k = rs5817_k(ra); rs5817_ra[k].nset++; rs5817_set++; if (rs5817_ra[k].nset <= 3) fprintf(stderr, "[b3set] callerkey=%08X slot=%08X upd=%08X fl=%04X depth=%u vi=%u\n", ra, slot, w0, fl, age, rs64_vi_n_g); }
'''
HGRID = r'''/* PATCH: s5817 grid helper */
extern void rs5817_gridset(uint32_t slot, uint32_t ra, uint32_t fl);
'''
T = "PATCH: s5817"
def apply8(text):
    n = 0
    if "RECOMP_FUNC void destroyNpcSlotByIndex(" not in text: return text, 0
    if "PATCH: s5817 helpers" not in text:
        i = text.find("RECOMP_FUNC void destroyNpcSlotByIndex("); text = text[:i] + H8 + text[i:]; n += 1
    A1 = "    // 0x8003ED74: addiu       $sp, $sp, -0x20\n"
    if "PATCH: s5817 entry" not in text:
        assert text.count(A1) == 1
        text = text.replace(A1, '    { /* PATCH: s5817 entry */ if (rs5817_en()) rs5817_entry(U32(ctx->r31), U32(ctx->r4)); }\n' + A1); n += 1
    A2 = "    // 0x8003EDB4: ori         $v0, $v0, 0x8\n"
    if "PATCH: s5817 flagset" not in text:
        assert text.count(A2) == 1
        text = text.replace(A2, '    { /* PATCH: s5817 flagset */ if (rs5817_en()) rs5817_flagset(U32(ctx->r31), U32(ctx->r16), U32(MEM_W(0X0, ctx->r16)), (uint32_t)MEM_HU(ctx->r16, 0X14), (uint32_t)MEM_BU(ctx->r16, 0X1A)); }\n' + A2); n += 1
    return text, n
def apply10(text):
    n = 0
    if "RECOMP_FUNC void processGridCellByDistance(" not in text: return text, 0
    A3 = "    // 0x80048F74: ori         $v0, $v0, 0x8\n"
    if "PATCH: s5817 grid" not in text:
        assert text.count(A3) == 1
        i = text.find("RECOMP_FUNC void processGridCellByDistance(")
        text = text[:i] + "/* PATCH: s5817 grid helper */\nstatic unsigned rs5817_gn;\nstatic void rs5817_g(uint32_t slot, uint32_t ra, uint32_t w0, uint32_t fl) { static int e = -1; if (e < 0) { const char* v = getenv(\"ROGUESQ_LOG_HUDBIT\"); e = (v && v[0]) ? 1 : 0; } if (!e) return; extern volatile uint32_t rs64_vi_n_g; rs5817_gn++; if (rs5817_gn <= 6 || (rs5817_gn & 1023) == 0) fprintf(stderr, \"[b3grid] n=%u slot=%08X upd=%08X fl=%04X ra=%08X vi=%u\\n\", rs5817_gn, slot, w0, fl, ra, rs64_vi_n_g); }\n" + text[i:]
        text = text.replace(A3, '    { /* PATCH: s5817 grid */ rs5817_g(U32(ctx->r17), U32(ctx->r31), U32(MEM_W(0X0, ctx->r17)), (uint32_t)MEM_HU(ctx->r17, 0X14)); }\n' + A3); n += 1
    return text, n
def apply(text):
    t, n = apply8(text)
    if n == 0: t, n = apply10(text)
    return t, n
if __name__ == "__main__":
    for f, fn in (("funcs_8.c", apply8), ("funcs_10.c", apply10)):
        p = base / f; t = p.read_text(); t2, n = fn(t)
        if n: p.write_text(t2)
        print(f, "live patched x%d" % n)
