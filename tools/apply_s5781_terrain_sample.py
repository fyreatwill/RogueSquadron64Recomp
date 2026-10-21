"""s5781: log the terrain sampler (sampleTerrainAtNpcPosition 0x80068D5C) the
orientation stepper calls at 0x800FF3A4, for the player only.

The sampler is a 2D grid march: struct 0x80136DC0 holds cell-index array (+0),
cell-record array (+4, stride 30), origin x (+0x20) / z (+0x2C) / y (+0x18),
scale (+0x10), width (+0x38 = 0x80136DF8) and height (+0x3A). Each cell's
lhu & 0x1FFF indexes a record whose signed byte +3 is compared with the
scaled player y. The helper replays that cell lookup for the player's own
cell and prints x,y,z, the scaled y, record bytes and the sampler's return.
Prints every 250 ms and on every return-value change (cap 400).
Gated by ROGUESQ_LOG_MTM.
"""
import pathlib
import sys

TAG = "PATCH: s5781 terrain sample"
CALL = "    sampleTerrainAtNpcPosition(rdram, ctx);\n"

HELPER = """/* """ + TAG + """ */
static int s5781_e = -1;
static unsigned s5781_left = 400;
static long long s5781_last_ms = -1000;
static int s5781_last_ret = -1;
static uint8_t* s5781_ram;
static uint32_t s5781_rd(uint32_t a) { uint8_t* rdram = s5781_ram; return (uint32_t)MEM_W(0, (int64_t)(int32_t)a); }
static float s5781_f(uint32_t a) { union { uint32_t u; float f; } p; p.u = s5781_rd(a); return p.f; }
static void s5781_sample(uint8_t* rdram, recomp_context* ctx) {
    uint32_t obj, pos, vel;
    int player, ret;
    float x = 0, y = 0, z = 0;
    if (s5781_e < 0) {
        const char* e = getenv("ROGUESQ_LOG_MTM");
        s5781_e = (e && e[0] && e[0] != '0') ? 1 : 0;
    }
    s5781_ram = rdram;
    obj = (uint32_t)MEM_W(ctx->r29, 0X4F8);
    player = (obj == 0x80137DBCu);
    pos = (uint32_t)U32(ctx->r4);
    vel = (uint32_t)U32(ctx->r5);
    if (s5781_e && player) { x = s5781_f(pos); y = s5781_f(pos + 4); z = s5781_f(pos + 8); }
    sampleTerrainAtNpcPosition(rdram, ctx);
    if (!s5781_e || !player || !s5781_left) return;
    ret = (int)ctx->r2;
    {
        extern long long rs64_s5773_ms(void);
        long long ms = rs64_s5773_ms();
        const uint32_t G = 0x80136DC0u;
        float k = s5781_f(0x8003C838u), ys, gx, gz;
        uint32_t W = s5781_rd(G + 0x38) & 0xFFFFu, H = s5781_rd(G + 0x38) >> 16;
        int ix, iz, cell_ok = 0;
        unsigned idx = 0, b3 = 0, b0 = 0, b1 = 0, b2 = 0, b4 = 0;
        if (ms - s5781_last_ms < 250 && ret == s5781_last_ret) return;
        s5781_last_ms = ms; s5781_last_ret = ret; s5781_left--;
        gx = (x - s5781_f(G + 0x20)) * k;
        gz = (z - s5781_f(G + 0x2C)) * k;
        ys = (y - s5781_f(G + 0x18)) / s5781_f(G + 0x10) * s5781_f(0x8003C844u);
        ix = (int)gx; iz = (int)gz;
        if (gx >= 0 && gz >= 0 && ix < (int)W && iz < (int)H) {
            uint32_t cp = s5781_rd(G) + (uint32_t)((iz * (int)W + ix) * 2);
            uint32_t w = s5781_rd(cp & ~3u);
            uint32_t rec;
            idx = ((cp & 2) ? (w & 0xFFFFu) : (w >> 16)) & 0x1FFFu;
            rec = s5781_rd(G + 4) + idx * 30u;
            b0 = s5781_rd(rec & ~3u) >> 24; b1 = (s5781_rd(rec & ~3u) >> 16) & 0xFF;
            b2 = (s5781_rd(rec & ~3u) >> 8) & 0xFF; b3 = s5781_rd(rec & ~3u) & 0xFF;
            b4 = s5781_rd((rec + 4) & ~3u) >> 24;
            cell_ok = 1;
        }
        fprintf(stderr, "[terr] t=%lld ret=%d pos=(%.2f,%.2f,%.2f) vel=0x%08X g=(%.2f,%.2f) ys=%.2f W=%u H=%u cell=%d idx=%u rec[0..4]=%u,%u,%u,%d(b3s),%u\\n",
            ms, ret, x, y, z, vel, gx, gz, ys, W, H, cell_ok, idx, b0, b1, b2, (int)(int8_t)b3, b4);
        fflush(stderr);
    }
}
"""


def apply(text):
    if TAG in text:
        return text, 0
    if text.count(CALL) != 1:
        raise RuntimeError(f"call count {text.count(CALL)}")
    out = []
    helper_done = False
    n = 0
    for line in text.splitlines(keepends=True):
        if not helper_done and line == '#include "funcs.h"\n':
            out.append(line)
            out.append(HELPER)
            helper_done = True
            continue
        if line == CALL:
            out.append(f"    s5781_sample(rdram, ctx); /* {TAG} */\n")
            n += 1
            continue
        out.append(line)
    if not helper_done:
        raise RuntimeError('missing #include "funcs.h"')
    return "".join(out), n


if __name__ == "__main__":
    base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    p = base / "funcs_43.c"
    updated, count = apply(p.read_text())
    if count:
        p.write_text(updated)
