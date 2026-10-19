"""s5520: one-shot, idempotent apply of the B40 writer logger to the LIVE RecompiledFuncs tree.
Same regex as the s5520 block in fixup_game_funcs_vendored.py (which covers regen); the vendored fixup is not
idempotent so it cannot be re-run on the live tree."""
import re, pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
pat = re.compile(r"(    // (0x[0-9A-F]{8}): sb [^\n]*\n(?:(?!    // 0x)[^\n]*\n){0,4}?)    MEM_B\(0XB40, ctx->(r\d+)\) = ([^;]+);\n")
def sub(m):
    return (m.group(1) + "    { static int s_b = 0; uint32_t _v = (uint32_t)(" + m.group(4) + ") & 0xFF; if (s_b < 200 && (uint32_t)ADD32(ctx->" + m.group(3) + ", 0XB40) == 0x80130B40u) { s_b++; fprintf(stderr, \"[b40w] pc=" + m.group(2) + " val=0x%02X\\n\", _v); } MEM_B(0XB40, ctx->" + m.group(3) + ") = (uint8_t)_v; } /* PATCH: s5520 b40 writer log */\n")
for n in ["funcs_17.c", "funcs_27.c", "funcs_34.c", "funcs_8.c"]:
    p = base / n
    t = p.read_text()
    if "s5520 b40" in t:
        print(n, "already")
        continue
    t2, k = pat.subn(sub, t)
    print(n, k)
    p.write_text(t2)
