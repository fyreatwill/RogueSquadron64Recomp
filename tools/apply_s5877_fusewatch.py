"""s5877: writer census for the player object's fuse state [0x80137F3C, +0xC) = obj(0x80137DBC)+0x180 flags / +0x184 fuse timer.

Widens the s5798 store hook range check and, in funcs_13.c, prints one [fzw] line per store (pc, ra, fn, width,
read-back word, object pos y +0x50, slot +0xB8) under ROGUESQ_LOG_MTM.  The per-frame timer decrement at pc 0x800B1080/0x800B10D8
is the positive control (must appear) and is rate-limited; every other writer is logged in full.  Idempotent;
mirrored into fixup_game_funcs_vendored.py (after apply_s5868_flagwatch.py).
"""
import pathlib
import sys

T = "PATCH: s5877 fusewatch"
OLD = "|| (uint32_t)(_a5798 - 0x8010CA1Cu) < 4u) rs64_s5798_st("
NEW = "|| (uint32_t)(_a5798 - 0x8010CA1Cu) < 4u || (uint32_t)(_a5798 - 0x80137F3Cu) < 0xCu) rs64_s5798_st("
ANC = "void rs64_s5798_st(uint8_t* rdram, recomp_context* ctx, uint32_t pc, uint32_t a, int w, const char* fn) {\n"
ADD = ANC + r'''    if ((uint32_t)(a - 0x80137F3Cu) < 0xCu) { /* ''' + T + r''' */
        extern long long rs64_s5773_ms(void);
        static int e = -1, n = 0, dec = 0; if (e < 0) { const char* s = getenv("ROGUESQ_LOG_MTM"); e = (s && s[0]) ? 1 : 0; }
        if (e) {
            int isdec = (pc == 0x800B1080u || pc == 0x800B10D8u);
            if (isdec) dec++;
            static uint32_t lastflg = 0xFFFFFFFFu; uint32_t v0 = (uint32_t)MEM_W(0, (gpr)(int32_t)(a & ~3u)); int skipflg = (a == 0x80137F3Cu && v0 == lastflg); if (a == 0x80137F3Cu) lastflg = v0;
            if (!skipflg && (!isdec || dec <= 4 || dec % 60 == 0) && n++ < 600) {
                uint32_t v = v0; float y, f; uint32_t yu = (uint32_t)MEM_W(0, (gpr)(int32_t)0x80137E0Cu); memcpy(&y, &yu, 4); memcpy(&f, &v, 4);
                fprintf(stderr, "[fzw] t=%lld a=%08x w=%d val=%08x(%g) pc=%08x ra=%08x fn=%s y=%g slot=%d dec=%d\n", rs64_s5773_ms(), a, w, v, f, pc, (uint32_t)ctx->r31, fn ? fn : "?", y, (int)MEM_W(0, (gpr)(int32_t)0x80137E74u), dec);
            }
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
        t = p.read_text()
        t2, n = apply(t, p.name)
        if t2 != t:
            p.write_text(t2)
        tot += n
    print("files widened:", tot)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    s = fp.read_text()
    if "apply_s5877_fusewatch" not in s:
        lst = '    "apply_s5868_flagwatch.py",\n'
        assert s.count(lst) == 1
        fp.write_text(s.replace(lst, lst + '    "apply_s5877_fusewatch.py",\n', 1))
        print("fixup patched")
