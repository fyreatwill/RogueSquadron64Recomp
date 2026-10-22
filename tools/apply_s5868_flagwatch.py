"""s5868: writer census for the mission-flags word 0x8010CA1C (gates playerXwingUpdate msg 3, see s5867).

Widens the s5798 store hook range check to the word and, in funcs_13.c, prints one [flw] line per store to it
(pc, ra, fn, stored value w).  Positive control: the 0->0x101 and 0x101->0 transitions seen in [plc] must show writers.
Idempotent; mirrored into fixup_game_funcs_vendored.py (after apply_s5867b_msg.py).
"""
import pathlib
import sys

T = "PATCH: s5868 flagwatch"
OLD = "|| (uint32_t)(_a5798 - 0x80137DB0u) < 0x120u) rs64_s5798_st("
NEW = "|| (uint32_t)(_a5798 - 0x80137DB0u) < 0x120u || (uint32_t)(_a5798 - 0x8010CA1Cu) < 4u) rs64_s5798_st("
ANC = "void rs64_s5798_st(uint8_t* rdram, recomp_context* ctx, uint32_t pc, uint32_t a, int w, const char* fn) {\n"
ADD = ANC + r'''    if ((uint32_t)(a - 0x8010CA1Cu) < 4u) { /* ''' + T + r''' */
        extern long long rs64_s5773_ms(void);
        static int n = 0;
        if (n++ < 4000) fprintf(stderr, "[flw] t=%lld a=%08x w=%08x pc=%08x ra=%08x fn=%s\n", rs64_s5773_ms(), a, (uint32_t)w, pc, (uint32_t)ctx->r31, fn ? fn : "?");
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
    if "apply_s5868_flagwatch" not in s:
        lst = '    "apply_s5867b_msg.py",\n]\n'
        assert s.count(lst) == 1
        fp.write_text(s.replace(lst, '    "apply_s5867b_msg.py",\n    "apply_s5868_flagwatch.py",\n]\n', 1))
        print("fixup patched")
