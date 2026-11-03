#!/usr/bin/env python3
"""s6808 G3: entry hook rs64_preempt_point(rdram) (ultramodern mesgqueue.cpp) on the title text glyph-mesh functions that
run 70-90 ms without an OS call on low-priority threads and starve the pri-122 audio thread (s6808 title AI gaps). The
placeholder "Debris" names are the glyph cell mesh builders (sampled under buildScaledFormatTextElement /
tickFormatMessageWorker). No guest state touched. Idempotent. Usage: fixup_preempt_point.py <RecompiledFuncs dir>"""
import pathlib, sys

base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "../N64Recomp/RecompiledFuncs")
TAG = "/* PATCH: s6808 preempt point */"
FUNCS = ["rasterizeFormatMessageGlyphs", "buildDebrisMeshFromCells", "rebuildDebrisCellGeometry",
         "emitDebrisCellFaces", "buildDebrisCellBitfield"]
decl = "extern void rs64_preempt_point(uint8_t* rdram); " + TAG + "\n"
done = 0
for p in sorted(base.glob("funcs_*.c")):
    s = p.read_text(); o = s
    for f in FUNCS:
        head = f"RECOMP_FUNC void {f}(uint8_t* rdram, recomp_context* ctx) {{\n"
        if head not in s:
            continue
        i = s.index(head) + len(head)
        if TAG not in s[i:i + 200]:
            s = s[:i] + "    rs64_preempt_point(rdram); " + TAG + "\n" + s[i:]
        done += 1
    if s != o:
        if decl not in s:
            s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + decl, 1)
        p.write_text(s)
if done != len(FUNCS):
    sys.exit(f"s6808 preempt point: found {done}/{len(FUNCS)} functions")
print(f"[s6808] preempt point hooks present in {done} functions")
