#!/usr/bin/env python3
"""s7134 G3 21:9 sky-side corner holes: widen the game's sphere-vs-view-frustum test x-extent under ASPECT.

ORIGIN (code read, s7134): the remaining 21:9 holes (s7133 F1 swaps 7524-7541, bottom-left at ~150 deg roll) sit where the
cloud layer's tiles are missing. The cloud layer (0x8005A4B4, generated name updateWalkerParticlePositions; loadTopCloudsAsset
builds it) draws a 4x4 tile grid per layer and skips every tile whose centre fails transformVec3ToNpcLocalWithScale
(0x8001DC34, a0 = camera, a3 = radius 30.0), at 0x8005A9C0. That function is the game's general sphere-in-view test (19 call
sites). Its screen-x half-extent is E = (cam+0x10 / cam+0x14) * (0x8011A844 / 0x8011A838) * 0x8011A840 (0x8001DEAC, radius path;
0x8001E168, point path), the same product setupCameraMatrices hands guPerspective as the aspect. Under ROGUESQ_ASPECT the s6104
patch multiplies only the guPerspective aspect by k (ASPECT_SCALE, with the s6718/s6719/s6927 state rules), so the test keeps a
4:3 x-extent: anything whose bounding sphere lies wholly outside the central 4:3 width is culled although it is on screen.
The drawn cloud tiles' edge is a cell staircase (tools/s7134_band.py, swap 7541), not a smooth ring: per-tile culling (H-skycull).

Fix: setupCameraMatrices records, per camera struct (s1/r17), the factor s6104 actually applied (new aspect / old aspect,
1.0 when ASPECT is off); the test multiplies E by that factor. 4:3 / retail: factor 1.0, no-op.
  Scope: only the render callers in SITES (cloud tiles 0x8005A9B8, addNpcToVisibilityBucket x3, selectMeshLodAndSubmitForRender);
  the other 14 sites include game logic (isPointInsideTriggerVolume, cutsceneDispatchSlotsByFlag, advanceNpcOnCurvedPath, effect
  spawners that draw rand) and keep the retail 4:3 extent, so mission scripting does not change with the window shape.
  ROGUESQ_CULL_XFIX: OPT-IN, default off = retail (s7134: no hole change, see below); =1 widens the render sites; =tog applies it in odd mach seconds (mach/24e6 & 1) for
  same-run A/B; =all widens all 19 sites.
  [s7134] stderr line once per mach second while a factor != 1 exists: mode, on, all calls/passes, cloud-caller calls/passes (flag set at the 0x8005A9B8 call: recompiled jal does not set $ra).
s7134 RESULT: L6 21:9 owner recipe, fix on (F3), all 19 sites (A1) and off (Z1) all show the sky-corner burst (max 27-31k px), with the
same-run no-clear pose marker after it, so this test is NOT what leaves those holes (H-skycull via 0x8001DC34 refuted). Same-run tog (T1, 253 s
alternating seconds): pass rate 0.259 on vs 0.236 off (single-source). Kept as an opt-in for side-edge object pop-in checks.
Idempotent; listed in fixup_game_funcs_vendored.py before apply_s7069_callsite_gate.py."""
import pathlib, sys
BASE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s7134 cull x"

HELP = r'''/* PATCH: s7134 cull x helpers */
#include <string.h>
extern uint64_t mach_absolute_time(void);
static uint32_t s7134_cam[16]; static float s7134_k[16]; static int s7134_n; static uint32_t s7134_old; static int s7134_md = -1;
static unsigned long long s7134_sec; static unsigned s7134_c[2][4]; int rs64_s7134_cloud;
void rs64_s7134_pre(uint32_t a) { s7134_old = a; }
void rs64_s7134_post(uint32_t cam, uint32_t a) {
    float o, n, k; int i; memcpy(&o, &s7134_old, 4); memcpy(&n, &a, 4); k = (o != 0.0f) ? n / o : 1.0f; if (!(k > 0.0f)) k = 1.0f;
    for (i = 0; i < s7134_n; i++) if (s7134_cam[i] == cam) { s7134_k[i] = k; return; }
    if (s7134_n < 16) { s7134_cam[s7134_n] = cam; s7134_k[s7134_n] = k; s7134_n++; fprintf(stderr, "[s7134] cam %08x k %g\n", (unsigned)cam, (double)k); } }
static int s7134_on(void) {
    if (s7134_md < 0) { const char* e = getenv("ROGUESQ_CULL_XFIX"); s7134_md = !(e && *e) || *e == '0' ? 0 : !strcmp(e, "tog") ? 2 : !strcmp(e, "all") ? 3 : 1; }
    return s7134_md == 1 || s7134_md == 3 || (s7134_md == 2 && ((mach_absolute_time() / 24000000ull) & 1)); }
static float s7134_kof(uint32_t cam) { int i; for (i = 0; i < s7134_n; i++) if (s7134_cam[i] == cam) return s7134_k[i]; return 1.0f; }
float rs64_s7134_x(uint32_t cam, float e) { float k = s7134_kof(cam); return (k != 1.0f && (rs64_s7134_cloud || s7134_md == 3) && s7134_on()) ? e * k : e; }
void rs64_s7134_ret(uint32_t ra, uint32_t cam, int v) {
    float k = s7134_kof(cam); unsigned long long s; int on; if (s7134_md < 0) (void)s7134_on(); if (k == 1.0f || !s7134_md) { rs64_s7134_cloud = 0; return; }
    s = mach_absolute_time() / 24000000ull; on = s7134_on();
    if (s != s7134_sec) { if (s7134_sec) fprintf(stderr, "[s7134] sec %llu md %d off all %u/%u cloud %u/%u on all %u/%u cloud %u/%u\n", s7134_sec, s7134_md,
            s7134_c[0][1], s7134_c[0][0], s7134_c[0][3], s7134_c[0][2], s7134_c[1][1], s7134_c[1][0], s7134_c[1][3], s7134_c[1][2]);
        memset(s7134_c, 0, sizeof s7134_c); s7134_sec = s; }
    s7134_c[on][0]++; if (v) s7134_c[on][1]++; if (rs64_s7134_cloud == 2) { s7134_c[on][2]++; if (v) s7134_c[on][3]++; } rs64_s7134_cloud = 0; }
'''

