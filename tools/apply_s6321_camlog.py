#!/usr/bin/env python3
"""s6321 G3c(a) H-matrix: log camera struct (*(0x80138D1C)+0x28, 22 words) and terrain-table floats
(0x80136DC0+0x10..0x28) per buildVisibleTerrainGridAroundCamera call. Env ROGUESQ_G3C_CAMLOG=1."""
import pathlib
BASE = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
LINE = (
    '    { /* PATCH: s6321 camlog */ static int en6321 = -1; static unsigned n6321 = 0;\n'
    '      if (en6321 < 0) { const char* e = getenv("ROGUESQ_G3C_CAMLOG"); en6321 = (e && *e && *e != \'0\') ? 1 : 0; }\n'
    '      if (en6321 && n6321 < 40000u) { uint32_t cp = (uint32_t)MEM_W(0, (int64_t)(int32_t)0x80138D1Cu);\n'
    '        fprintf(stderr, "[camlog] n=%u ptr=%08X cam=", n6321, cp);\n'
    '        if (cp >= 0x80000000u && cp < 0x80800000u) for (int q = 0; q < 22; q++) { uint32_t u = (uint32_t)MEM_W(0x28 + q * 4, (int64_t)(int32_t)cp); float fv; memcpy(&fv, &u, 4); fprintf(stderr, "%g,", fv); }\n'
    '        fprintf(stderr, " tt="); for (int q = 0; q < 10; q++) { uint32_t u = (uint32_t)MEM_W(0x10 + q * 4, (int64_t)(int32_t)0x80136DC0u); float fv; memcpy(&fv, &u, 4); fprintf(stderr, "%g,", fv); }\n'
    '        fprintf(stderr, "\\n"); } n6321++; }\n'
)
def apply(text):
    if "s6321 camlog" in text:
        return text, 0
    k = text.find("    { /* PATCH: s6036 dd */")
    if k < 0:
        return text, 0
    return text[:k] + LINE + text[k:], 1


if __name__ == "__main__":
    p = BASE / "funcs_9.c"
    t, n = apply(p.read_text())
    if n:
        p.write_text(t)
    print(f"funcs_9.c camlog x{n}")
