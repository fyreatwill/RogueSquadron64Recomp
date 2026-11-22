#!/usr/bin/env python3
"""s7835 G3 half-tick dt: where does the port's 0.5-tick flight frame come from?
The sim's dt word 0x8011A904 = stamp(0x80128ED8) - prev stamp (computeFrameDeltaTime 0x8000BBB0). The stamp is written only at
0x8001993C in awaitFrameSyncMesgBlock: the low word of osGetTime taken right after each VI message (host clock in the port,
Count in retail), and the same block bumps the retraces-since-flip byte (s6) that the buffer arbiter compares with its limit.
Env ROGUESQ_S7835_DT=1 prints
  [dt7835] vi n=<k> st=<stamp> ctr=<byte s6 before ++> lim=<byte s6-1>       (each VI wake, 0x8001993C)
  [dt7835] fr n=<k> dt=<word 0x8011A904>                                   (each game frame, computeFrameDeltaTime exit)
Interleaves with [ramdump] (s7834) on stderr. Measurement only; off = untouched."""
import pathlib, sys
BASE = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
EN = ('static int en7835 = -1; if (en7835 < 0) { const char* e = getenv("ROGUESQ_S7835_DT"); '
      'en7835 = (e && *e && *e != \'0\') ? 1 : 0; }')
VI_LINE = ('    { /* PATCH: s7835 dtlog vi */ ' + EN + ' static unsigned n7835v = 0;\n'
           '      if (en7835 && n7835v < 400000u) fprintf(stderr, "[dt7835] vi n=%u st=%08X ctr=%u lim=%u\\n", n7835v, (uint32_t)ctx->r16, '
           '(unsigned)ctx->r2, (unsigned)ctx->r3); n7835v++; }\n')
FR_ANCHOR = "L_8000BBE8:\n"
FR_LINE = ('    { /* PATCH: s7835 dtlog fr */ ' + EN + ' static unsigned n7835f = 0;\n'
           '      if (en7835 && n7835f < 400000u) fprintf(stderr, "[dt7835] fr n=%u dt=%u\\n", n7835f, '
           '(uint32_t)MEM_W(0, (int64_t)(int32_t)0x8011A904u)); n7835f++; }\n')

def apply4(text):
    # anchor on the 0x8001993C store line whatever later fixups wrap around it (plain `MEM_W(...) = ctx->r16;` early in the
    # chain, `{ ... RS64_S5798_ST(0x8001993Cu, ...) }` in the final tree)
    if "s7835 dtlog vi" in text:
        return text, 0
    k = text.find("MEM_W(-0X7128, ctx->r1) = ctx->r16;")
    if k < 0:
        return text, 0
    j = text.find("\n", k) + 1
    return text[:j] + VI_LINE + text[j:], 1

def apply3(text):
    if "s7835 dtlog fr" in text:
        return text, 0
    k = text.find("RECOMP_FUNC void computeFrameDeltaTime(")
    if k < 0:
        return text, 0
    j = text.find(FR_ANCHOR, k)
    end = text.find("RECOMP_FUNC void ", k + 10)
    if j < 0 or (end >= 0 and j > end):
        return text, 0
    j += len(FR_ANCHOR)
    return text[:j] + FR_LINE + text[j:], 1

if __name__ == "__main__":
    base = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else BASE
    for name, fn in (("funcs_4.c", apply4), ("funcs_3.c", apply3)):
        p = base / name
        t, n = fn(p.read_text())
        if n:
            p.write_text(t)
        print(f"{name} s7835 dtlog x{n}")
