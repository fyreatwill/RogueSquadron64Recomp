#!/usr/bin/env python3
"""s4538: at musyxInitVoiceFromSample's 0x800921E8 store, count stores
whose voice is congruent to 0x801724C0 modulo 0x88.

Keeps the s4537 census. Prints one arm line on the first store, with
that voice's residue. Prints up to 4 lattice stores and up to 4 stores
of the target voice. On the bad 0x800903F0 jal for that voice, prints
n_all, n_this, and n_lattice. ROGUESQ_LOG_S4538=1. Diagnostic only.
Does not skip the store. Idempotent.
"""
from pathlib import Path

p = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
s = p.read_text()
if "rs64_s4538_init_store" in s:
    print("already applied")
    raise SystemExit(0)

helper = r'''
/* PATCH: s4538 init slot lattice. Diagnostic only. Does not skip the store.
   (voice - 0x801724C0) mod 0x88. 2^32 % 0x88 == 120, so a wrapped uint32
   difference then % 0x88 reports a voice an exact number of slots below
   the target as residue 120. Fold 120 back in when voice < target. */
static unsigned rs64_s4538_n_all = 0;
static unsigned rs64_s4538_n_this = 0;
static unsigned rs64_s4538_n_lattice = 0;
static uint32_t rs64_s4538_last_this = 0;
static int rs64_s4538_on = -1;
static int rs64_s4538_lattice_rows = 0;
static int rs64_s4538_voice_rows = 0;
static int rs64_s4538_jal_rows = 0;

static int rs64_s4538_enabled(void) {
    if (rs64_s4538_on < 0) {
        const char* e = getenv("ROGUESQ_LOG_S4538");
        rs64_s4538_on = (e && e[0] && e[0] != '0') ? 1 : 0;
    }
    return rs64_s4538_on;
}

static uint32_t rs64_s4538_residue(uint32_t voice) {
    const uint32_t target = 0x801724C0u;
    const uint32_t stride = 0x88u;
    uint32_t r = (voice - target) % stride;
    if (voice < target) {
        r = (r + stride - 120u) % stride;
    }
    return r;
}

static void rs64_s4538_init_store(gpr voice, gpr stored) {
    if (!rs64_s4538_enabled()) return;
    uint32_t v = (uint32_t)voice;
    uint32_t d = (uint32_t)stored;
    uint32_t residue = rs64_s4538_residue(v);
    int exact = (v == 0x801724C0u);
    int lattice = (residue == 0u);
    rs64_s4538_n_all++;
    if (exact) {
        rs64_s4538_n_this++;
        rs64_s4538_last_this = d;
    }
    if (lattice) rs64_s4538_n_lattice++;
    if (rs64_s4538_n_all == 1u) {
        fprintf(stderr,
            "[s4538-init] kind=arm voice=0x%08X word=0x%08X residue=%u n_all=%u n_this=%u n_lattice=%u\n",
            v, d, residue, rs64_s4538_n_all, rs64_s4538_n_this, rs64_s4538_n_lattice);
        fflush(stderr);
    }
    if (exact && rs64_s4538_voice_rows < 4) {
        rs64_s4538_voice_rows++;
        fprintf(stderr,
            "[s4538-init] kind=voice voice=0x%08X word=0x%08X residue=%u n_all=%u n_this=%u n_lattice=%u\n",
            v, d, residue, rs64_s4538_n_all, rs64_s4538_n_this, rs64_s4538_n_lattice);
        fflush(stderr);
    }
    if (lattice && rs64_s4538_lattice_rows < 4) {
        rs64_s4538_lattice_rows++;
        fprintf(stderr,
            "[s4538-init] kind=lattice voice=0x%08X word=0x%08X residue=%u n_all=%u n_this=%u n_lattice=%u\n",
            v, d, residue, rs64_s4538_n_all, rs64_s4538_n_this, rs64_s4538_n_lattice);
        fflush(stderr);
    }
}

static void rs64_s4538_on_jal(gpr voice, gpr raw34) {
    if (!rs64_s4538_enabled()) return;
    uint32_t v = (uint32_t)voice;
    if (v != 0x801724C0u) return;
    uint32_t d = (uint32_t)raw34;
    uint32_t top = d >> 24;
    int bad = (d & 1u) || (top >= 0x20u && top < 0x7fu);
    if (!bad) return;
    if (rs64_s4538_jal_rows >= 4) return;
    rs64_s4538_jal_rows++;
    fprintf(stderr,
        "[s4538-init] kind=jal site=800903F0 voice=0x%08X raw34=0x%08X n_all=%u n_this=%u n_lattice=%u last_this=0x%08X\n",
        v, d, rs64_s4538_n_all, rs64_s4538_n_this, rs64_s4538_n_lattice,
        rs64_s4538_last_this);
    fflush(stderr);
}

'''

anchor = "RECOMP_FUNC void musyxRenderVoiceSamples(uint8_t* rdram, recomp_context* ctx) {\n"
if s.count(anchor) != 1:
    raise SystemExit(f"musyxRenderVoiceSamples anchor count {s.count(anchor)}")
s = s.replace(anchor, helper + anchor, 1)

store = '    rs64_s4537_init_store(ctx->r4, ctx->r3); /* PATCH: s4537 */\n'
store_n = s.count(store)
if store_n != 1:
    raise SystemExit(f"store anchor count {store_n}")
s = s.replace(
    store,
    store + '    rs64_s4538_init_store(ctx->r4, ctx->r3); /* PATCH: s4538 */\n',
    1,
)

jal = '    rs64_s4537_on_jal(ctx->r17, ctx->r7); /* PATCH: s4537 */\n'
jal_n = s.count(jal)
if jal_n != 1:
    raise SystemExit(f"jal anchor count {jal_n}")
s = s.replace(
    jal,
    jal + '    rs64_s4538_on_jal(ctx->r17, ctx->r7); /* PATCH: s4538 */\n',
    1,
)

if s.count("rs64_s4538_init_store(") != 2:
    raise SystemExit("init_store count is not declaration+call")
if s.count("rs64_s4538_on_jal(") != 2:
    raise SystemExit("on_jal count is not declaration+call")
p.write_text(s)
print("applied")
