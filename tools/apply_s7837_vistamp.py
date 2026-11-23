#!/usr/bin/env python3
"""s7837 G3 port determinism: quantise the guest frame stamp to whole VIs.
The sim's dt (0x8011A904) is stamp(0x80128ED8) - previous stamp. The stamp is written only at 0x8001993C in
awaitFrameSyncMesgBlock from the low word of osGetTime taken when the guest thread wakes on a VI message. Retail reads
Count, so its stamps are VI-exact; the port reads the host clock, so every stamp carries host wake jitter (s7837: raw
per-VI deltas 781078..781406 ticks, the flight-onset dt 0.79 / 1.00 / 0.98 VI over three identical runs), and two
identical runs fork guest state ~160 flight frames in.
Env ROGUESQ_VI_STAMP=1 overwrites the stored stamp with (uint32)(total_vis * 781250), the ultramodern VI counter
(events.cpp, global) times the 46.875 MHz / 60 Hz Count ticks per VI. r16 stays the raw host stamp, so the s7835
`[dt7835] vi st=` log keeps showing the jitter while `[dt7835] fr dt=` shows the quantised dt.
Every reader of 0x80128ED8 (0x8000BBD8/BBEC computeFrameDeltaTime, 0x8000BE20 submitGfxFrame, 0x8000C470/C484
timeSnapshotFiller) subtracts an earlier copy of the same stamp, so a pure stamp-only time base is consistent.
Off (unset/0) = untouched retail-port behaviour."""
import pathlib, sys
BASE = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
ANCHOR = "MEM_W(-0X7128, ctx->r1) = ctx->r16;"
LINE = ('    { /* PATCH: s7837 vistamp */ static int en7837 = -1; if (en7837 < 0) { const char* e = getenv("ROGUESQ_VI_STAMP"); '
        'en7837 = (e && *e && *e != \'0\') ? 1 : 0; if (en7837) fprintf(stderr, "[s7837] vistamp on: stamp = total_vis * 781250\\n"); }\n'
        '      if (en7837) { extern uint64_t total_vis; MEM_W(-0X7128, ctx->r1) = (int32_t)(uint32_t)(total_vis * 781250ull); } }\n')

def apply4(text):
    if "s7837 vistamp" in text:
        return text, 0
    k = text.find(ANCHOR)
    if k < 0:
        return text, 0
    j = text.find("\n", k) + 1
    return text[:j] + LINE + text[j:], 1

if __name__ == "__main__":
    base = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else BASE
    p = base / "funcs_4.c"
    t, n = apply4(p.read_text())
    if n:
        p.write_text(t)
    print(f"funcs_4.c s7837 vistamp x{n}")
