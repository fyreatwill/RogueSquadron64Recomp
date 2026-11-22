#!/usr/bin/env python3
"""s7834 G3 pitch: per-call hex dump of guest RAM 0x80137DB0..0x801384E0 (player object 0x80137DBC.. + camera block 0x80138458..)
at the s6321 camlog site in buildVisibleTerrainGridAroundCamera (guest PC ~0x80043918), printed only when the bytes change.
The retail twin is rs64_oracle --pc-ram-dump 0x80043918:0x80137DB0:0x801384E0 (same PC, same range), so both sides sample
the same instruction. Env ROGUESQ_S7834_RAMDUMP=1 (measurement only; off = untouched). Scorer: tools/s7834_ramdump_cmp.py."""
import pathlib, sys
BASE = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
LINE = (
    '    { /* PATCH: s7834 ramdump */ static int en7834 = -1; static unsigned n7834 = 0, k7834 = 0; static uint32_t last7834[460];\n'
    '      if (en7834 < 0) { const char* e = getenv("ROGUESQ_S7834_RAMDUMP"); en7834 = (e && *e && *e != \'0\') ? 1 : 0; }\n'
    '      if (en7834 && k7834 < 60000u) { uint32_t cur7834[460]; int ch = 0;\n'
    '        for (int q = 0; q < 460; q++) { cur7834[q] = (uint32_t)MEM_W(q * 4, (int64_t)(int32_t)0x80137DB0u); ch |= cur7834[q] != last7834[q]; }\n'
    '        if (ch) { fprintf(stderr, "[ramdump] n=%u w=", n7834); for (int q = 0; q < 460; q++) { fprintf(stderr, "%08X", cur7834[q]); last7834[q] = cur7834[q]; }\n'
    '          fprintf(stderr, "\\n"); k7834++; } }\n'
    '      n7834++; }\n'
)
def apply(text):
    if "s7834 ramdump" in text:
        return text, 0
    k = text.find("    { /* PATCH: s6321 camlog */")
    if k < 0:
        return text, 0
    return text[:k] + LINE + text[k:], 1

if __name__ == "__main__":
    p = (pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else BASE) / "funcs_9.c"
    t, n = apply(p.read_text())
    if n:
        p.write_text(t)
    print(f"funcs_9.c s7834 ramdump x{n}")
