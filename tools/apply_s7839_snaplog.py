#!/usr/bin/env python3
"""s7839 G3 discriminator: does timeSnapshotFiller (0x8000BC00) hand the guest a different mid-frame elapsed time in the port
than on N64 timing, at the lvl4 flight fork (s7838: rows 0-2 bit-identical, camera forks at row 3, NOT via dt word 0x8011A904)?
At 0x8000BE28 the function holds v0 = stamp 0x80128ED8 - prev 0x8011A900 (v1). Env ROGUESQ_S7839_SNAP=1 logs
`[snap7839] el=<v0> prev=<v1> s0=<a0 struct> vi=<total_vis>` there, and `[snap7839] ret f0=<hex> s0=.. vi=..` at L_8000BF38 (the
value stored to a0+0x20), `gt=` raw osGetTime delta at 0x8000BC70 and `vd=` VI-byte diff 0x80128EAF-0x80128EAE at 0x8000BE80.
(N64Recomp does not set $ra on direct calls, so the caller key is s0 = a0.) Env ROGUESQ_S7839_SNAP_EL=<n> (lever) overrides v0 with n at 0x8000BE28 (n = raw stamp units; logs
`[snap7839] pin`); ROGUESQ_S7839_SNAP_VD=<n> overrides the VI-byte diff at 0x8000BE80 (before slti).
Unset = untouched. Retail twin: rs64_oracle --watch-pc 0x8000BE28 prints v0/v1."""
import pathlib, sys
BASE = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
HDR = ('static int en7839 = -1; static long long pin7839 = -1; if (en7839 < 0) { const char* e = getenv("ROGUESQ_S7839_SNAP"); '
       'en7839 = (e && *e && *e != \'0\') ? 1 : 0; const char* p = getenv("ROGUESQ_S7839_SNAP_EL"); pin7839 = (p && *p) ? atoll(p) : -1; '
       'if (en7839 || pin7839 >= 0) fprintf(stderr, "[snap7839] armed log=%d pin=%lld\\n", en7839, pin7839); }\n')
SITE1 = ('    { /* PATCH: s7839 snaplog el */ ' + HDR +
         '      extern uint64_t total_vis; if (pin7839 >= 0) { if (en7839) fprintf(stderr, "[snap7839] pin el %d->%lld\\n", (int32_t)ctx->r2, pin7839); ctx->r2 = (int32_t)pin7839; }\n'
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
         'pv7839 = (p && *p) ? atoll(p) : -1; if (pv7839 >= 0) fprintf(stderr, "[snap7839] pin vd=%lld\\n", pv7839); }\n'
         '      if (pv7839 >= 0) ctx->r2 = (int32_t)pv7839; }\n')

def apply3(text):
    n = 0
    if "s7839 snaplog el" not in text and text.count(A1) == 1:
        text = text.replace(A1, SITE1 + A1); n += 1
    if "s7839 snaplog ret" not in text and text.count(A2) == 1:
        j = text.find(A2) + len(A2); text = text[:j] + SITE2 + text[j:]; n += 1
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
