"""s6146b G1d: pc-range census/mark for initHudStruct (0x800C0084..0x800C1B60). Its HUD node lives in a heap object
(s2+0x3C), not in D_8010CA30 (s6146 census: only one initHudStruct store lands in that region), so key on pc.
funcs_33.c macro is widened to always call the hook for pc in range; funcs_13.c hook gets a pc branch placed first.
Env: ROGUESQ_HUD_WATCH=1 logs each distinct pc once ([hudp] w, addr, val); ROGUESQ_HUD_MARKPC=<px>[:<lo-hex>-<hi-hex>]
adds px to stored normal floats (|v| in [1e-3,4096]) for pcs in [lo,hi] (default whole function). Idempotent."""
import pathlib, sys
T = "PATCH: s6146b hudpc"
OLD = "|| (uint32_t)(_a5798 - 0x8010CA30u) < 0x1F00u) rs64_s5798_st("
NEW = "|| (uint32_t)(_a5798 - 0x8010CA30u) < 0x1F00u || ((uint32_t)(pc) - 0x800C0084u) < 0x1ADDu) rs64_s5798_st("
ANC = "void rs64_s5798_st(uint8_t* rdram, recomp_context* ctx, uint32_t pc, uint32_t a, int w, const char* fn) {\n"
ADD = ANC + r'''    if ((uint32_t)(pc - 0x800C0084u) < 0x1ADDu) { /* ''' + T + r''' */
        static int ew = -1; static int cls = 0; static double mk = 0; static uint32_t lo = 0x800C0084u, hi = 0x800C1B60u;
        if (ew < 0) {
            const char* s = getenv("ROGUESQ_HUD_WATCH"); ew = (s && s[0]) ? 1 : 0;
            const char* m = getenv("ROGUESQ_HUD_MARKPC"); const char* cl = getenv("ROGUESQ_HUD_MARKCLS"); if (cl) cls = (cl[0]=='x') ? 1 : (cl[0]=='y') ? 2 : 0;
            if (m && m[0]) { mk = atof(m); const char* c = strchr(m, ':'); if (c) { lo = (uint32_t)strtoul(c + 1, 0, 16); const char* d = strchr(c, '-'); if (d) hi = (uint32_t)strtoul(d + 1, 0, 16); }
                fprintf(stderr, "[hudp] MARK +%g pc %08x-%08x\n", mk, lo, hi); }
        }
        uint32_t v = (uint32_t)MEM_W(0, (gpr)(int32_t)(a & ~3u)); float f; memcpy(&f, &v, 4);
        int marked = 0;
        if (w == 4 && mk != 0 && pc >= lo && pc <= hi && ((f > 1e-3f && f < 4096.f) || (f < -1e-3f && f > -4096.f)) && (cls == 0 || ((f >= 8.f || f <= -8.f) && (a & 0xFu) == (cls == 1 ? 4u : 8u)))) {
            f = (float)(f + mk); memcpy(&v, &f, 4); MEM_W(0, (gpr)(int32_t)(a & ~3u)) = v; marked = 1;
        }
        if (ew || marked) {
            static uint32_t pcs[4096]; static int np = 0; int i;
            for (i = 0; i < np; i++) if (pcs[i] == pc) break;
            if (i == np && np < 4096) { pcs[np++] = pc; fprintf(stderr, "[hudp] pc=%08x a=%08x w=%d val=%08x(%g)%s\n", pc, a, w, v, f, marked ? " MARKED" : ""); }
        }
        return;
    }
'''
def apply(text, name=""):
    if T in text or (name != "funcs_33.c" and name != "funcs_13.c"): return text, 0
    n = 0
    if name == "funcs_33.c":
        if OLD not in text: return text, 0
        text = text.replace(OLD, NEW)
    else:
        if text.count(ANC) != 1: return text, 0
        text = text.replace(ANC, ADD, 1)
    return text + "\n/* " + T + " */\n", 1
if __name__ == "__main__":
    base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    tot = 0
    for p in sorted(base.glob("funcs_*.c")):
        t = p.read_text(); t2, n = apply(t, p.name)
        if t2 != t: p.write_text(t2)
        tot += n
    print("patched:", tot)
