#!/usr/bin/env python3
"""s7839 G3 discriminator: does timeSnapshotFiller (0x8000BC00) hand the guest a different mid-frame elapsed time in the port
than on N64 timing, at the lvl4 flight fork (s7838: rows 0-2 bit-identical, camera forks at row 3, NOT via dt word 0x8011A904)?
At 0x8000BE28 the function holds v0 = stamp 0x80128ED8 - prev 0x8011A900 (v1). Env ROGUESQ_S7839_SNAP=1 logs
`[snap7839] el=<v0> prev=<v1> s0=<a0 struct> vi=<total_vis>` there, and `[snap7839] ret f0=<hex> s0=.. vi=..` at L_8000BF38 (the
value stored to a0+0x20), `gt=` raw osGetTime delta at 0x8000BC70 and `vd=` VI-byte diff 0x80128EAF-0x80128EAE at 0x8000BE80.
(N64Recomp does not set $ra on direct calls, so the caller key is s0 = a0.) Env ROGUESQ_S7839_SNAP_EL=<n> (lever) overrides v0 with n at 0x8000BE28 (n = raw stamp units; logs
`[snap7839] pin`); ROGUESQ_S7839_SNAP_VD=<n> overrides the VI-byte diff at 0x8000BE80 (before slti).
s7840: ROGUESQ_RETAIL_SNAP=1 is shorthand for EL=811160 VD=1 (explicit levers win); pinned port = retail CPO1 rest pitch on lvl2/3/4.
Unset = untouched. Retail twin: rs64_oracle --watch-pc 0x8000BE28 prints v0/v1."""
import pathlib, sys
BASE = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
OLD_H = "pin7839 = (p && *p) ? atoll(p) : -1; "
NEW_H = "const char* rs = getenv(\"ROGUESQ_RETAIL_SNAP\"); pin7839 = (p && *p) ? atoll(p) : ((rs && *rs && *rs != '0') ? 811160 : -1); "
OLD_V = "pv7839 = (p && *p) ? atoll(p) : -1; "
NEW_V = "const char* rs = getenv(\"ROGUESQ_RETAIL_SNAP\"); pv7839 = (p && *p) ? atoll(p) : ((rs && *rs && *rs != '0') ? 1 : -1); "
# s7891: the s7891 crawl-site dump (tools/s7891_crawl_clock.sh) shows retail's 3rd crawl call (the first after the two
# prev==-1 zeros of a load) stores 1/60 (el 0) while the =1 pin stores 0.03397 -> 2 VI, putting the port's crawl clock +1 VI
# (half a frame) ahead = island A. Two variants of the =1 pin:
#   ROGUESQ_RETAIL_SNAP=2: el kept 0 on every frame whose real el is under half a VI (390625 port units). REFUTED as a det pin
#     (s7891 fix2): the port boot then runs retail's 1 VI/frame and the press schedule never reaches the mission.
#   ROGUESQ_RETAIL_SNAP=3: only the first el-path frame after a prev==-1 reset (the post-load frame, which retail times for real:
#     1, 2 or 3 VI per load) runs unpinned (real el AND real vd); every other frame keeps the =1 pin.
# =1 and unset are unchanged in behaviour (the reset hook is a host-side store only).
OLD_PIN1 = ('      extern uint64_t total_vis; if (pin7839 >= 0) { if (en7839) fprintf(stderr, "[snap7839] pin el %d->%lld\\n", (int32_t)ctx->r2, pin7839); '
            'ctx->r2 = (int32_t)pin7839; }\n')
