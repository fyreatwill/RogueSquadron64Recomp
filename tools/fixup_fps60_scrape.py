#!/usr/bin/env python3
"""s6817 G3 FPS60: terrain-scrape contact response step. 0x800FEF10 (misnamed stepObjectOrientationTowardTarget) is the
craft collision resolver: up to 5 passes per tick; each pass that finds a contact takes one jump-table case
(0x800FF47C..0x800FF98C) that rotates the craft orientation by K*dt (K = 120/180 deg/s, rodata 0x800A9468..) and adds K'*dt
to the caller's angle accumulators (a2/a3), then re-sweeps with vel*dt. The per-pass step is a deflection quantum, not a
continuous force: at 30 Hz (dt 1/30) one contact tick deflects 6 deg/pass (lvl14 15.4 s: pitch -30 = 5 passes), at
ROGUESQ_FPS60 (dt 1/60) only 3 deg/pass, so the craft stays near the surface and takes 7 contact ticks (20 hp each) instead
of 2 (s6816). Under ROGUESQ_FPS60 the ten case multiplies use max(dt, 1/30); the sweep (0x800FEF78.., 0x800FF9F8..) keeps
the real dt. ROGUESQ_FPS60_SCRAPE=0 restores. Retail (no FPS60) unchanged. Idempotent.
Usage: fixup_fps60_scrape.py <RecompiledFuncs dir>"""
import pathlib, re, sys

base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "../N64Recomp/RecompiledFuncs")
TAG = "/* PATCH: s6817 fps60 scrape */"
HEAD = "RECOMP_FUNC void stepObjectOrientationTowardTarget(uint8_t* rdram, recomp_context* ctx) {\n"
HELPER = ("extern char* getenv(const char*); static float rs64_scrape_dt(float dt) { static int on = -1; if (on < 0) { "
          "const char* f = getenv(\"ROGUESQ_FPS60\"); const char* s = getenv(\"ROGUESQ_FPS60_SCRAPE\"); "
          "on = f && *f && *f != '0' && !(s && *s == '0'); } return (on && dt < (1.0f / 30.0f)) ? (1.0f / 30.0f) : dt; } "
          + TAG + "\n")
MUL = re.compile(r"(ctx->f(?:0|2|20)\.fl = MUL_S\()ctx->f24\.fl(, ctx->f(?:0|2|20)\.fl\);)")
done = 0
for p in sorted(base.glob("funcs_*.c")):
    s = p.read_text()
    if HEAD not in s:
        continue
    i = s.index(HEAD)
    j = s.index("\nRECOMP_FUNC ", i + len(HEAD)) if "\nRECOMP_FUNC " in s[i + len(HEAD):] else len(s)
    a = s.index("// 0x800FF47C:", i, j)
    b = s.index("// 0x800FF98C:", a, j)
    seg, n = MUL.subn(r"\1rs64_scrape_dt(ctx->f24.fl)\2 " + TAG, s[a:b])
    already = seg.count("rs64_scrape_dt(ctx->f24.fl)")
    if already != 10:
        sys.exit(f"s6817 fps60 scrape: expected 10 case multiplies in {p.name}, found {already}")
    s = s[:a] + seg + s[b:]
    if HELPER not in s:
        s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + HELPER, 1)
    p.write_text(s)
    done += 1
if done != 1:
    sys.exit(f"s6817 fps60 scrape: stepObjectOrientationTowardTarget found in {done} files (want 1)")
print("[s6817] fps60 scrape contact step patched (10 case multiplies)")
