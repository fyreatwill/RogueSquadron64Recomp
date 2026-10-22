"""s5912: winner-selection witness in audioCueDispatcherNpcHandler's projectile loop (ROGUESQ_LOG_HUDBIT). Per sphere hit (stage 3, ret!=0): id, t=*(sp+0x70), running best (f20),
update fn of the NPC. Per round (reset at stage 0, summarised at L_8005D288): winner id, t, floats @0x8003B03C/0x8003B040. Per-id tally: cross, win, lost(cross but another id won),
band of t of wins (<=A, <=B, >B). Control: ids that get killed (msg5 recipients) must show wins in band<=A. Idempotent; mirrored into fixup."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s5912 shadow"
HELP = r'''/* PATCH: s5912 shadow helpers */
static struct { uint32_t id, fn; unsigned cross, win, lost, wb[3], mind; float mint; } rs5912_T[64]; static unsigned rs5912_n, rs5912_rounds, rs5912_r0, rs5912_rwin;
static struct { uint32_t id; float t; } rs5912_R[24]; static unsigned rs5912_rn;
static int rs5912_en(void) { static int e = -1; if (e < 0) { const char* s = getenv("ROGUESQ_LOG_HUDBIT"); e = (s && s[0]) ? 1 : 0; } return e; }
static float rs5912_f(uint8_t* rdram, uint32_t a) { union { uint32_t u; float f; } x; x.u = (uint32_t)MEM_W(S32((int32_t)a), 0); return x.f; }
static unsigned rs5912_slot(uint8_t* rdram, uint32_t id) { unsigned z; for (z = 0; z < rs5912_n; z++) if (rs5912_T[z].id == id) return z; if (z >= 64) return 63; rs5912_T[z].id = id; { uint32_t tb = (uint32_t)MEM_W(S32((int32_t)0x80130BB0u), 0), n = (uint32_t)MEM_W(S32((int32_t)(tb + id * 8)), 0); rs5912_T[z].fn = ((n >> 24) == 0x80) ? (uint32_t)MEM_W(S32((int32_t)n), 0) : 0; } rs5912_T[z].mint = 1e30f; rs5912_n++; return z; }
static void rs5912_start(void) { if (!rs5912_en()) return; rs5912_rn = 0; }
static void rs5912_hit(uint8_t* rdram, uint32_t id, uint32_t sp) { if (!rs5912_en()) return; float t = rs5912_f(rdram, sp + 0x70); unsigned z = rs5912_slot(rdram, id); rs5912_T[z].cross++; if (t < rs5912_T[z].mint) rs5912_T[z].mint = t; if (rs5912_rn < 24) { rs5912_R[rs5912_rn].id = id; rs5912_R[rs5912_rn].t = t; rs5912_rn++; } }
static void rs5912_end(uint8_t* rdram, uint32_t win, float best) { if (!rs5912_en()) return; rs5912_rounds++; float A = rs5912_f(rdram, 0x8003B03Cu), B = rs5912_f(rdram, 0x8003B040u);
  if (!rs5912_rn) { rs5912_r0++; } else {
    for (unsigned i = 0; i < rs5912_rn; i++) { unsigned z = rs5912_slot(rdram, rs5912_R[i].id); if ((win & 0xFFFF) != rs5912_R[i].id) rs5912_T[z].lost++; }
    if ((win & 0xFFFF) != 0xFFFF) { unsigned z = rs5912_slot(rdram, win & 0xFFFF); rs5912_T[z].win++; rs5912_rwin++; rs5912_T[z].wb[best <= A ? 0 : best <= B ? 1 : 2]++; }
    if (rs5912_rn > 1) { static unsigned pm; if (pm++ < 40) { fprintf(stderr, "[s5912] round multi n=%u win=%x best=%g A=%g B=%g:", rs5912_rn, win & 0xFFFF, best, A, B); for (unsigned i = 0; i < rs5912_rn; i++) fprintf(stderr, " %x(t=%g)", rs5912_R[i].id, rs5912_R[i].t); fprintf(stderr, "\n"); } } }
  if ((rs5912_rounds & 255) == 0) { fprintf(stderr, "[s5912] rounds=%u nohit=%u haswin=%u A=%g B=%g ids:", rs5912_rounds, rs5912_r0, rs5912_rwin, A, B); for (unsigned z = 0; z < rs5912_n; z++) fprintf(stderr, " %x{fn=%x x=%u w=%u lost=%u wb=%u/%u/%u mint=%g}", rs5912_T[z].id, rs5912_T[z].fn, rs5912_T[z].cross, rs5912_T[z].win, rs5912_T[z].lost, rs5912_T[z].wb[0], rs5912_T[z].wb[1], rs5912_T[z].wb[2], rs5912_T[z].mint); fprintf(stderr, "\n"); } }
'''
A0 = "    rs5861_ev(rdram, 0, 0, 0); /* PATCH: s5861 shadow */\n"
A3 = "    if (ctx->r2) rs5861_ev(rdram, 3, (uint32_t)(ctx->r16 & 0xFFFF), (uint32_t)ctx->r29); /* PATCH: s5861 shadow */\n"
AE = "L_8005D288:\n"
AH = "static void rs5861_ev(uint8_t* rdram, uint32_t stage, uint32_t id, uint32_t sp) {"
def apply(text):
    if TAG in text or A0 not in text or "RECOMP_FUNC void audioCueDispatcherNpcHandler(" not in text: return text, 0
    assert text.count(A0) == 1 and text.count(A3) == 1 and text.count(AE) == 1 and text.count(AH) == 1
    text = text.replace(AH, HELP + AH, 1)
    text = text.replace(A0, A0 + "    rs5912_start(); /* " + TAG + " */\n", 1)
    text = text.replace(A3, A3 + "    if (ctx->r2) rs5912_hit(rdram, (uint32_t)(ctx->r16 & 0xFFFF), (uint32_t)ctx->r29); /* " + TAG + " */\n", 1)
    text = text.replace(AE, AE + "    rs5912_end(rdram, (uint32_t)ctx->r4, ctx->f20.fl); /* " + TAG + " */\n", 1)
    return text, 1
if __name__ == "__main__":
    p = base / "funcs_13.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("live patched x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    s = fp.read_text()
    if "apply_s5912_shadow" in s: print("fixup already")
    else:
        anc = '    if p.name == "funcs_8.c":\n        import apply_s5910_postra as _a5910'
        assert s.count(anc) == 1
        blk = ('    if p.name == "funcs_13.c":\n        import apply_s5912_shadow as _a5912\n        text, _n5912 = _a5912.apply(text)\n'
               '        if _n5912:\n            changed = True\n            report.append(f"{p.name}: s5912 shadow x{_n5912}")\n\n')
        s = s.replace(anc, blk + anc, 1)
        lst = '    "apply_s5910_postra.py",\n'
        assert s.count(lst) == 1
        s = s.replace(lst, lst + '    "apply_s5912_shadow.py",\n', 1)
        fp.write_text(s); print("fixup patched")