PIN1 = ('      extern uint64_t total_vis; extern int rs64_s7891_reset, rs64_s7891_free; if (pin7839 >= 0) { /* s7891 sub-VI */ static int sub7839 = -1; static unsigned long long z7839 = 0; '
        'if (sub7839 < 0) { const char* r2 = getenv("ROGUESQ_RETAIL_SNAP"); sub7839 = (r2 && r2[0] == \'2\' && !r2[1]) ? 1 : (r2 && r2[0] == \'3\' && !r2[1]) ? 2 : 0; '
        'if (sub7839) fprintf(stderr, "[snap7891] RETAIL_SNAP=%d: %s\\n", sub7839 + 1, sub7839 == 1 ? "sub-half-VI el kept 0" : "post-reset frame unpinned"); }\n'
        '        if (en7839) fprintf(stderr, "[snap7839] pin el %d->%lld\\n", (int32_t)ctx->r2, pin7839); '
        'if (sub7839 == 1 && (int32_t)ctx->r2 >= 0 && (int32_t)ctx->r2 < 390625) { if (z7839++ < 64) fprintf(stderr, "[snap7891] el %d kept 0 vi=%llu n=%llu\\n", '
        '(int32_t)ctx->r2, (unsigned long long)total_vis, z7839); ctx->r2 = 0; } '
        'else if (sub7839 == 2 && rs64_s7891_reset) { rs64_s7891_reset = 0; rs64_s7891_free = 1; if (z7839++ < 256) fprintf(stderr, "[snap7891] post-reset el %d real vi=%llu n=%llu\\n", '
        '(int32_t)ctx->r2, (unsigned long long)total_vis, z7839); } else ctx->r2 = (int32_t)pin7839; }\n')
# s7894: ROGUESQ_SNAP3_ONLY=<n> (with RETAIL_SNAP=3) unpins ONLY post-reset fire n and forces its el to 0 (stores max(vd,1) VI,
# retail's 1 VI on the crawl), every other post-reset frame keeps the =1 pin. s7894 measured plain =3 host-timing dependent: the
# unpinned frame stores the real el (0 or 781250 = 1 VI) and the m6 crawl got 781250 in 3 of 4 runs. Unset = the s7891 =3 behaviour.
PIN1_S7891 = PIN1
PIN1 = PIN1_S7891.replace('else if (sub7839 == 2 && rs64_s7891_reset) { rs64_s7891_reset = 0; rs64_s7891_free = 1; if (z7839++ < 256) fprintf(stderr, "[snap7891] post-reset el %d real vi=%llu n=%llu\\n", '
    '(int32_t)ctx->r2, (unsigned long long)total_vis, z7839); }',
    'else if (sub7839 == 2 && rs64_s7891_reset) { static int only7894 = -1; if (only7894 < 0) { const char* o4 = getenv("ROGUESQ_SNAP3_ONLY"); only7894 = (o4 && *o4) ? atoi(o4) : 0; } '
    'rs64_s7891_reset = 0; ++z7839; if (only7894 && (int)z7839 != only7894) { if (z7839 < 256) fprintf(stderr, "[snap7894] post-reset el %d pinned vi=%llu n=%llu\\n", '
    '(int32_t)ctx->r2, (unsigned long long)total_vis, z7839); ctx->r2 = (int32_t)pin7839; } else { rs64_s7891_free = 1; if (z7839 < 256) fprintf(stderr, "[snap7891] post-reset el %d %s vi=%llu n=%llu\\n", '
    '(int32_t)ctx->r2, only7894 ? "forced 0" : "real", (unsigned long long)total_vis, z7839); if (only7894) ctx->r2 = 0; } }')
