#!/usr/bin/env python3
"""s4537: at musyxInitVoiceFromSample's 0x800921E8 store, count every
store and every store whose voice is 0x801724C0.

Prints one arm line on the first store (any voice), each target-voice
store up to 16, and n_all/n_this on the bad 0x800903F0 jal for that
voice. An alias whose physical address is 0x1724C0 but whose pointer
is not 0x801724C0 is counted separately as n_phys and does not increment
n_this. ROGUESQ_LOG_S4537=1. Diagnostic only. Does not skip the store.
Idempotent.
"""
from pathlib import Path

p = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
s = p.read_text()
if "rs64_s4537_init_store" in s:
    print("already applied")
    raise SystemExit(0)

helper = r'''
/* PATCH: s4537 init-voice store census. Diagnostic only. Does not skip the store. */
static unsigned rs64_s4537_n_all = 0;
static unsigned rs64_s4537_n_this = 0;
static unsigned rs64_s4537_n_phys = 0;
static uint32_t rs64_s4537_last_this = 0;
static uint32_t rs64_s4537_last_phys = 0;
static int rs64_s4537_on = -1;
static int rs64_s4537_exact_rows = 0;
static int rs64_s4537_phys_rows = 0;
static int rs64_s4537_jal_rows = 0;

static int rs64_s4537_enabled(void) {
    if (rs64_s4537_on < 0) {
        const char* e = getenv("ROGUESQ_LOG_S4537");
        rs64_s4537_on = (e && e[0] && e[0] != '0') ? 1 : 0;
    }
    return rs64_s4537_on;
}

static void rs64_s4537_init_store(gpr voice, gpr stored) {
    if (!rs64_s4537_enabled()) return;
    uint32_t v = (uint32_t)voice;
    uint32_t d = (uint32_t)stored;
    int exact = (v == 0x801724C0u);
    int phys = ((v & 0x1fffffffu) == 0x01724C0u);
    rs64_s4537_n_all++;
    if (exact) {
        rs64_s4537_n_this++;
        rs64_s4537_last_this = d;
    } else if (phys) {
        rs64_s4537_n_phys++;
        rs64_s4537_last_phys = d;
    }
    if (rs64_s4537_n_all == 1u) {
        fprintf(stderr,
            "[s4537-init] kind=arm voice=0x%08X word=0x%08X n_all=%u n_this=%u n_phys=%u\n",
            v, d, rs64_s4537_n_all, rs64_s4537_n_this, rs64_s4537_n_phys);
        fflush(stderr);
    }
    if (exact && rs64_s4537_exact_rows < 16) {
        rs64_s4537_exact_rows++;
        fprintf(stderr,
            "[s4537-init] kind=voice voice=0x%08X word=0x%08X n_all=%u n_this=%u n_phys=%u\n",
            v, d, rs64_s4537_n_all, rs64_s4537_n_this, rs64_s4537_n_phys);
        fflush(stderr);
    } else if (!exact && phys && rs64_s4537_phys_rows < 4) {
        rs64_s4537_phys_rows++;
        fprintf(stderr,
            "[s4537-init] kind=phys voice=0x%08X word=0x%08X n_all=%u n_this=%u n_phys=%u\n",
            v, d, rs64_s4537_n_all, rs64_s4537_n_this, rs64_s4537_n_phys);
        fflush(stderr);
    }
}

static void rs64_s4537_on_jal(gpr voice, gpr raw34) {
    if (!rs64_s4537_enabled()) return;
    uint32_t v = (uint32_t)voice;
    if (v != 0x801724C0u) return;
    uint32_t d = (uint32_t)raw34;
    uint32_t top = d >> 24;
    int bad = (d & 1u) || (top >= 0x20u && top < 0x7fu);
    if (!bad) return;
    if (rs64_s4537_jal_rows >= 4) return;
    rs64_s4537_jal_rows++;
    fprintf(stderr,
        "[s4537-init] kind=jal site=800903F0 voice=0x%08X raw34=0x%08X n_all=%u n_this=%u n_phys=%u last_this=0x%08X last_phys=0x%08X\n",
        v, d, rs64_s4537_n_all, rs64_s4537_n_this, rs64_s4537_n_phys,
        rs64_s4537_last_this, rs64_s4537_last_phys);
    fflush(stderr);
}

'''

anchor = "RECOMP_FUNC void musyxRenderVoiceSamples(uint8_t* rdram, recomp_context* ctx) {\n"
if s.count(anchor) != 1:
    raise SystemExit(f"musyxRenderVoiceSamples anchor count {s.count(anchor)}")
s = s.replace(anchor, helper + anchor, 1)

store = '    rs64_s4535_store(rdram, "800921E8", 1, 0x800921E8u, ctx->r4, ctx->r3, ctx->r5, 0x4u); /* PATCH: s4535 */\n'
store_n = s.count(store)
if store_n != 1:
    raise SystemExit(f"store anchor count {store_n}")
s = s.replace(
    store,
    store + '    rs64_s4537_init_store(ctx->r4, ctx->r3); /* PATCH: s4537 */\n',
    1,
)

jal = '    rs64_s4534_jal(rdram, "800903F0", 3, 0x800903F0u, ctx->r17, ctx->r7, ctx->r5); /* PATCH: s4534 */\n'
jal_n = s.count(jal)
if jal_n != 1:
    raise SystemExit(f"jal anchor count {jal_n}")
s = s.replace(
    jal,
    jal + '    rs64_s4537_on_jal(ctx->r17, ctx->r7); /* PATCH: s4537 */\n',
    1,
)

if s.count("rs64_s4537_init_store(") != 2:
    raise SystemExit("init_store count is not declaration+call")
if s.count("rs64_s4537_on_jal(") != 2:
    raise SystemExit("on_jal count is not declaration+call")
p.write_text(s)
print("applied")
