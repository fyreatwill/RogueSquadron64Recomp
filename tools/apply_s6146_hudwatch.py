"""s6146 G1d: HUD struct store census + "mark everything" positive control.
Widens the s5798 store hook to the HUD struct array D_8010CA30[2] (0xF80 B each, 0x1F00 total) and, in funcs_13.c's
rs64_s5798_st, (a) under ROGUESQ_HUD_WATCH logs one [hudw] line per distinct (pc) with first value/offset/count and
(b) under ROGUESQ_HUD_MARK=<px>[:<pc-hex>|all] adds px to the stored float (normal floats |v| in [1e-3,4096] only).
Default env unset = no behaviour change. Idempotent."""
import pathlib, sys

T = "PATCH: s6146 hudwatch"
OLD = "|| (uint32_t)(_a5798 - 0x80137F3Cu) < 0xCu) rs64_s5798_st("
NEW = "|| (uint32_t)(_a5798 - 0x80137F3Cu) < 0xCu || (uint32_t)(_a5798 - 0x8010CA30u) < 0x1F00u) rs64_s5798_st("
ANC = "void rs64_s5798_st(uint8_t* rdram, recomp_context* ctx, uint32_t pc, uint32_t a, int w, const char* fn) {\n"
ADD = ANC + r'''    if ((uint32_t)(a - 0x8010CA30u) < 0x1F00u) { /* ''' + T + r''' */
        static int ew = -1; static double mk = 0; static int mkall = 0; static uint32_t mkpc = 0;
        if (ew < 0) {
            const char* s = getenv("ROGUESQ_HUD_WATCH"); ew = (s && s[0]) ? 1 : 0;
            const char* m = getenv("ROGUESQ_HUD_MARK");
            if (m && m[0]) { mk = atof(m); const char* c = strchr(m, ':'); if (c) { if (!strcmp(c + 1, "all")) mkall = 1; else mkpc = (uint32_t)strtoul(c + 1, 0, 16); } else mkall = 1;
                fprintf(stderr, "[hudw] MARK +%g all=%d pc=%08x\n", mk, mkall, mkpc); }
        }
        uint32_t v = (uint32_t)MEM_W(0, (gpr)(int32_t)(a & ~3u)); float f; memcpy(&f, &v, 4);
        if (w == 4 && mk != 0 && (mkall || pc == mkpc) && ((f > 1e-3f && f < 4096.f) || (f < -1e-3f && f > -4096.f))) {
            f = (float)(f + mk); memcpy(&v, &f, 4); MEM_W(0, (gpr)(int32_t)(a & ~3u)) = v;
        }
        if (ew) {
            static uint32_t pcs[512]; static uint32_t cnt[512]; static int np = 0; int i;
            for (i = 0; i < np; i++) if (pcs[i] == pc) break;
            if (i == np && np < 512) { pcs[np++] = pc; cnt[i] = 0; }
            if (i < np) { if (cnt[i]++ < 2) fprintf(stderr, "[hudw] pc=%08x a=%08x off=%03x w=%d val=%08x(%g) fn=%s\n", pc, a, a - 0x8010CA30u, w, v, f, fn ? fn : "?"); }
        }
        return;
    }
'''

def apply(text, name=""):
    if T in text or OLD not in text:
        return text, 0
    text = text.replace(OLD, NEW)
    if name == "funcs_13.c":
        assert text.count(ANC) == 1
        text = text.replace(ANC, ADD, 1)
    return text + "\n/* " + T + " */\n", 1

if __name__ == "__main__":
    base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    tot = 0
    for p in sorted(base.glob("funcs_*.c")):
        t = p.read_text(); t2, n = apply(t, p.name)
        if t2 != t: p.write_text(t2)
        tot += n
    print("files widened:", tot)