# s7895: ROGUESQ_SNAP3_ONLY=c keys the unpin on the crawl dt site instead of the fire index: a post-reset frame is unpinned (el
# forced 0) only when the most recent timeSnapshotFiller return mark (rs64_xtrace_mark, needs RAND_TRACE like every det recipe) was
# 0x800C6674 (the crawl's advanceWrappingPhaseAccumulator path, runModelViewerLoop ra 0x800C9D94). s7895: fire 6 is the crawl on m6/m11
# but on m3 (0x31=2, no chapter crawl) fire 6 is a cinematic post-load frame, and ONLY=6 lost every phase-6 match there. Numeric
# ONLY=<n> unchanged; the log lines now carry dtpc=.
PIN1_S7894 = PIN1
PIN1 = PIN1_S7894.replace('static int only7894 = -1; if (only7894 < 0) { const char* o4 = getenv("ROGUESQ_SNAP3_ONLY"); only7894 = (o4 && *o4) ? atoi(o4) : 0; } '
    'rs64_s7891_reset = 0; ++z7839; if (only7894 && (int)z7839 != only7894) { if (z7839 < 256) fprintf(stderr, "[snap7894] post-reset el %d pinned vi=%llu n=%llu\\n", '
    '(int32_t)ctx->r2, (unsigned long long)total_vis, z7839);',
    'static int only7894 = -1; extern uint32_t rs64_s7895_dtpc; if (only7894 == -1) { const char* o4 = getenv("ROGUESQ_SNAP3_ONLY"); only7894 = (o4 && *o4) ? (*o4 == \'c\' ? -2 : atoi(o4)) : 0; } '
    'rs64_s7891_reset = 0; ++z7839; int hit7895 = only7894 == -2 ? (rs64_s7895_dtpc == 0x800C6674u) : ((int)z7839 == only7894); '
    'if (only7894 && !hit7895) { if (z7839 < 256) fprintf(stderr, "[snap7894] post-reset el %d pinned vi=%llu n=%llu dtpc=%08X\\n", '
    '(int32_t)ctx->r2, (unsigned long long)total_vis, z7839, rs64_s7895_dtpc);').replace(
    'fprintf(stderr, "[snap7891] post-reset el %d %s vi=%llu n=%llu\\n", \'\n    \'(int32_t)ctx->r2, only7894 ? "forced 0" : "real", (unsigned long long)total_vis, z7839);', 'X')
PIN1 = PIN1.replace('if (z7839 < 256) fprintf(stderr, "[snap7891] post-reset el %d %s vi=%llu n=%llu\\n", (int32_t)ctx->r2, only7894 ? "forced 0" : "real", (unsigned long long)total_vis, z7839);',
    'if (z7839 < 256) fprintf(stderr, "[snap7891] post-reset el %d %s vi=%llu n=%llu dtpc=%08X\\n", (int32_t)ctx->r2, only7894 ? "forced 0" : "real", (unsigned long long)total_vis, z7839, rs64_s7895_dtpc);')
assert PIN1 != PIN1_S7894 and PIN1.count('dtpc=%08X') == 2, PIN1.count('dtpc=%08X')
# s7895 (same session, second arm): dtpc alone is not the crawl. scratch/s7895/m3k showed boot/hangar fires 1,3,4,5 also follow a
# 0x800C6674 mark (advanceWrappingPhaseAccumulator is the whole front end's dt path) and =c forced them all. The crawl is keyed by its
# timeSnapshotFiller struct a0 = s0 = 0x80165DE0 (runModelViewerLoop's callee sp+0x10); s7894/c6 rand rows give each 0x800C6674 scene
# its own struct (80165EA8 boot, 80165D80, 80165ED8, 80165EC0 hangar, 80165DE0 = the 1088 crawl calls from VI 5602).
PIN1_S7895A = PIN1
PIN1 = PIN1_S7895A.replace('(rs64_s7895_dtpc == 0x800C6674u)', '((uint32_t)ctx->r16 == 0x80165DE0u && rs64_s7895_dtpc == 0x800C6674u)')
assert PIN1 != PIN1_S7895A
assert PIN1 != PIN1_S7891
# s7898: ROGUESQ_SNAP3_ONLY takes a comma list: 'c' (the crawl struct key) plus fire numbers n (1..63), any hit forces el 0.
# s7898 measured m11's post-crawl cinematic (struct 0x80165E78, shared with the boot cinematic, so no struct key) post-load frame:
# retail stores 1.0 VI, the =1-pinned port 2.038 VI (+1 VI cumulative over all 849 later calls). A single token is unchanged.
PIN1_S7895B = PIN1
PIN1 = PIN1_S7895B.replace('only7894 = (o4 && *o4) ? (*o4 == \'c\' ? -2 : atoi(o4)) : 0; }',
    'only7894 = (o4 && *o4) ? (*o4 == \'c\' ? -2 : atoi(o4)) : 0; if (o4) for (const char* q7898 = o4; *q7898; ) { '
    'if (*q7898 == \'c\') only7894 = -2; else if (*q7898 >= \'0\' && *q7898 <= \'9\') { int v7898 = atoi(q7898); if (v7898 > 0 && v7898 < 64) fm7898 |= 1ull << v7898; '
    'while (*q7898 >= \'0\' && *q7898 <= \'9\') ++q7898; continue; } ++q7898; } }').replace(
    'static int only7894 = -1; extern uint32_t rs64_s7895_dtpc;', 'static int only7894 = -1; static unsigned long long fm7898 = 0; extern uint32_t rs64_s7895_dtpc;').replace(
    '((uint32_t)ctx->r16 == 0x80165DE0u && rs64_s7895_dtpc == 0x800C6674u) :',
    '(((uint32_t)ctx->r16 == 0x80165DE0u && rs64_s7895_dtpc == 0x800C6674u) || (z7839 < 64 && ((fm7898 >> z7839) & 1))) :')
