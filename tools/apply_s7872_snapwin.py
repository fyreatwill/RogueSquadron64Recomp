#!/usr/bin/env python3
"""s7872 G3 lever: VI-windowed timeSnapshotFiller el override (0x8000BE28), applied AFTER the s7839/s7840 pin.

Env ROGUESQ_S7872_SNAP_WIN=<lo>:<hi>:<el> sets v0 (el = stamp - prev) to <el> while lo <= total_vis < hi, on top of whatever
ROGUESQ_RETAIL_SNAP / ROGUESQ_S7839_SNAP_EL put there. Why: the retail CPO1 oracle (s7872 scratch/s7872/rsnap) shows el is
NOT a constant: 0 on most pre-flight frames (incl. the opening cinematic, retail dt rows 2610-3588) and 1 VI in the hangar
stretch, on single post-load frames and in flight (s7840's 811160). A whole-run el=0 pin forks the boot/menu state (s7872 p1:
0-13% exact), so the cinematic test needs a window. Logs `[snap7872] win lo..hi el=<n>` once and `[snap7872] hits=<n> vi=<v>`
at the first hit and every 256th. Unset = untouched (byte-identical behaviour)."""
import pathlib, sys
BASE = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
A1 = "    // 0x8000BE28: mtc1        $v0, $f2\n"
SITE = ('    { /* PATCH: s7872 snapwin */ static int w7872 = -1; static unsigned long long lo7872, hi7872; static long long el7872; '
        'static unsigned long long h7872 = 0;\n'
        '      if (w7872 < 0) { const char* e = getenv("ROGUESQ_S7872_SNAP_WIN"); w7872 = 0; '
        'if (e && *e && sscanf(e, "%llu:%llu:%lld", &lo7872, &hi7872, &el7872) == 3) { w7872 = 1; '
        'fprintf(stderr, "[snap7872] win %llu..%llu el=%lld\\n", lo7872, hi7872, el7872); } }\n'
        '      if (w7872) { extern uint64_t total_vis; if (total_vis >= lo7872 && total_vis < hi7872) { ctx->r2 = (int32_t)el7872; '
        'if ((h7872++ & 255) == 0) fprintf(stderr, "[snap7872] hits=%llu vi=%llu\\n", h7872, (unsigned long long)total_vis); } } }\n')

def apply3(text):
    if "s7872 snapwin" in text or text.count(A1) != 1 or "s7839 snaplog el" not in text:
        return text, 0
    return text.replace(A1, SITE + A1), 1

if __name__ == "__main__":
    base = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else BASE
    p = base / "funcs_3.c"
    t, n = apply3(p.read_text())
    if n: p.write_text(t)
    print(f"s7872 snapwin x{n}")
