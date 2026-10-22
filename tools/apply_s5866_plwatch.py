"""s5866: runtime writer census for the player craft record [0x80137DB0, +0x120).

Widens the s5798 store hook range check (every generated store) to also cover the player record and, in funcs_13.c,
adds a per-word table (write count, last pc, last ra, last fn).  Once per second of wall time (rs64_s5773_ms) a
[plw] line lists every word written since the last line as +off:count@pc, so a frozen ship window (no stick effect)
can be compared with an A-hold window in one run.  Positive control: the A window must show writers.
Idempotent; mirrored into fixup_game_funcs_vendored.py (after apply_s5798_recwatch.py).
"""
import pathlib
import sys

T = "PATCH: s5866 plwatch"
OLD = "if ((uint32_t)(_a5798 - 0x80165B00u) < 0x300u) rs64_s5798_st("
NEW = "if ((uint32_t)(_a5798 - 0x80165B00u) < 0x300u || (uint32_t)(_a5798 - 0x80137DB0u) < 0x120u) rs64_s5798_st("
ANC = "void rs64_s5798_st(uint8_t* rdram, recomp_context* ctx, uint32_t pc, uint32_t a, int w, const char* fn) {\n"
ADD = ANC + r'''    if ((uint32_t)(a - 0x80137DB0u) < 0x120u) { /* ''' + T + r''' */
        static struct { uint32_t n, pc, ra, val; const char* fn; } pl[0x120 / 4];
        static long long last_ms = -1; extern long long rs64_s5773_ms(void);
        uint32_t k = (a - 0x80137DB0u) >> 2;
        pl[k].n++; pl[k].pc = pc; pl[k].ra = (uint32_t)ctx->r31; pl[k].fn = fn; pl[k].val = (uint32_t)MEM_W(0, (gpr)(int32_t)(a & ~3u));
        long long ms = rs64_s5773_ms();
        if (last_ms < 0) last_ms = ms;
        if (ms - last_ms >= 1000) {
            static int e = -1; if (e < 0) { const char* s = getenv("ROGUESQ_PLAYER_DUMP"); e = (s && s[0]) ? 1 : 0; }
            if (e) { char buf[1800]; int off = 0; buf[0] = 0;
                for (int i = 0; i < 0x120 / 4 && off < 1700; i++) if (pl[i].n) off += snprintf(buf + off, sizeof(buf) - off, " %x:%u@%08x/%s=%08x", (unsigned)(i * 4 + 0xB0), pl[i].n, pl[i].pc, pl[i].fn ? pl[i].fn : "?", pl[i].val);
                fprintf(stderr, "[plw] t=%lld base=80137d00+%s\n", ms, buf); }
            memset(pl, 0, sizeof(pl)); last_ms = ms;
        }
        return;
    }
'''


def apply(text, name=""):
    if T in text:
        return text, 0
    if OLD not in text:
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
    if "apply_s5866_plwatch" in s:
        print("fixup already")
    else:
        lst = '    "apply_s5798_recwatch.py",\n]\n'
        assert s.count(lst) == 1
        fp.write_text(s.replace(lst, '    "apply_s5798_recwatch.py",\n    "apply_s5866_plwatch.py",\n]\n', 1))
        print("fixup patched")
