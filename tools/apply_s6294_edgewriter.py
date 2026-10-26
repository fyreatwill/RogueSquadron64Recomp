"""s6294 G3c: log the terrain visibility-radius writer at 0x80043918.

The log is opt-in so normal runs stay unchanged. It is applied after s6036's
draw-distance transform and survives regeneration through the vendored fixup.
"""

import pathlib


BASE = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
START = '    { /* PATCH: s6036 dd */ static float m6036 = -1.0f;\n'
END = '    // 0x8004391C: lwc1        $f4, 0xC50($s0)\n'


def apply9(text):
    if "PATCH: s6294 edgewriter" in text:
        return text, 0
    i = text.find(START)
    if i < 0:
        return text, 0
    j = text.find(END, i)
    if j < 0:
        raise RuntimeError("s6036 block end not found")
    old = text[i:j]
    new = old.replace(
        '    { /* PATCH: s6036 dd */ static float m6036 = -1.0f;\n',
        '    { /* PATCH: s6036 dd */ static float m6036 = -1.0f;\n'
        '      static int edge_en6294 = -1; static unsigned edge_n6294 = 0;\n'
        '      if (edge_en6294 < 0) { const char* e = getenv("ROGUESQ_G3C_EDGE_WRITER"); edge_en6294 = (e && *e && *e != \'0\') ? 1 : 0; }\n',
        1,
    )
    old_gate = '      { extern volatile int g_rs64_dd_blk; g_rs64_dd_blk = (me6036 != 1.0f); }\n'
    new_gate = old_gate + (
        '      if (edge_en6294 && (edge_n6294 < 12 || (edge_n6294 % 1200u) == 0u)) {\n'
        '        union { uint32_t u; float f; } raw6294; raw6294.u = ctx->f2.u32l;\n'
        '        int valid6294 = MEM_W(4, (int64_t)(int32_t)0x80136DC0) != 0;\n'
        '        const char* a = getenv("ROGUESQ_ASPECT_SCALE");\n'
        '        fprintf(stderr, "[edge-writer] pc=0x80043918 n=%u arm=%s dd=%g raw=%g eff=%g valid=%d r31=0x%08X\\n", edge_n6294, (a && *a) ? a : "retail", m6036, raw6294.f, me6036, valid6294, (unsigned)ctx->r31);\n'
        '        fflush(stderr);\n'
        '      }\n'
        '      edge_n6294++;\n'
    )
    if old_gate not in new:
        raise RuntimeError("s6036 gate anchor not found")
    new = new.replace(old_gate, new_gate, 1)
    return text[:i] + new + text[j:], 1


if __name__ == "__main__":
    p = BASE / "funcs_9.c"
    t = p.read_text()
    t2, n = apply9(t)
    if n:
        p.write_text(t2)
    print(f"funcs_9.c live patched x{n}")
