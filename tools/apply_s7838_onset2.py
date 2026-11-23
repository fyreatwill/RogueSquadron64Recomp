#!/usr/bin/env python3
"""s7838 G3 discriminator: does the port fly retail's exact path once its flight-onset dt matches retail's?
s7834/s7836/s7838 found the port's first flight frame takes dt = 1 VI (781250 ticks; legal guest logic, s7835: the
submitGfxFrame twin sampled 1 VI before the first sim frame), retail 2 VI, and the camera swing-in then settles at a
different rest pitch (lvl4: w441 0.1917 port vs 0.2084 retail CPO1 and CPO2) -> the reticle rests 5.75 px lower.
Env ROGUESQ_VI_STAMP_ONSET2=<vi> (needs ROGUESQ_VI_STAMP=1 so dts are whole VIs): once total_vis >= <vi>, any frame dt
of exactly 1 VI written to 0x8011A904 by either writer, computeFrameDeltaTime (0x8000BBE4) or its inline twin in
submitGfxFrame (0x8000C47C, s7835), is raised to 2 VI before it is used; each
raise logs `[s7838] onset2 <site> dt 781250->1562500 vi=<total_vis>`. Only the sim dt word changes (the stamp and its copies
stay), so it is a measurement lever, not a fix. Unset/0 = untouched. Inserted at L_8000BBE8 (ahead of the s7835 dtlog)
and at L_8000C480. First s7838 run patched only the first writer and changed nothing: the twin's dt is the one in use."""
import pathlib, sys
BASE = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
SITES = (("bbe8", "RECOMP_FUNC void computeFrameDeltaTime(", "L_8000BBE8:\n"), ("c480", None, "L_8000C480:\n"))
def line(site):
    return ('    { /* PATCH: s7838 onset2 ' + site + ' */ static long long from7838 = -2; if (from7838 == -2) { const char* e = getenv("ROGUESQ_VI_STAMP_ONSET2"); '
        'from7838 = (e && *e && *e != \'0\') ? atoll(e) : -1; if (from7838 >= 0) fprintf(stderr, "[s7838] onset2 armed from vi=%lld\\n", from7838); }\n'
        '      if (from7838 >= 0) { extern uint64_t total_vis; if ((long long)total_vis >= from7838 && (uint32_t)MEM_W(0, (int64_t)(int32_t)0x8011A904u) == 781250u) { '
        'MEM_W(0, (int64_t)(int32_t)0x8011A904u) = 1562500; fprintf(stderr, "[s7838] onset2 ' + site + ' dt 781250->1562500 vi=%llu\\n", '
        '(unsigned long long)total_vis); } } }\n')

def apply3(text):
    n = 0
    for site, func, anchor in SITES:
        if ("s7838 onset2 " + site) in text:
            continue
        k = text.find(func) if func else 0
        if k < 0:
            continue
        j = text.find(anchor, k)
        if func:
            end = text.find("RECOMP_FUNC void ", k + 10)
            if end >= 0 and j > end:
                continue
        if j < 0 or text.count(anchor) != 1:
            continue
        j += len(anchor)
        text = text[:j] + line(site) + text[j:]
        n += 1
    return text, n

if __name__ == "__main__":
    base = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else BASE
    p = base / "funcs_3.c"
    t, n = apply3(p.read_text())
    if n:
        p.write_text(t)
    print(f"funcs_3.c s7838 onset2 x{n}")