def patch_test(T):
    f = "RECOMP_FUNC void transformVec3ToNpcLocalWithScale("
    i = T.index(f); assert T.count(f) == 1
    T = T[:i] + HELP + T[i:]
    i = T.index(f)
    end = T.index("\nRECOMP_FUNC", i + 10)
    body = T[i:end]
    MUL = "    ctx->f0.fl = MUL_S(ctx->f0.fl, ctx->f2.fl);\n"
    for pc in ("0x8001DEAC", "0x8001E168"):
        a = body.index("    // %s: mul.s       $f0, $f0, $f2\n" % pc)
        j = body.index(MUL, a); assert j - a < 400
        add = "    ctx->f0.fl = rs64_s7134_x(U32(ctx->r17), ctx->f0.fl); /* %s */\n" % MARK
        body = body[:j + len(MUL)] + add + body[j + len(MUL):]
    L = body.index("L_8001E1E8:")
    a = body.index("    // 0x8001E1E8: lw          $ra, 0x3C($sp)\n", L)
    body = body[:a] + "    rs64_s7134_ret(U32(MEM_W(ctx->r29, 0X3C)), U32(ctx->r17), (int)ctx->r2); /* %s */\n" % MARK + body[a:]
    return T[:i] + body + T[end:]

def patch_cam(T):
    S = "    { /* PATCH: s6104 aspect */"
    i = T.index(S); assert T.count(S) == 1
    e = T.index("\n", T.index("\n", i) + 1) + 1  # the s6104 block is two lines
    assert T[e - 4:e] == "} }\n", repr(T[e - 20:e])
    T = T[:e] + "    { extern void rs64_s7134_post(uint32_t, uint32_t); rs64_s7134_post(U32(ctx->r17), (uint32_t)ctx->r7); } /* %s */\n" % MARK + T[e:]
    return T[:i] + "    { extern void rs64_s7134_pre(uint32_t); rs64_s7134_pre((uint32_t)ctx->r7); } /* %s */\n" % MARK + T[i:]

SITES = {"updateWalkerParticlePositions": 2, "addNpcToVisibilityBucket": 1, "selectMeshLodAndSubmitForRender": 1}  # render-only callers
SMARK = "PATCH: s7134 site"
def patch_sites(T):
    n = 0
    for fn, sid in SITES.items():
        h = "RECOMP_FUNC void %s(" % fn
        if h not in T: continue
        i = T.index(h); end = T.find("\nRECOMP_FUNC", i + 10); end = len(T) if end < 0 else end
        c = "    transformVec3ToNpcLocalWithScale(rdram, ctx);\n"
        body = T[i:end].replace(c, "    { extern int rs64_s7134_cloud; rs64_s7134_cloud = %d; } /* %s */\n" % (sid, SMARK) + c)
        n += body.count(SMARK); T = T[:i] + body + T[end:]
    return T, n

done = 0
for name, fn, key in (("funcs_6.c", patch_test, "RECOMP_FUNC void transformVec3ToNpcLocalWithScale("),
                      ("funcs_4.c", patch_cam, "PATCH: s6104 aspect")):
    P = BASE / name
    T = P.read_text()
    if MARK in T: print("s7134 already applied to", name); continue
    if key not in T:  # regen may move functions between files
        cands = [p for p in BASE.glob("funcs_*.c") if key in p.read_text()]
        assert len(cands) == 1, (key, cands); P = cands[0]; T = P.read_text()
        if MARK in T: print("s7134 already applied to", P.name); continue
    P.write_text(fn(T)); done += 1; print("s7134 applied to", P.name)
tot = 0
for P in sorted(BASE.glob("funcs_*.c")):
    T = P.read_text()
    if SMARK in T or not any("RECOMP_FUNC void %s(" % f in T for f in SITES): tot += T.count(SMARK); continue
    T, n = patch_sites(T); P.write_text(T); tot += n; print("s7134 sites", P.name, n)
assert tot == 5, tot  # 1 cloud + 3 visibility bucket + 1 LOD submit
