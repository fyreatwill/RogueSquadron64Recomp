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

# s6819: contact DAMAGE. updatePlayerCraftPhysics (0x800B2918..0x800B29F8) takes rodata 0x800A5734 (20 hp) from +0xC0 on
# every tick 0x800FEF10 returns 1. The only gates are two flag tests (0x80130B4C & 0x800000, player +0x184 & 0x78); no
# tick counter, and the s6816/s6817 traces show hits on consecutive FPS60 ticks (15.600/15.617). So the damage is a
# per-tick quantum: a sustained contact costs 2x per real second at FPS60. Under ROGUESQ_FPS60 the subtrahend is scaled by
# dt*30 (dt = arg a1 spilled at sp+0x1DC); ROGUESQ_FPS60_SCRAPE_DMG=0 (or ROGUESQ_FPS60_SCRAPE=0) restores. Retail unchanged.
TAG2 = "/* PATCH: s6819 fps60 scrape dmg */"
HEAD2 = "RECOMP_FUNC void updatePlayerCraftPhysics(uint8_t* rdram, recomp_context* ctx) {\n"
HELPER2 = ("extern char* getenv(const char*); static float rs64_scrape_dmg_scale(float dt) { static int on = -1; if (on < 0) { "
           "const char* f = getenv(\"ROGUESQ_FPS60\"); const char* s = getenv(\"ROGUESQ_FPS60_SCRAPE\"); "
           "const char* d = getenv(\"ROGUESQ_FPS60_SCRAPE_DMG\"); "
           "on = f && *f && *f != '0' && !(s && *s == '0') && !(d && *d == '0'); } "
           "return (on && dt > 0.0f && dt < (1.0f / 30.0f)) ? dt * 30.0f : 1.0f; } " + TAG2 + "\n")
SITE2 = "    // 0x800B29D4: lwc1        $f0, 0x5734($at)\n    ctx->f0.u32l = MEM_W(ctx->r1, 0X5734);\n"
NEW2 = SITE2 + ("    { union { uint32_t u; float f; } rs64_dt; rs64_dt.u = MEM_W(ctx->r29, 0X1DC); "
                "ctx->f0.fl *= rs64_scrape_dmg_scale(rs64_dt.f); } " + TAG2 + "\n")
done = 0
for p in sorted(base.glob("funcs_*.c")):
    s = p.read_text()
    if HEAD2 not in s:
        continue
    if TAG2 not in s:
        if s.count(SITE2) != 1:
            sys.exit(f"s6819 fps60 scrape dmg: expected 1 site 0x800B29D4 in {p.name}, found {s.count(SITE2)}")
        s = s.replace(SITE2, NEW2, 1)
        s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + HELPER2, 1)
        p.write_text(s)
    done += 1
if done != 1:
    sys.exit(f"s6819 fps60 scrape dmg: updatePlayerCraftPhysics found in {done} files (want 1)")
print("[s6819] fps60 scrape contact damage patched (dt*30 under FPS60)")