assert PIN1.count('7898') >= 8, PIN1.count('7898')

HDR = ('static int en7839 = -1; static long long pin7839 = -1; if (en7839 < 0) { const char* e = getenv("ROGUESQ_S7839_SNAP"); '
       'en7839 = (e && *e && *e != \'0\') ? 1 : 0; const char* p = getenv("ROGUESQ_S7839_SNAP_EL"); const char* rs = getenv("ROGUESQ_RETAIL_SNAP"); pin7839 = (p && *p) ? atoll(p) : ((rs && *rs && *rs != \'0\') ? 811160 : -1); '
       'if (en7839 || pin7839 >= 0) fprintf(stderr, "[snap7839] armed log=%d pin=%lld\\n", en7839, pin7839); }\n')
SITE1 = ('    { /* PATCH: s7839 snaplog el */ ' + HDR +
         PIN1 +
         '      if (en7839) fprintf(stderr, "[snap7839] el=%d prev=%08X s0=%08X vi=%llu\\n", (int32_t)ctx->r2, (uint32_t)ctx->r3, '
         '(uint32_t)ctx->r16, (unsigned long long)total_vis); }\n')
SITE2 = ('    { /* PATCH: s7839 snaplog ret */ static int en7839b = -1; if (en7839b < 0) { const char* e = getenv("ROGUESQ_S7839_SNAP"); '
         'en7839b = (e && *e && *e != \'0\') ? 1 : 0; }\n'
         '      if (en7839b) { extern uint64_t total_vis; fprintf(stderr, "[snap7839] ret f0=%08X s0=%08X vi=%llu\\n", ctx->f0.u32l, '
         '(uint32_t)ctx->r16, (unsigned long long)total_vis); } }\n')
A1, A2 = "    // 0x8000BE28: mtc1        $v0, $f2\n", "L_8000BF38:\n"
A3, A4 = "    // 0x8000BC70: mtc1        $v0, $f4\n", "    // 0x8000BE80: slti        $v0, $v0, 0x2\n"
def site(tag, fmt):
    return ('    { /* PATCH: s7839 snaplog ' + tag + ' */ static int e7839' + tag + ' = -1; if (e7839' + tag + ' < 0) { const char* e = getenv("ROGUESQ_S7839_SNAP"); '
            'e7839' + tag + ' = (e && *e && *e != \'0\') ? 1 : 0; }\n'
            '      if (e7839' + tag + ') { extern uint64_t total_vis; fprintf(stderr, "[snap7839] ' + fmt + ' s0=%08X vi=%llu\\n", (int32_t)ctx->r2, (uint32_t)ctx->r16, '
            '(unsigned long long)total_vis); } }\n')

