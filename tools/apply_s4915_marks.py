#!/usr/bin/env python3
"""s4915: marks in postSwapRdpReset (entry, post-BF20 return value) and bufferArbiterAllocSlot entry.
Idempotent. Usage: apply_s4915_marks.py <RecompiledFuncs dir>. Reuses rs64_s4913_mark (host dumps
flag A/B plus arbiter slot bytes 0x80128EA8..B7 for tags starting 'psrr' / 'bAlloc')."""
import sys, pathlib

DECL = 'extern void rs64_s4913_mark(uint8_t* rdram, const char* tag);\n'
CALL = "    bufferArbiterAllocSlot(rdram, ctx);\n"


def mark(tag):
    return f'    rs64_s4913_mark(rdram, {tag}); // PATCH: s4915 mark\n'


def func_span(t, name):
    i = t.index("RECOMP_FUNC void " + name + "(")
    j = t.index("{\n", i) + 2
    k = t.find("RECOMP_FUNC void ", j)
    return i, j, (len(t) if k < 0 else k)


def patch_text(t):
    if "RECOMP_FUNC void postSwapRdpReset(" in t:
        i, j, e = func_span(t, "postSwapRdpReset")
        if "s4915 mark" not in t[i:e]:
            k = t.index(CALL, j) + len(CALL)
            t = t[:k] + mark('(ctx->r2 ? "psrr-bf20-ret-nz" : "psrr-bf20-ret-0")') + t[k:]
            t = t[:j] + mark('"psrr-entry"') + t[j:]
    if "RECOMP_FUNC void bufferArbiterAllocSlot(" in t:
        i, j, e = func_span(t, "bufferArbiterAllocSlot")
        if "s4915 mark" not in t[i:e]:
            t = t[:j] + mark('"bAlloc-entry"') + t[j:]
    if "s4915 mark" in t and DECL not in t:
        t = t.replace('#include "recomp.h"\n', '#include "recomp.h"\n' + DECL, 1)
    return t


if __name__ == "__main__":
    for p in sorted(pathlib.Path(sys.argv[1]).glob("funcs_*.c")):
        t = p.read_text()
        n = patch_text(t)
        if n != t:
            p.write_text(n)
            print("patched", p.name)