PINVD = ('    { /* PATCH: s7839 snaplog pinvd */ static long long pv7839 = -2; if (pv7839 == -2) { const char* p = getenv("ROGUESQ_S7839_SNAP_VD"); '
         'const char* rs = getenv("ROGUESQ_RETAIL_SNAP"); pv7839 = (p && *p) ? atoll(p) : ((rs && *rs && *rs != \'0\') ? 1 : -1); if (pv7839 >= 0) fprintf(stderr, "[snap7839] pin vd=%lld\\n", pv7839); }\n'
         '      if (pv7839 >= 0) { extern int rs64_s7891_free; if (rs64_s7891_free) rs64_s7891_free = 0; else ctx->r2 = (int32_t)pv7839; } }\n')

# s7840: ROGUESQ_RETAIL_SNAP=1 = the retail-typical pin (el 811160, vd 1) without spelling both levers; upgrade older patched trees.
PINVD_S7840 = PINVD.replace("      if (pv7839 >= 0) { extern int rs64_s7891_free; if (rs64_s7891_free) rs64_s7891_free = 0; else ctx->r2 = (int32_t)pv7839; } }\n",
                            "      if (pv7839 >= 0) ctx->r2 = (int32_t)pv7839; }\n")
OLD_HDR = HDR.replace(NEW_H, OLD_H); OLD_PINVD = PINVD_S7840.replace(NEW_V, OLD_V)
# s7891: the prev==-1 path (0x8000BE10, value 0, no el) and the flags-clear path (L_8000BEE8, value = dt word 0x8011A904 / rate,
# 0 right after a load: the two zeros that open every post-load segment) arm RETAIL_SNAP=3's one unpinned post-reset frame.
# Guest-neutral host stores.
A5 = "    // 0x8000BE10: mtc1        $zero, $f0\n"
A6 = "L_8000BEE8:\n"
# s7892: arm only before the first mission tick (rs64_s7858_tick, counted at the 0x800FA730 XTRACE mark the det recipes always
# arm). Ungated, m6 (0x31=5) fired an 8th reset at port VI 13415 = mission tick ~8 and forked the det pair there (s7892).
OLD_RESET = "    { /* PATCH: s7891 snap reset */ extern int rs64_s7891_reset; rs64_s7891_reset = 1; }\n"
RESET = "    { /* PATCH: s7891 snap reset */ extern int rs64_s7891_reset; extern volatile uint32_t rs64_s7858_tick; /* s7892 pre-flight only */ if (!rs64_s7858_tick) rs64_s7891_reset = 1; }\n"

def apply3(text):
    n = 0
    for o, nw in ((OLD_HDR, HDR), (OLD_PINVD, PINVD), (PINVD_S7840, PINVD), (OLD_PIN1, PIN1), (PIN1_S7891, PIN1), (PIN1_S7894, PIN1), (PIN1_S7895A, PIN1), (PIN1_S7895B, PIN1), (OLD_RESET, RESET),
                  (OLD_RESET.replace("snap reset", "snap reset2"), RESET.replace("snap reset", "snap reset2"))):
        if o in text:
            text = text.replace(o, nw); n += 1
    if "s7839 snaplog el" not in text and text.count(A1) == 1:
        text = text.replace(A1, SITE1 + A1); n += 1
    if "s7839 snaplog ret" not in text and text.count(A2) == 1:
        j = text.find(A2) + len(A2); text = text[:j] + SITE2 + text[j:]; n += 1
    if "s7891 snap reset" not in text and text.count(A5) == 1:
        text = text.replace(A5, RESET + A5); n += 1
    if "s7891 snap reset2" not in text and text.count(A6) == 1:
        text = text.replace(A6, A6 + RESET.replace("snap reset", "snap reset2")); n += 1
    for tag, fmt, a in (("gt", "gt=%d", A3), ("vd", "vd=%d", A4)):
        if ("s7839 snaplog " + tag) not in text and text.count(a) == 1:
            text = text.replace(a, site(tag, fmt) + (PINVD if tag == "vd" else "") + a); n += 1
    return text, n

if __name__ == "__main__":
    base = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else BASE
    p = base / "funcs_3.c"
    t, n = apply3(p.read_text())
    if n:
        p.write_text(t)
    print(f"funcs_3.c s7839 snaplog x{n}")
